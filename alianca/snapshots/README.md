# snapshots

Pontos de **retomada**. Um snapshot é um documento **autocontido** que permite reiniciar uma sessão (outro modelo, outra ferramenta, novo contexto) **sem depender do histórico anterior**.

## Cada snapshot contém

- Estado atual e o que está em andamento.
- Arquitetura vigente (resumo).
- Decisões vigentes (ponteiros para `../memory/decisions/`).
- Tarefas abertas.
- Próximos passos concretos.

## Convenção

- Nome: `snapshot-AAAA-MM-DD-<slug>.md`.
- Gerado: antes de tarefa grande e ao concluir um marco (nível ≥ 1); automático por marco no nível 4.
- O mais recente é a fonte de verdade para retomada (ver `../START-HERE.md` §2).
