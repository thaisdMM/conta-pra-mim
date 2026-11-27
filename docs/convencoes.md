# Convenções

## Código

- Type hints em toda assinatura (`mypy --strict` no CI).
- Uma responsabilidade por função.
- Nomes completos, sem abreviações nem apelidos curtos em imports (nada de
  `ET` ou `df_at`); o nome diz o que acontece, sem números.
- Docstrings no Google Style (`Args`, `Returns`, `Raises`): dizem o que o
  código faz, não por que a decisão foi tomada.
- Classes de erro definem só um atributo de classe com o motivo; `__init__`
  próprio só quando carregam dados extras.
- Toda chamada externa tem limite de tempo e trata o erro sem parar o
  programa: o registro com problema é marcado, e os outros seguem.
- Configuração (chave, modelo) vem do `.env`, nunca escrita no código.

## Testes

- `pytest` em `tests/`, um arquivo por módulo.
- Um comportamento por teste; docstring curta em todo teste, dizendo o que ele
  prova.
- Testes de lógica substituem o LLM por um falso, para rodar sem chave no CI.
- Testes de integração com o LLM real levam a marca `integracao` e são pulados
  quando não há chave. Rodar só eles: `uv run pytest -m integracao`.
- Os testes não substituem a execução real do programa ao fim de cada tarefa.

## Commits

`<tipo>(<escopo>): <mudança, imperativo, minúscula, sem ponto>`, com os tipos
`feat`, `fix`, `refactor`, `test`, `docs` e `chore` e bullet points simples e objetivos.
A mensagem diz o que mudou e em qual arquivo, de forma legível. Um commit por tarefa do mapa,
sem linhas de coautoria.

## Checagens antes de cada commit

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest
```
