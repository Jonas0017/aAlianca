---
trigger: sinais de crescimento/encolhimento do projeto cruzam um gatilho de nível
keywords: mudar de nivel, subir de nivel, rebaixar o nivel, promover o nivel, gatilho de nivel, nivel do harness, migrar de nivel
load-when: evolução
applies-to: todos os níveis
priority: lifecycle (fora da ordem de precedência de código)
---

# migration — evolução de nível do harness

O harness é um sistema vivo. O nível do `setup` é só a **estimativa inicial** — observe o comportamento real do projeto de tempos em tempos (não só nos marcos) e ajuste: o usuário pode ter subestimado, ou a estrutura prometida pode nunca ter surgido. **Suba** quando a complexidade real aparece; **rebaixe** quando a estrutura fica ociosa.

## Gatilhos de promoção

| De → Para | Gatilho |
|---|---|
| 0 → 1 | > 1 arquivo com lógica não-trivial, ou expectativa de retomada futura |
| 1 → 2 | ≥ 3 módulos, ou ≥ 2 devs, ou primeira integração externa |
| 2 → 3 | ≥ 6 módulos, ou dados pessoais/auth introduzidos, ou memória segmentada além da mínima (`active-context` + `stack`) |
| 3 → 4 | múltiplos times, compliance regulatório, ou ≥ 3 agents especializados ativos |

> Risco também promove: se `R` cruzar 40 a qualquer momento, suba +1 nível e ative `security`.

## Gatilhos de simplificação (rebaixar)

- Estrutura ociosa (pastas/arquivos do nível sem uso real) e complexidade caiu de forma estável.

## Gatilho de federação (memória plana inchada → microprojeto)

Migração não é só de nível: a **memória** também evolui. Quando a memória plana da raiz incha — o `memory/active-context.md` já mistura **≥ 2 bounded contexts** distintos, ou um subsistema independente passou a acumular decisões/tarefas próprias que não interessam ao resto — é sinal de **federar**.

- **Gatilho:** ≥ 2 bounded contexts convivendo no `active-context.md`, ou uma frente independente que já pesa na memória principal.
- **Ação:** carregue `microproject` e **proponha** (nível ≥ 2, nunca automático) extrair o **1º bounded context** para `alianca/microprojects/<slug>/`, movendo a memória daquela frente para lá.
- **Aditivo e reversível:** o conhecimento se **move** (raiz → microprojeto), não se perde; concluir/rebaixar arquiva de volta (ver `microproject` §CONCLUIR). A raiz continua sendo o **fallback compartilhado**.

## Procedimento

1. **Reavalie os 3 eixos** (E, L, R) com a rubrica do `setup` — os números mudaram?
2. **Recalcule o nível.** Mudou?
3. **Proponha ao usuário** a mudança, explicando o porquê em uma frase (P0: linguagem humana).
4. Após o "sim":
   - **Promover:** crie as novas pastas/arquivos do nível-alvo; não recrie o que já existe.
   - **Rebaixar:** **arquive** o excedente em `memory/archive/` — **nunca apague**.
5. **Registre** a mudança em `memory/decisions/` e gere um `snapshot`.
6. Atualize o `router.md` (instruções que passam a ser relevantes) e o `alianca-version` se aplicável.

## Princípio

Migração é aditiva e reversível por padrão. Conhecimento nunca se perde — ele se move para `archive/`.

## Migração de versão da Aliança (≠ migração de nível)

Subir de **nível** muda a estrutura do *projeto*; atualizar a **versão da Aliança** muda o *harness* em si. São coisas diferentes.

Ao chegar a um projeto cujo `router.md` declara um `alianca-version` **anterior** ao da Aliança atual:

1. Não quebre o projeto. Veja o que mudou entre as versões (changelog no `PROTOCOL` / `HANDOFF`).
2. Rode o `health-check` para mapear o que está desalinhado com a versão nova.
3. Aplique o **diff de estrutura** de forma aditiva (novas instruções/pastas); arquive o obsoleto em `memory/archive/` — nunca apague.
4. Atualize `alianca-version` no `router.md` e registre a migração em `memory/decisions/`.
