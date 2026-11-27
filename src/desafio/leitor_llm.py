"""Organiza um lançamento da planilha com o Gemini, validando a resposta."""

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

import httpx2
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from desafio.venda import Venda

LIMITE_MILISSEGUNDOS = 30_000

INSTRUCOES = """\
Você organiza lançamentos de vendas de uma loja de acessórios. A dona escreve
cada venda numa planilha, cada dia de um jeito, com erros e campos vazios.
Devolva a venda do lançamento principal no esquema JSON pedido.

Para cada campo, diga a origem e o motivo numa frase simples:
- escrito: o valor está claro na própria coluna do campo e só mudou de formato;
- deduzido: o valor não está na coluna do campo; saiu de outra coluna ou das
  linhas vizinhas. Diga de onde;
- falta: não dá para saber; o valor fica null.

A coluna de cada campo na planilha: data = "data", produto = "oq vendeu",
cliente = "pra quem", valor_produto = "valor", pagamento = "como pagou",
cartao = "cartao", parcelas = "vezes", entrega = "entrega ou loja",
rastreio = "rastreio", observacao = "obs".

Exemplo: a coluna "como pagou" tem "credito 3x visa", e as colunas "cartao" e
"vezes" estão vazias.
- Valor escrito: pagamento "credito", escrito, porque está na coluna
  "como pagou".
- Valores deduzidos: parcelas "3", deduzido, e cartao "visa", deduzido, porque
  saíram da coluna "como pagou".
Os dois últimos são deduzidos porque não estão nas suas próprias colunas.
Nunca invente. Se não dá para saber, a origem é falta.

Formatos:
- datas sempre no formato brasileiro DD/MM/AAAA, por exemplo 16/08/2026,
  nunca 2026-08-16;
- valores sempre em reais, com vírgula e duas casas decimais, sem "R$",
  por exemplo 25,00 e 120,00;
- frete só quando estiver escrito no lançamento, por exemplo "35+12 frete";
  sem frete escrito, o frete é falta. Nunca deduza o frete e nunca use 0,00;
- entrega "presencial" é o mesmo que "loja": devolva "loja".
As linhas vizinhas servem só de contexto, por exemplo para deduzir uma data.
"""


class ErroLeituraLLM(Exception):
    """O LLM não devolveu uma venda para o lançamento."""

    motivo = "O LLM não devolveu uma venda."


class LLMSemResposta(ErroLeituraLLM):
    """O Gemini não respondeu: limite de tempo, erro da API ou resposta vazia."""

    motivo = "O Gemini não respondeu a tempo ou respondeu com erro."


class ChaveOuPedidoInvalido(ErroLeituraLLM):
    """O Gemini recusou o pedido: chave errada, modelo inexistente ou pedido mal feito."""

    motivo = "O Gemini recusou o pedido: confira a chave e o modelo no .env."


class RespostaForaDoFormato(ErroLeituraLLM):
    """O Gemini respondeu, mas fora do formato da venda."""

    motivo = "O Gemini respondeu fora do formato da venda."


class GeradorDeResposta(Protocol):
    """Recebe o pedido e o esquema JSON e devolve o texto do LLM."""

    def __call__(self, pedido: str, esquema: dict[str, Any]) -> str: ...


def montar_pedido(
    lancamento: Mapping[str, str], vizinhas: Sequence[Mapping[str, str]]
) -> str:
    """Monta o texto enviado ao LLM com o lançamento e as linhas vizinhas.

    Args:
        lancamento: As colunas da linha, com o cabeçalho da planilha como chave.
        vizinhas: As linhas próximas, no mesmo formato, para contexto.

    Returns:
        O pedido em texto.
    """
    principal = json.dumps(lancamento, ensure_ascii=False)
    contexto = "\n".join(json.dumps(linha, ensure_ascii=False) for linha in vizinhas)
    return (
        f"{INSTRUCOES}\nLançamento principal:\n{principal}\n\n"
        f"Linhas vizinhas:\n{contexto or '(nenhuma)'}\n"
    )


def organizar_lancamento(
    lancamento: Mapping[str, str],
    gerar: GeradorDeResposta,
    vizinhas: Sequence[Mapping[str, str]] = (),
) -> Venda:
    """Manda um lançamento ao LLM e valida a venda devolvida.

    Args:
        lancamento: As colunas da linha, com o cabeçalho da planilha como chave.
        gerar: A função que chama o LLM.
        vizinhas: As linhas próximas, para contexto.

    Returns:
        A venda organizada, com a origem e o motivo de cada campo.

    Raises:
        LLMSemResposta: Se o LLM não respondeu.
        RespostaForaDoFormato: Se a resposta não é uma venda válida.
    """
    texto = gerar(montar_pedido(lancamento, vizinhas), Venda.model_json_schema())
    try:
        return Venda.model_validate_json(texto)
    except ValidationError as erro:
        raise RespostaForaDoFormato from erro


def criar_cliente_gemini(chave: str | None = None) -> genai.Client:
    """Cria o cliente do Gemini com o limite de tempo.

    Args:
        chave: A chave da API; sem ela, o cliente lê GEMINI_API_KEY do ambiente.

    Returns:
        O cliente pronto para chamar o Gemini.
    """
    return genai.Client(
        api_key=chave,
        http_options=types.HttpOptions(timeout=LIMITE_MILISSEGUNDOS),
    )


def criar_gerador_gemini(cliente: genai.Client, modelo: str) -> GeradorDeResposta:
    """Cria a função que chama o Gemini pedindo JSON no esquema recebido.

    Args:
        cliente: O cliente do Gemini.
        modelo: O nome do modelo, lido de GEMINI_MODELO no .env.

    Returns:
        A função que recebe o pedido e o esquema e devolve o texto.
    """

    def gerar(pedido: str, esquema: dict[str, Any]) -> str:
        """Chama o Gemini e devolve o texto da resposta.

        Args:
            pedido: O texto enviado ao Gemini.
            esquema: O esquema JSON que a resposta precisa seguir.

        Returns:
            O texto da resposta, em JSON.

        Raises:
            ChaveOuPedidoInvalido: Se o Gemini recusou a chave, o modelo ou o pedido.
            LLMSemResposta: Se passou do limite, o Gemini deu erro ou veio vazio.
        """
        configuracao = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=esquema,
            temperature=0,
        )
        try:
            resposta = cliente.models.generate_content(
                model=modelo, contents=pedido, config=configuracao
            )
        except errors.ClientError as erro:
            raise ChaveOuPedidoInvalido from erro
        except (errors.APIError, httpx2.HTTPError) as erro:
            raise LLMSemResposta from erro
        if not resposta.text:
            raise LLMSemResposta
        return resposta.text

    return gerar


def mostrar_venda(venda: Venda) -> None:
    """Mostra cada campo da venda com o valor, a origem e o motivo.

    Args:
        venda: A venda organizada.
    """
    for nome, campo in venda:
        print(f"{nome}: {campo.valor or '-'} ({campo.origem}: {campo.motivo})")


def main() -> None:
    """Organiza com o Gemini real a linha 21 da planilha da Maria."""
    load_dotenv(".env")
    modelo = os.environ.get("GEMINI_MODELO")
    if not modelo:
        print("Falta GEMINI_MODELO no .env.")
        return
    lancamento = {
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
    vizinhas = [
        {"data": "2026-08-16", "oq vendeu": "pulseira", "pra quem": "a do predio"},
        {"data": "17/08/2026", "oq vendeu": "tiara", "pra quem": "menina do insta"},
    ]
    gerador = criar_gerador_gemini(criar_cliente_gemini(), modelo)
    try:
        venda = organizar_lancamento(lancamento, gerador, vizinhas)
    except ErroLeituraLLM as erro:
        print(f"Não deu para organizar: {erro.motivo}")
        return
    mostrar_venda(venda)


if __name__ == "__main__":
    main()
