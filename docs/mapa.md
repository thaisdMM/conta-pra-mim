# Mapa do conta-pra-mim

## Estado

- Início do timer do MVP: cerca de 10h34.
- Feito: perguntas, repositório no GitHub com a `main` protegida, este mapa.
- Perguntas fechadas por volta de 11h15 (cerca de 40 minutos).
- Tarefa 1 feita na branch `feat/chamada-llm`: o Gemini organiza a linha 21
  com data, valor, entrega e a origem de cada campo certos.
- Proposta para o "MVP do MVP", a confirmar: tarefa 3, tarefa 4 com a busca dentro dela (corte 1)
  e, no fim, Docker e CI (tarefa 2).
- Próxima: tarefa 3. Na nova conversa: ler `CLAUDE.md`, `CLAUDE.local.md`,
  este mapa e `enunciado.md`; rodar `date`; mostrar o cartão e esperar o "ok".

## Ordem de corte (se o tempo apertar)

1. A busca (tarefa 5) entra na página da tarefa 4, sem página própria.
2. Na tarefa 3, o LLM trata só as datas e os pagamentos que as regras não
   resolvem; o resto vai para "Para conferir" como "falta a Maria".
3. A tela da tarefa 4 grava direto e mostra o que gravou, sem "Corrigir".

## O problema

A Maria anota as vendas numa planilha, cada dia de um jeito. Ela precisa
registrar uma venda e achar uma informação depois, sozinha, sem perder o que já
anotou. Ver `enunciado.md`.

## Decisões

| Decisão | Escolha | Alternativa recusada |
| --- | --- | --- |
| Como a Maria usa | Página no navegador, simples e com botões grandes | Continuar só na planilha; bot do Telegram (virou melhoria) |
| Base da página | Django, que a usuária domina | FastAPI, sugerido pela IA |
| Onde ficam as vendas | Planilha organizada (`.xlsx`), que ela abre no Excel | Banco SQLite |
| Planilha original | Lida uma vez e nunca alterada | Acrescentar vendas nela |
| Campos da planilha antiga | Escrito, deduzido (com o motivo) ou falta a Maria | Deixar o LLM decidir tudo; descartar a linha |
| Quem deduz | Regras fixas para os formatos que se repetem; o LLM só nas linhas que as regras não resolvem, com as linhas vizinhas como contexto | O LLM recebe todas as linhas |
| Dúvidas para a Maria | Aba "Para conferir" na planilha organizada, uma frase simples por dúvida | Ela conferir linha por linha |
| Lançamento que não é venda | Fica na planilha e vai para "Para conferir" | Apagar |
| Registrar venda | Ela escreve como fala, o LLM organiza, a página mostra e ela clica "Salvar" | Gravar direto |
| Buscar venda | Uma caixa com uma palavra, sem LLM | Pergunta livre ao LLM (virou melhoria) |
| Fiado | Forma de pagamento "fiado"; buscar "fiado" mostra quem deve | Campo "pago: sim ou não" (fica para depois) |
| Frete | Valor do produto e frete em campos separados, com um aviso visível de que a venda tem frete | Um valor total com o frete na observação |
| Como ela abre o app | Alguém instala uma vez no computador dela; ela abre um atalho. Dito no README e na apresentação | App na internet (virou melhoria) |
| Dados de clientes no LLM | Só as linhas que as regras não resolvem vão ao Gemini; ponto para a apresentação | Mandar todas as linhas |

## Tarefas do MVP

Cada tarefa tem uma branch e uma PR, com o CI obrigatório.

### Tarefa 1: chamada real ao LLM com um lançamento

- **O que fazer:** mandar ao Gemini um lançamento difícil da planilha (por
  exemplo, "credito 3x visa" sem cartão nem parcelas nas colunas) e receber os
  campos da venda validados pelo Pydantic, cada campo com a origem (escrito,
  deduzido, falta) e o motivo. Limite de tempo e tratamento de erro.
- **Arquivos:** o módulo de leitura com o LLM, o modelo Pydantic da venda e o
  teste com um LLM falso.
- **Pronto quando:** `uv run python verificar_llm.py` responde, a execução
  real mostra o lançamento organizado e os testes passam.
- **Requisito da vaga:** IA generativa; testes e validações.
- **Tempo:** 10 min.

### Tarefa 2: Django, Docker e CI

- **O que fazer:** criar o projeto Django com uma página vazia, o Dockerfile, o
  Docker Compose e o job `build` no CI. Escrever no README como rodar.
- **Arquivos:** projeto Django, `Dockerfile`, `compose.yaml`,
  `.github/workflows/ci.yml`, `README.md`.
- **Pronto quando:** `docker compose up` abre a página no navegador e o CI
  passa.
- **Risco:** o `mypy --strict` com Django pode exigir pacotes de tipos; se
  travar, avisar e propor o corte.
- **Requisito da vaga:** boas práticas, Git, Python.
- **Tempo:** 10 min.

### Tarefa 3: organizar a planilha antiga

- **O que fazer:** ler `dados/planilha_original_maria.xlsx`, aplicar as regras
  fixas (datas, valores, pagamento), mandar ao LLM só as linhas que sobraram e
  gravar a planilha organizada com a aba "Para conferir".
- **Arquivos:** módulo das regras, módulo da planilha, testes.
- **Pronto quando:** a execução real gera a planilha organizada a partir do
  arquivo real e mostra quantas linhas foram para "Para conferir".
- **Requisito da vaga:** dados estruturados e não estruturados.
- **Tempo:** 15 min.

### Tarefa 4: página para registrar uma venda

- **O que fazer:** caixa "Conte a venda", o LLM organiza, a página mostra o
  resultado em frases simples com "Salvar" e "Corrigir"; "Salvar" grava na
  planilha organizada.
- **Arquivos:** view, template e teste.
- **Pronto quando:** uma venda escrita na página aparece na planilha
  organizada.
- **Requisito da vaga:** integração com sistemas e APIs.
- **Tempo:** 10 min.

### Tarefa 5: página para buscar uma venda

- **O que fazer:** uma caixa de busca por palavra (nome, pagamento, rastreio)
  que mostra as vendas encontradas.
- **Arquivos:** view, template e teste.
- **Pronto quando:** buscar "AA123456789BR" mostra a venda do colar dourado da
  Ana.
- **Requisito da vaga:** Python.
- **Tempo:** 5 min.

### Fim do MVP

Se estiver bom: tag `mvp-2h` e os horários de início e de fim no README.

## Melhorias (depois do MVP, sem prazo)

1. Tela de confirmação: a aba "Para conferir" vira uma página com "sim" e
   "corrigir" para cada dúvida.
2. Bot do Telegram: a Maria registra e busca pelo chat, inclusive com
   pergunta livre ("quanto a Ana me pagou em setembro?").
3. App na internet com link fixo (por exemplo, no Render), para ela não
   depender de instalação.
4. Entrar pelo Excel: ela continua anotando na planilha, e um botão
   "organizar de novo" trata só as linhas novas.
