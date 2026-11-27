# Uso de IA no desafio

| Sugestão da IA | Decisão | Motivo |
| --- | --- | --- |
| Medir a duração da chamada em `verificar_llm.py` com `time.perf_counter()` em vez de `time.time()` | Aceita | `perf_counter` não é afetado por ajustes no relógio do computador e é mais preciso |
| Manter os nomes curtos `m` e `n` em `verificar_llm.py` | Recusada | Não quero abreviações no código; viraram `modelo_disponivel` e `nome` |
| Deixar o Docker como melhoria, fora do MVP | Recusada | Docker e CI se criam no início do projeto; escrever o Dockerfile é rápido |
| Tirar o filtro de `docs/` do CI para a PR só de documentação não travar | Recusada | Segui o padrão do meu outro projeto: o CI pula documentação e a dona do repositório faz o merge |
| Commit direto na `main`, sem PR, para ganhar tempo | Recusada | Com mais prazo, uma PR por tarefa com CI obrigatório mostra o trabalho profissional |
| Usar FastAPI para a página e o serviço | Recusada | Escolhi Django, que domino mais: no MVP, preciso revisar e explicar cada linha |
| Abrir uma PR para o commit só de documentação do mapa | Recusada | Documentação vai direto na `main`, como no meu outro projeto; a PR travou no merge |
| Deixar o LLM marcar como "escrito" o cartão e as parcelas tirados de "credito 3x visa" | Recusada | Saíram de outra coluna, então são "deduzido"; a regra dizia "claro no lançamento" e se cruzava com a de "deduzido"; reescrevi com a coluna de cada campo e um exemplo, e o Gemini acertou |
| Frete "0,00" deduzido numa venda na loja | Recusada | Um zero inventado esconde um frete esquecido; o frete só entra quando está escrito, e o Pydantic recusa frete deduzido |
| Deixar o nome do modelo escrito no código, como padrão | Recusada | Configuração vem do `.env`; o programa avisa quando falta |
