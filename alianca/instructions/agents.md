---
trigger: decidir dividir trabalho entre vários agentes/especialistas (nível ≥ 3, tarefa grande com frentes paralelas independentes, ou revisão independente)
keywords: agente, agentes, subagente, subagentes, especialistas, paralelizar, em paralelo, frentes paralelas, dividir o trabalho, orquestrar
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

## Resolução por escopo (memória federada)

Com a memória **federada** por microprojetos (ver `microproject`), a resolução de um agente/especialista segue a mesma hierarquia da memória — **local → raiz → genérico**:

1. **Local:** se o **escopo ativo** é um microprojeto e ele define um agente próprio para a frente (em `microprojects/<slug>/`), use-o — ele carrega o contexto local (memória do microprojeto).
2. **Raiz:** senão, use o agente equivalente definido na raiz (compartilhado por todos os escopos).
3. **Genérico:** senão, o agente de propósito geral.

O especialista opera no **escopo ativo**: lê/escreve na memória daquele escopo (`microprojects/<slug>/memory/` ou `alianca/memory/`), nunca cruza fronteiras sem passar pela raiz.

### Hoisting de agentes (local → raiz, no 2º consumidor)

Um agente nasce **local** no microprojeto que precisou dele. Só sobe para a raiz quando um **segundo** escopo passa a precisar do mesmo especialista (regra do 2º consumidor — a mesma do hoisting de memória em `microproject`). Ao promover: mova a definição para a raiz, deixe um **stub/ponteiro** no local e registre a aresta em `registry.json.hoisted`. Um agente usado por um escopo só **não** é candidato a hoisting — YAGNI.

## Para P0 (leigo)

Invisível. Não exponha o conceito de "agentes"; apenas relate o produto.
