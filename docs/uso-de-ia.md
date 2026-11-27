# Uso de IA no desafio

| Sugestão da IA | Decisão | Motivo |
| --- | --- | --- |
| Medir a duração da chamada em `verificar_llm.py` com `time.perf_counter()` em vez de `time.time()` | Aceita | `perf_counter` não é afetado por ajustes no relógio do computador e é mais preciso |
| Manter os nomes curtos `m` e `n` em `verificar_llm.py` | Recusada | Não quero abreviações no código; viraram `modelo_disponivel` e `nome` |
| Deixar o Docker como melhoria, fora do MVP | Recusada | Docker e CI se criam no início do projeto; escrever o Dockerfile é rápido |
| Tirar o filtro de `docs/` do CI para a PR só de documentação não travar | Recusada | Segui o padrão do meu outro projeto: o CI pula documentação e a dona do repositório faz o merge |
| Commit direto na `main`, sem PR, para ganhar tempo | Recusada | Com mais prazo, uma PR por tarefa com CI obrigatório mostra o trabalho profissional |
| Usar FastAPI para a página e o serviço | Recusada | Escolhi Django, que domino mais: no MVP, preciso revisar e explicar cada linha |
