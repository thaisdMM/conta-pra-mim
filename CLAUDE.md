# Regras de trabalho

## Contexto do projeto

Repositório único. O código fica em `src/` e os testes em `tests/`.

A stack e as ferramentas não ficam listadas aqui: o que se escreve neste
arquivo envelhece e vira exatamente o erro que a regra 9 existe para evitar.

## Ler antes de cada tarefa

- `pyproject.toml`: stack, ferramentas e versões declaradas.
- `enunciado.md`: o que foi pedido.
- `docs/mapa.md`: decisões e tarefas aprovadas.

Ler só quando a tarefa tocar no assunto:

- `docs/convencoes.md`: antes de escrever código, teste ou mensagem de commit.
- `docs/uso-de-ia.md`: ao fim de cada tarefa, para registrar as sugestões.

## Regras absolutas

1. **Nunca inferir, nunca supor, nunca preencher lacunas.**
   Se a informação falta, está incompleta ou é ambígua, parar e perguntar,
   agrupando as perguntas como diz a regra 5. Não completar o que "parece
   lógico" pelo contexto. Uma suposição errada custa mais para corrigir do que
   uma pergunta custa para fazer. Uma escolha de rotina não é informação
   faltando: ela fica com a regra 5.

2. **Ler os arquivos relevantes. Nunca responder por padrão do treinamento.**
   Antes de responder ou alterar, ler o arquivo inteiro, não só o trecho
   colado na conversa: imports e classes de base carregam informação que não
   aparece no trecho. Ler um arquivo custa menos do que reescrever uma resposta
   errada.

3. **Aprovar o plano uma vez por tarefa.**
   Antes do código, apresentar o plano em tópicos: as peças e as escolhas que
   mudam o comportamento. Esperar a aprovação explícita uma vez; depois,
   escrever as peças sem parar a cada uma.

4. **Não alterar nada fora do escopo da tarefa.**
   Se uma mudança fora do escopo for necessária, explicar o motivo e pedir
   permissão antes.

5. **Perguntar só as escolhas que mudam o comportamento.**
   Quando a escolha muda o que o programa faz (saída, dados gravados, regras
   de negócio), parar e perguntar. Cada pergunta traz as opções (até quatro),
   a diferença entre elas, a recomendada e o motivo. Escolhas de rotina
   (nomes, organização dos arquivos, estrutura dos testes, a API idiomática da
   versão em uso) são feitas sem perguntar e citadas com o motivo.

6. **Tudo em português**: código, nomes, docstrings, documentação e commits.
   Só os prefixos do Conventional Commits ficam em inglês.

7. **Sem comentários no meio do código**, salvo quando indispensáveis. O que
   precisa ser dito vai na docstring.

8. **Seguir os padrões existentes.** Antes de escrever algo novo, ler o
   arquivo parecido que já existe e seguir o mesmo padrão.

9. **Conferir a versão em uso antes de propor qualquer código.**
   O treinamento fica atrás da stack. Antes de sugerir qualquer API, método,
   configuração, modelo de LLM ou comando, conferir o que está realmente em
   uso: `pyproject.toml` para a versão mínima e `uv.lock` para a resolvida
   (ler só as linhas `name` e `version` dos pacotes envolvidos, nunca o
   arquivo inteiro). Se a versão estiver fora do que o treinamento cobre, ler
   a documentação oficial daquela versão. Nunca propor algo suspeito de estar
   obsoleto dentro da versão em uso.
   Esta regra vale para toda proposta, não só para as duvidosas: o erro que ela
   pega é a resposta confiante baseada numa versão antiga, que, por ser
   confiante, nunca aciona a regra 1. Exemplo real: um modelo de LLM tirado da
   documentação da biblioteca, sem chamada real com a chave, não respondia no
   plano gratuito.

10. **Provar com o recurso real, não só com testes falsos.**
    Testes com um falso (por exemplo, um LLM falso) provam a lógica, não a
    integração. Toda tarefa que toca um recurso externo (LLM, API, arquivo
    real, banco) termina com uma execução real do programa, e o resultado é
    mostrado. Antes da primeira tarefa com o LLM, rodar
    `uv run python verificar_llm.py`. Toda chamada externa tem limite de
    tempo: o programa nunca pode ficar parado esperando.

11. **Não rodar comandos que mudam estado sem permissão**: instalações,
    remoções e edições de configuração.

12. **Todo bug encontrado é corrigido com um teste de regressão.**
    Primeiro, um teste que reproduz o bug e falha no código atual; depois, a
    correção até ele passar. Um bug fora da tarefa atual segue a regra 4: vai
    para o mapa e é corrigido em tarefa própria.

13. **Sem commit sem aprovação da mensagem**, e sem linhas de coautoria.

## Regra 1 × regra 5

As duas parecem iguais, mas cobrem situações diferentes:

- **Regra 1**: a informação **falta**. Um campo não foi definido, um caminho
  não está claro, um requisito é ambíguo. Não dá para seguir porque não se
  sabe o que é verdade.
- **Regra 5**: a informação **existe, mas sobra uma escolha**. Dois padrões
  válidos, duas bibliotecas possíveis. Dá para seguir: se a escolha muda o
  comportamento, quem decide é a usuária; se é rotina, escolher e citar.

Na dúvida, tratar como regra 1 e perguntar.
