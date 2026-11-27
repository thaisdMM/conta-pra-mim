import json
import os
from types import SimpleNamespace
from typing import Any, cast

import httpx2
import pytest
from dotenv import load_dotenv
from google import genai
from google.genai import errors

from desafio.leitor_llm import (
    ChaveOuPedidoInvalido,
    LLMSemResposta,
    RespostaForaDoFormato,
    criar_cliente_gemini,
    criar_gerador_gemini,
    organizar_lancamento,
)
from desafio.venda import Venda

LANCAMENTO = {
    "data": "8/16/26",
    "oq vendeu": "anel",
    "pra quem": "tia da Ana",
    "valor": "25",
    "como pagou": "credito 3x visa",
    "cartao": "",
    "vezes": "",
    "entrega ou loja": "presencial",
    "rastreio": "",
    "obs": "",
}

VIZINHA = {**LANCAMENTO, "data": "2026-08-16", "pra quem": "a do predio"}


def campo(valor: str | None, origem: str = "escrito") -> dict[str, Any]:
    """Monta um campo no formato que o LLM devolve."""
    return {"valor": valor, "origem": origem, "motivo": "Estava no lançamento."}


def resposta_valida() -> dict[str, Any]:
    """Monta a resposta do LLM para o lançamento de exemplo."""
    return {
        "e_venda": campo("sim"),
        "data": campo("16/08/2026"),
        "produto": campo("anel"),
        "cliente": campo("tia da Ana"),
        "valor_produto": campo("25,00"),
        "frete": campo(None, "falta"),
        "pagamento": campo("credito"),
        "cartao": campo("visa", "deduzido"),
        "parcelas": campo("3", "deduzido"),
        "entrega": campo("loja"),
        "rastreio": campo(None, "falta"),
        "observacao": campo(None, "falta"),
    }


class GeradorFalso:
    """LLM falso: guarda o pedido e o esquema e devolve um texto fixo."""

    def __init__(self, texto: str) -> None:
        self.texto = texto
        self.pedido = ""
        self.esquema: dict[str, Any] = {}

    def __call__(self, pedido: str, esquema: dict[str, Any]) -> str:
        self.pedido = pedido
        self.esquema = esquema
        return self.texto


class ModelosFalsos:
    """Imita cliente.models: devolve uma resposta ou levanta um erro."""

    def __init__(self, resultado: object) -> None:
        self.resultado = resultado
        self.chamadas: list[dict[str, Any]] = []

    def generate_content(self, **argumentos: Any) -> object:
        self.chamadas.append(argumentos)
        if isinstance(self.resultado, Exception):
            raise self.resultado
        return self.resultado


def cliente_falso(resultado: object) -> tuple[genai.Client, ModelosFalsos]:
    """Monta um cliente do Gemini falso com os modelos falsos."""
    modelos = ModelosFalsos(resultado)
    return cast(genai.Client, SimpleNamespace(models=modelos)), modelos


def test_organizar_lancamento_devolve_venda_validada() -> None:
    """A resposta do LLM vira uma Venda com valor, origem e motivo."""
    gerador = GeradorFalso(json.dumps(resposta_valida()))

    venda = organizar_lancamento(LANCAMENTO, gerador)

    assert (venda.parcelas.valor, venda.parcelas.origem) == ("3", "deduzido")


def test_pedido_leva_o_lancamento() -> None:
    """O pedido ao LLM traz o texto que a dona escreveu."""
    gerador = GeradorFalso(json.dumps(resposta_valida()))

    organizar_lancamento(LANCAMENTO, gerador)

    assert "credito 3x visa" in gerador.pedido


def test_pedido_leva_as_linhas_vizinhas() -> None:
    """O pedido ao LLM traz as linhas vizinhas como contexto."""
    gerador = GeradorFalso(json.dumps(resposta_valida()))

    organizar_lancamento(LANCAMENTO, gerador, vizinhas=[VIZINHA])

    assert "a do predio" in gerador.pedido


def test_esquema_enviado_e_o_da_venda() -> None:
    """O LLM recebe o esquema JSON do modelo Venda."""
    gerador = GeradorFalso(json.dumps(resposta_valida()))

    organizar_lancamento(LANCAMENTO, gerador)

    assert gerador.esquema == Venda.model_json_schema()


def test_resposta_que_nao_e_json_levanta_erro() -> None:
    """Um texto que não é JSON vira RespostaForaDoFormato."""
    with pytest.raises(RespostaForaDoFormato):
        organizar_lancamento(LANCAMENTO, GeradorFalso("não sei"))


def test_resposta_sem_um_campo_levanta_erro() -> None:
    """Um JSON sem um dos campos da venda vira RespostaForaDoFormato."""
    resposta = resposta_valida()
    del resposta["pagamento"]

    with pytest.raises(RespostaForaDoFormato):
        organizar_lancamento(LANCAMENTO, GeradorFalso(json.dumps(resposta)))


def test_gerador_gemini_pede_json_no_esquema() -> None:
    """O gerador pede ao Gemini uma resposta JSON no esquema recebido."""
    cliente, modelos = cliente_falso(SimpleNamespace(text="{}"))

    criar_gerador_gemini(cliente, "modelo-teste")("pedido", {"type": "object"})

    configuracao = modelos.chamadas[0]["config"]
    assert (
        configuracao.response_mime_type,
        configuracao.response_json_schema,
    ) == ("application/json", {"type": "object"})


def test_gerador_gemini_pede_temperatura_zero() -> None:
    """O gerador pede temperatura zero, para as respostas variarem menos."""
    cliente, modelos = cliente_falso(SimpleNamespace(text="{}"))

    criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})

    assert modelos.chamadas[0]["config"].temperature == 0


def test_gerador_gemini_devolve_o_texto_da_resposta() -> None:
    """O gerador devolve o texto que o Gemini respondeu."""
    cliente, _ = cliente_falso(SimpleNamespace(text='{"ok": true}'))

    texto = criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})

    assert texto == '{"ok": true}'


def test_gerador_gemini_transforma_limite_de_tempo_em_erro() -> None:
    """Passar do limite de tempo vira LLMSemResposta."""
    cliente, _ = cliente_falso(httpx2.TimeoutException("demorou"))

    with pytest.raises(LLMSemResposta):
        criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})


def test_gerador_gemini_transforma_pedido_recusado_em_erro() -> None:
    """Uma chave ou um modelo recusado pelo Gemini vira ChaveOuPedidoInvalido."""
    cliente, _ = cliente_falso(errors.ClientError(400, {"error": {}}))

    with pytest.raises(ChaveOuPedidoInvalido):
        criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})


def test_gerador_gemini_transforma_erro_do_servidor_em_erro() -> None:
    """Um erro do servidor do Gemini vira LLMSemResposta."""
    cliente, _ = cliente_falso(errors.ServerError(503, {"error": {}}))

    with pytest.raises(LLMSemResposta):
        criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})


def test_gerador_gemini_transforma_resposta_vazia_em_erro() -> None:
    """Uma resposta sem texto vira LLMSemResposta."""
    cliente, _ = cliente_falso(SimpleNamespace(text=None))

    with pytest.raises(LLMSemResposta):
        criar_gerador_gemini(cliente, "modelo-teste")("pedido", {})


@pytest.mark.integracao
def test_gemini_real_deduz_parcelas_do_pagamento() -> None:
    """O Gemini real tira as 3 parcelas de "credito 3x visa", como deduzidas."""
    load_dotenv(".env")
    chave = os.environ.get("GEMINI_API_KEY")
    modelo = os.environ.get("GEMINI_MODELO")
    if not chave or not modelo:
        pytest.skip("Sem GEMINI_API_KEY ou GEMINI_MODELO no .env.")
    gerador = criar_gerador_gemini(criar_cliente_gemini(chave), modelo)

    venda = organizar_lancamento(LANCAMENTO, gerador, vizinhas=[VIZINHA])

    assert (venda.parcelas.valor, venda.parcelas.origem) == ("3", "deduzido"), (
        venda.model_dump_json(indent=2)
    )
