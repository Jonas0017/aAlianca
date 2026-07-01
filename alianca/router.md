# router — índice de instruções

> O índice **enxuto** da Aliança. Leia isto a cada turno; **carregue uma instrução só quando o gatilho dela casar** com o que você vai fazer agora. Não pré-carregue tudo.

```
alianca-version: 2.2
```

---

## Como usar

1. Antes de agir, percorra a tabela abaixo e veja se algum **gatilho** descreve a sua ação atual.
2. Se um ou mais casarem, abra a(s) instrução(ões) em `instructions/<arquivo>` e siga-as **antes** de agir.
3. Se dois gatilhos conflitarem, use a **ordem de precedência**.

## Ordem de precedência (quando gatilhos conflitam)

```
security  >  bug-prevention  >  testing  >  architecture  >  refactor  >  interface  >  code-quality
```

A segurança nunca é sacrificada por estilo ou velocidade. (Estilo/formatação não é um módulo à parte — é o piso do `code-quality`.) `interface` e `code-quality` são pisos de superfícies diferentes — o que o humano usa e o código-fonte — e raramente colidem; quando colidem, correção vem antes de aparência.

> Os módulos de ciclo de vida (`tasks`, `questions`, `snapshot`, `migration`, `health-check`, `x9`, `agents`) ficam **fora** desta ordem — coordenam o trabalho, não competem com os módulos de código.

---

## Instruções

| Instrução | Gatilho (carregue quando…) | Fase | Aplica-se a | Status |
|---|---|---|---|---|
| `setup` | iniciar um projeto **novo** (sem código e sem `memory/active-context.md`) | bootstrap | todas as personas | ✅ pronto |
| `tasks` | criar uma tarefa, ou mover uma tarefa entre os 4 estados (sobretudo ao declarar algo "pronto") | execução | todos | ✅ pronto |
| `questions` | perguntar algo sobre o projeto, adiar uma resposta ("responde depois") ou registrar uma resposta | execução | todos | ✅ pronto |
| `adopt` | integrar a Aliança a um projeto que **já existe** (há código/docs, sem pasta `alianca/`) | bootstrap | todas as personas | ✅ pronto |
| `persona-p0` | usuário classificado como leigo (P0) | bootstrap+execução | P0 | ✅ pronto |
| `deep-questions` | a triagem do setup indicou algum eixo ≥ 2 | bootstrap | níveis ≥ 2 | ✅ pronto |
| `testing` | criar ou alterar lógica testável | execução | todos | ✅ pronto |
| `code-quality` | antes de commit / ao abrir PR | review | todos | ✅ pronto |
| `architecture` | criar/alterar estrutura: novo módulo, camada, fronteira ou dependência | execução | todos | ✅ pronto |
| `refactor` | detectar duplicação (3x) ou função longa demais | execução | todos | ✅ pronto |
| `bug-prevention` | escrever código com risco de erro (entrada externa, estado, concorrência) | execução | todos | ✅ pronto |
| `security` | tocar em auth, dados pessoais, pagamentos ou segredos | execução | todos (profundidade ∝ risco) | ✅ pronto |
| `interface` | criar/alterar superfície humana: tela, layout, componente, fluxo, CLI/TUI, texto ou erro de UI | execução | todos | ✅ pronto |
| `snapshot` | antes de tarefa grande, ou ao concluir um marco | execução | níveis ≥ 1 | ✅ pronto |
| `migration` | sinais de crescimento/encolhimento cruzam um gatilho (PROTOCOL §5) | evolução | todos | ✅ pronto |
| `health-check` | revisar a saúde do harness (periódico) | review | níveis ≥ 2 | ✅ pronto |
| `x9` | auditar **pontas soltas** do projeto: coisas criadas/prometidas/iniciadas pela metade que quebram o fluxo (roda pontual ou em modo monitor) | review | todos | ✅ pronto |
| `agents` | dividir trabalho entre especialistas: nível ≥ 3, frentes paralelas independentes, ou revisão independente | execução | níveis ≥ 2 | ✅ pronto |

> **Legenda:** ✅ pronto · ⏳ planejado. Ao criar uma instrução, troque o status e confira que o caminho `instructions/<arquivo>.md` existe (o `health-check` valida isso).

---

## Contrato de uma instrução

Todo arquivo em `instructions/` começa com este cabeçalho:

```
---
trigger: <condição observável que faz você carregar este módulo>
keywords: <palavras que o roteador casa no prompt; opcional — se ausente, o compile.py deriva do trigger>
load-when: bootstrap | execução | review | migração | evolução
applies-to: <personas e/ou níveis aplicáveis>
priority: <posição na ordem de precedência>
---
<instruções completas do módulo>
```

---

## Orçamento de contexto

Carregue o **mínimo**: este `router.md` + as instruções cujo gatilho casou agora. Se várias casarem e o contexto estiver apertado, siga a ordem de precedência e carregue uma de cada vez.
