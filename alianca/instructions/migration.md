---
trigger: sinais de crescimento/encolhimento do projeto cruzam um gatilho de nível
load-when: evolução
applies-to: todos os níveis
priority: lifecycle (fora da ordem de precedência de código)
---

# migration — evolução de nível do harness

O harness é um sistema vivo. Quando o projeto cresce, a estrutura sobe de nível; quando encolhe, simplifica. Reavalie a cada marco.

## Gatilhos de promoção

| De → Para | Gatilho |
|---|---|
| 0 → 1 | > 1 arquivo com lógica não-trivial, ou expectativa de retomada futura |
| 1 → 2 | ≥ 3 módulos, ou ≥ 2 devs, ou primeira integração externa |
| 2 → 3 | ≥ 6 módulos, ou dados pessoais/auth introduzidos, ou memória > 1 documento |
| 3 → 4 | múltiplos times, compliance regulatório, ou ≥ 3 agents especializados ativos |

> Risco também promove: se `R` cruzar 40 a qualquer momento, suba +1 nível e ative `security`.

## Gatilhos de simplificação (rebaixar)

- Estrutura ociosa (pastas/arquivos do nível sem uso real) e complexidade caiu de forma estável.

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
