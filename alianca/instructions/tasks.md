---
trigger: criar uma tarefa nova, ou mover uma tarefa entre estados (sobretudo ao declarar algo "pronto")
load-when: execução
applies-to: todos os níveis (a estrutura escala; o fluxo dos 4 estados não)
priority: fora da ordem de precedência — módulo de ciclo de vida (coordena o trabalho, não compete com os módulos de código)
---

# tasks — como criar e mover tarefas

> O quadro de trabalho da Aliança. Uma tarefa atravessa **4 estados**, e a fronteira entre o 3º e o 4º é onde o harness paga a dívida do anti-alucinação: "escrevi" não é "funciona".

## Os 4 estados

| # | Estado | Significa | Como sai daqui |
|---|---|---|---|
| 1 | **A fazer** | definida, ainda não começou | alguém pega → vira *Em andamento* |
| 2 | **Em andamento** | sendo trabalhada agora (foco) | código escrito e auto-declarado pronto → *Realizada* |
| 3 | **Realizada** | código existe; o agente **acha** que está pronto — mas **ninguém rodou/observou ainda** | passa pelo VERIFICAR (testes verdes, lint limpo, comportamento observado, docs/memória atualizados) → *Validada* |
| 4 | **Validada e testada** | DoD satisfeito **de fato**: rodou, observou, cita `arquivo:linha` ou saída de teste | tarefa **fechada** |

**O 3º estado é deliberadamente desconfiado.** "Realizada" é o limbo do *"achei que funciona"* — onde a maioria dos bugs e do retrabalho mora. Uma tarefa só **fecha** quando chega a *Validada*; nada pula da escrita direto para fechado.

### A fronteira Realizada → Validada (a única regra inegociável)

Mover para *Validada* exige **rodar e observar** — nunca declarar pronto de cabeça (invariante anti-alucinação, `START-HERE` §5). O contrato (DoD):

- **testes verdes** (ver `testing`) · **lint limpo** (ver `code-quality`) · **comportamento observado** (rodou, viu acontecer) · **docs/memória atualizados**.
- Ao afirmar que algo funciona, **cite a evidência**: `arquivo:linha`, saída do teste, ou o que você observou.

Se o VERIFICAR falha, a tarefa **volta para Em andamento** com a abordagem ajustada — não insista no que não funcionou (é loop, não fila — `START-HERE` §4). Erro que **se repete** vira regra em `memory/feedback.md`.

## Onde as tarefas vivem (esquema índice + arquivo)

Mesma mecânica da memória segmentada e das `decisions/`: um **índice** que aponta para **um arquivo por item** — e o arquivo só nasce quando a tarefa merece. Escala com o nível:

- **Nível 0–1:** um único `TASKS.md` na raiz. As 4 seções **são** o índice; cada tarefa é uma linha. Sem pasta, sem arquivo por tarefa.
- **Nível 2+:** pasta `tasks/` na raiz. `tasks/TASKS.md` é o **índice** (as 4 seções, uma linha por tarefa apontando para o arquivo); tarefa não-trivial ganha `tasks/<slug>.md` próprio (contexto, DoD, evidência de validação). Tarefa pequena continua só na linha do índice.

> **Uma só fonte de verdade:** o quadro é o estado **estruturado** do trabalho; `memory/active-context.md` é a **narrativa do agora** e aponta para a tarefa *Em andamento* atual. Nunca duplique o status nos dois — o quadro manda no status, o active-context conta a história.

### Molde do índice (`TASKS.md`)

```
# TASKS — <projeto>

## A fazer
- [ ] <tarefa>   ·  DoD: testes verdes · lint limpo · docs/memória atualizados

## Em andamento
- [ ] <tarefa>   ·  <dono/agente, se houver>

## Realizada (escrita — aguardando validação)
- [~] <tarefa>   ·  <o que falta observar para validar>

## Validada e testada
- [x] <tarefa>   ·  <AAAA-MM-DD> · <evidência: teste/observação>
```

A partir do Nível 2, cada `[~]`/`[x]` não-trivial vira link para `tasks/<slug>.md`: `- [~] [<título>](<slug>.md) · …`.

### Molde do arquivo de tarefa (Nível 2+, `tasks/<slug>.md`)

```
---
status: a-fazer | em-andamento | realizada | validada
dono: <agente/pessoa, se houver>
---
# <título da tarefa>

**Objetivo:** <o que e por quê, em uma frase>
**DoD:** testes verdes · lint limpo · comportamento observado · docs/memória atualizados
**Evidência de validação:** <preenchido ao mover para Validada — teste/saída/arquivo:linha>
```

## Regras de operação

- **Limite de WIP:** mantenha *Em andamento* curto (idealmente 1). Muitas tarefas abertas ao mesmo tempo = nenhuma terminada.
- **Granularidade:** uma tarefa cabe num DoD verificável. Se não dá para descrever como provar que ficou pronta, ela está grande demais — quebre.
- **P0 (leigo):** descreva a tarefa em **linguagem de produto**, sem jargão; reporte em "o que foi feito / o que falta / o que preciso de você" (ver `persona-p0`).
- **Marco:** ao fechar um conjunto de tarefas *Validadas*, gere um `snapshot` e consolide a memória.
