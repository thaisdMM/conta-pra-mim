"""Confere se a chave do Gemini funciona, com uma chamada real e limite de tempo."""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

LIMITE_MILISSEGUNDOS = 30_000


def main() -> None:
    """Lista os modelos flash da chave e faz uma chamada curta ao modelo escolhido."""
    load_dotenv(".env")
    modelo = os.environ.get("GEMINI_MODELO", "gemini-3.5-flash-lite")
    cliente = genai.Client(http_options=types.HttpOptions(timeout=LIMITE_MILISSEGUNDOS))
    nomes = [
        modelo_disponivel.name
        for modelo_disponivel in cliente.models.list()
        if "flash" in (modelo_disponivel.name or "")
    ]
    print("Modelos flash da chave:", ", ".join(nome for nome in nomes if nome))
    inicio = time.perf_counter()
    resposta = cliente.models.generate_content(model=modelo, contents="Responda só: ok")
    print(f"{modelo} respondeu em {time.perf_counter() - inicio:.1f}s: {resposta.text}")


if __name__ == "__main__":
    main()
