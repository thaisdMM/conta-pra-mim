import pytest
from pydantic import ValidationError

from desafio.venda import Campo, Venda


def test_campo_escrito_guarda_valor_origem_e_motivo() -> None:
    """Um campo escrito guarda o valor, a origem e o motivo."""
    campo = Campo(valor="pix", origem="escrito", motivo="Estava na coluna.")

    assert (campo.valor, campo.origem, campo.motivo) == (
        "pix",
        "escrito",
        "Estava na coluna.",
    )


def test_campo_que_falta_recusa_valor() -> None:
    """Um campo com origem "falta" não pode trazer valor."""
    with pytest.raises(ValidationError):
        Campo(valor="Ana", origem="falta", motivo="Não anotado.")


def test_campo_com_valor_recusa_valor_vazio() -> None:
    """Um campo escrito ou deduzido precisa trazer valor."""
    with pytest.raises(ValidationError):
        Campo(valor=None, origem="deduzido", motivo="Pelas vizinhas.")


def test_campo_recusa_origem_desconhecida() -> None:
    """A origem só aceita escrito, deduzido ou falta."""
    with pytest.raises(ValidationError):
        Campo.model_validate(
            {"valor": "pix", "origem": "chute", "motivo": "Sem motivo."}
        )


def test_venda_recusa_frete_deduzido() -> None:
    """O frete nunca é deduzido: um frete deduzido é recusado."""
    escrito = {"valor": "x", "origem": "escrito", "motivo": "Estava escrito."}
    campos = dict.fromkeys(Venda.model_fields, escrito)
    campos["frete"] = {"valor": "0,00", "origem": "deduzido", "motivo": "Na loja."}

    with pytest.raises(ValidationError):
        Venda.model_validate(campos)
