---
trigger: decidir dividir trabalho entre vários agentes/especialistas (nível ≥ 3, tarefa grande com frentes paralelas independentes, ou revisão independente)
load-when: execução
applies-to: níveis ≥ 2 (opcional) · níveis ≥ 3 (recomendado)
priority: lifecycle (fora da ordem de precedência de código)
---

# agents — quando usar múltiplos agentes

Um agente só resolve a maioria dos projetos. Vários agentes só compensam quando o trabalho **realmente** se divide em frentes independentes — senão é overhead de coordenação e contexto duplicado.

## Quando NÃO dividir

- Nível 0–1, ou tarefa pequena/linear: **um agente faz tudo.**
- Subtarefas em cadeia (cada uma depende do resultado da anterior): paralelizar não ajuda.

## Quando dividir

Os agentes escalam com o nível (nenhum no 0–1; QA/documentação opcional no 2; especialistas por stack no 3; time completo + coordinator no 4 — ver PROTOCOL §11). Gatilhos concretos para dividir:
- Frentes **independentes** que rodam em paralelo (ex.: backend e frontend de telas distintas).
- Tarefa grande onde uma **revisão independente** agrega valor (um agente faz, outro revisa).
- Investigação ampla (varrer muitos arquivos) que cabe a um agente de busca dedicado.

## Regras invariantes (o coordinator)

- O **coordinator coordena, nunca executa** tarefa técnica.
- O coordinator consome **apenas resumos** dos especialistas — nunca o histórico completo.
- Cada especialista devolve um **handoff** curto: o que fez, o que mudou (`arquivo:linha`), o que falta, riscos.
- O estado partilhado vive em disco (`memory/`), não no diálogo entre agentes.

## Mapeamento por ferramenta

- **Claude Code:** especialista = subagent (tool Agent); o resumo retornado **é** o handoff. Lance em paralelo só frentes independentes (que não editam os mesmos arquivos).
- **Genérico:** sessões/roles separadas com prompt dedicado; o coordinator junta os resumos.

## Para P0 (leigo)

Invisível. Não exponha o conceito de "agentes"; apenas relate o produto.
