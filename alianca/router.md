# router — índice de instruções

> O índice **enxuto** da Aliança. Leia isto a cada turno; **carregue uma instrução só quando o gatilho dela casar** com o que você vai fazer agora. Não pré-carregue tudo.

```
alianca-version: 2.0
```

---

## Como usar

1. Antes de agir, percorra a tabela abaixo e veja se algum **gatilho** descreve a sua ação atual.
2. Se um ou mais casarem, abra a(s) instrução(ões) em `instructions/<arquivo>` e siga-as **antes** de agir.
3. Se dois gatilhos conflitarem, use a **ordem de precedência**.

## Ordem de precedência (quando gatilhos conflitam)

```
security  >  bug-prevention  >  testing  >  refactor  >  code-quality  >  style
```

A segurança nunca é sacrificada por estilo ou velocidade.

---

## Instruções

| Instrução | Gatilho (carregue quando…) | Fase | Aplica-se a | Status |
|---|---|---|---|---|
| `setup` | iniciar um projeto novo (sem `memory/active-context.md`) | bootstrap | todas as personas | ✅ pronto |
| `persona-p0` | usuário classificado como leigo (P0) | bootstrap+execução | P0 | ✅ pronto |
| `deep-questions` | a triagem do setup indicou algum eixo ≥ 2 | bootstrap | níveis ≥ 2 | ✅ pronto |
| `testing` | criar ou alterar lógica testável | execução | todos | ✅ pronto |
| `code-quality` | antes de commit / ao abrir PR | review | todos | ✅ pronto |
| `refactor` | detectar duplicação (3x) ou função longa demais | execução | todos | ✅ pronto |
| `bug-prevention` | escrever código com risco de erro (entrada externa, estado, concorrência) | execução | todos | ✅ pronto |
| `security` | tocar em auth, dados pessoais, pagamentos ou segredos | execução | R ≥ 40 | ✅ pronto |
| `snapshot` | antes de tarefa grande, ou ao concluir um marco | execução | níveis ≥ 1 | ✅ pronto |
| `migration` | sinais de crescimento/encolhimento cruzam um gatilho (PROTOCOL §5) | evolução | todos | ✅ pronto |
| `health-check` | revisar a saúde do harness (periódico) | review | níveis ≥ 2 | ✅ pronto |

> **Legenda:** ✅ pronto · ⏳ planejado. Ao criar uma instrução, troque o status e confira que o caminho `instructions/<arquivo>.md` existe (o `health-check` valida isso).

---

## Contrato de uma instrução

Todo arquivo em `instructions/` começa com este cabeçalho:

```
---
trigger: <condição observável que faz você carregar este módulo>
load-when: bootstrap | execução | review | migração | evolução
applies-to: <personas e/ou níveis aplicáveis>
priority: <posição na ordem de precedência>
---
<instruções completas do módulo>
```

---

## Orçamento de contexto

Carregue o **mínimo**: este `router.md` + as instruções cujo gatilho casou agora. Se várias casarem e o contexto estiver apertado, siga a ordem de precedência e carregue uma de cada vez.
