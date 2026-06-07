---
trigger: escrever código com risco de erro — entrada externa, estado mutável, concorrência, integração
load-when: execução
applies-to: todos os níveis
priority: bug-prevention (acima de testing)
---

# bug-prevention — prevenção de bugs

O bug mais barato é o que não existe. Previna na escrita, não no debug.

## Nas fronteiras (entrada externa)

- **Valide tudo que vem de fora** (usuário, API, arquivo, env) na borda do sistema. Nunca confie no input.
- **Guard clauses / fail fast:** rejeite o inválido cedo, com erro claro, em vez de propagar estado ruim.
- Trate **nulo, vazio, limite e tipo errado** explicitamente.

## Erros

- **Sem catch silencioso.** Todo erro é tratado ou propagado com contexto — nunca engolido.
- Mensagens de erro dizem **o que** falhou e **o que fazer**.
- Recursos (arquivo, conexão, lock) são liberados sempre, inclusive em falha.

## Estado e concorrência

- Prefira **dados imutáveis**; evite estado mutável compartilhado.
- Onde há concorrência: cuidado com condições de corrida; proteja seções críticas.
- Operações que podem falhar no meio: torne-as **idempotentes** ou transacionais.

## Tipos e contratos

- **Use tipos** onde a stack permite — o compilador pega bugs de graça.
- Documente pré/pós-condições de funções não óbvias; use asserções para invariantes.

## Por nível

| Nível | Reforço |
|---|---|
| 0–1 | guard clauses + tipos quando disponíveis |
| 2–3 | **code review obrigatório**; contratos explícitos nas interfaces |
| 4 | + property-based testing e fuzzing onde aplicável |

## Anti-alucinação (vale sempre)

- Não afirme que algo funciona sem **rodar e observar**.
- Ao descrever o código, **cite `arquivo:linha`** — não invente comportamento.
