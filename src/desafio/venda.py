"""Modelo da venda organizada a partir de um lançamento da planilha."""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

Origem = Literal["escrito", "deduzido", "falta"]


class Campo(BaseModel):
    """Um campo da venda, com o valor, de onde ele veio e o motivo.

    Attributes:
        valor: O valor em texto, ou None quando falta.
        origem: "escrito" (estava claro no lançamento), "deduzido" (preenchido a
            partir de outras informações) ou "falta" (não dá para saber).
        motivo: Uma frase simples dizendo de onde veio o valor.
    """

    valor: str | None = Field(
        description="Valor em texto; null quando a origem é falta."
    )
    origem: Origem = Field(
        description=(
            "escrito: estava claro na própria coluna do campo e só mudou de "
            "formato; "
            "deduzido: não estava na coluna do campo; saiu de outra coluna "
            "ou das linhas vizinhas; "
            "falta: não dá para saber."
        )
    )
    motivo: str = Field(description="Uma frase simples dizendo de onde veio o valor.")

    @model_validator(mode="after")
    def conferir_valor_com_origem(self) -> Self:
        """Confere que só o campo que falta vem sem valor.

        Returns:
            O próprio campo, quando está coerente.

        Raises:
            ValueError: Se a origem é "falta" com valor, ou outra origem sem valor.
        """
        if self.origem == "falta" and self.valor is not None:
            raise ValueError("Campo com origem 'falta' não pode ter valor.")
        if self.origem != "falta" and self.valor is None:
            raise ValueError("Campo escrito ou deduzido precisa de valor.")
        return self


class Venda(BaseModel):
    """Uma venda organizada, com a origem de cada campo."""

    e_venda: Campo = Field(
        description=(
            "sim ou nao: nao quando o lançamento é compra de estoque, "
            "devolução ou outra coisa que não é venda."
        )
    )
    data: Campo = Field(description="Data da venda no formato DD/MM/AAAA.")
    produto: Campo = Field(description="O que foi vendido.")
    cliente: Campo = Field(description="Nome ou descrição de quem comprou.")
    valor_produto: Campo = Field(description="Valor do produto, sem frete, como 25,00.")
    frete: Campo = Field(
        description="Valor do frete escrito no lançamento, como 12,00; senão, falta."
    )
    pagamento: Campo = Field(
        description="Forma de pagamento: pix, dinheiro, debito, credito ou fiado."
    )
    cartao: Campo = Field(
        description="Bandeira do cartão, como visa ou master; só para débito e crédito."
    )
    parcelas: Campo = Field(
        description="Número de parcelas, como 3; só para débito e crédito."
    )
    entrega: Campo = Field(
        description="Como o produto chegou: loja, correios, motoboy ou sedex."
    )
    rastreio: Campo = Field(description="Código de rastreio, como AA123456789BR.")
    observacao: Campo = Field(description="Observação escrita pela dona.")

    @model_validator(mode="after")
    def conferir_frete_escrito(self) -> Self:
        """Confere que o frete só vem quando estava escrito no lançamento.

        Returns:
            A própria venda, quando o frete está coerente.

        Raises:
            ValueError: Se o frete veio deduzido.
        """
        if self.frete.origem == "deduzido":
            raise ValueError("O frete nunca é deduzido: ou está escrito, ou falta.")
        return self
