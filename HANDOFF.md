# Snapshot / Handoff — Projeto Aliança — 2026-06-08

> Ponto de retomada autossuficiente. Abra uma nova sessão e diga: **"continue a partir do HANDOFF.md"**. Tudo que você precisa para continuar está aqui.

## O que é o projeto

Construir a **Aliança** — um *gerador de harness* adaptativo e **model-agnostic** (qualquer LLM + outras ferramentas) que serve de base para qualquer projeto de qualquer dev. Não é um harness único: produz estruturas diferentes conforme a **persona** (P0 leigo → P3 time/org) e a **stack**. Slogan: "o elo que liga os dois mundos".

Princípios-chave: dimensionamento **multi-eixo** (Estrutura/Longevidade/Risco) com rubrica determinística; **backbone inegociável** (testes, qualidade, refatoração, prevenção de bugs); carregamento **just-in-time** de instruções por gatilho; **estado em disco** (memória/snapshots), não em % de contexto.

## Decisões travadas

- **Nome do produto:** Aliança. Edições comerciais: Start (P0/P1), Pro (P2), Org (P3).
- **Nomenclatura simples** (usuário rejeitou nomes poéticos): `START-HERE.md`, `router.md`, `instructions/`, `memory/`, `snapshots/`; instrução `setup` (bootstrap); `agents`, `coordinator`, `health-check`.
- **Formato de entrega:** pasta-referência em `.md` puro (model-agnostic).
- **Sem `stacks/` (decisão 2.1).** Sugerir ferramentas é trabalho da LLM, não do harness — catálogo `.md` seria redundante, inflaria contexto e apodreceria. A stack é **decidida no `setup`** e **registrada por projeto** em `memory/stack.md` (molde genérico que se adapta ao projeto do dev final). Tudo que a Aliança cria deve ser genérico e adaptável.
- Idioma de trabalho: PT-BR.

## Estrutura atual no disco

```
harness ai/
├─ PROTOCOL.md            ← teoria/spec completa (16 seções)
├─ HANDOFF.md             ← este arquivo
└─ alianca/               ← implementação de referência
   ├─ START-HERE.md       ← ponto de entrada do LLM
   ├─ router.md           ← índice de 12 instruções + gatilhos + precedência
   ├─ instructions/       ← TODAS as 12 prontas ✅
   │   setup · deep-questions · persona-p0 · testing · code-quality · architecture ·
   │   refactor · bug-prevention · security · snapshot · migration · health-check
   ├─ memory/README.md    ← documenta vision, active-context, stack.md, decisions…
   └─ snapshots/README.md
```

> A **stack não tem pasta**: `memory/stack.md` é gerado por projeto no `setup` (decisão 2.1).

## Estado (o que está pronto)

- ✅ **Fase 1** — espinha operacional (START-HERE, router, estrutura de pastas).
- ✅ **Fase 2** — `setup` (questionário progressivo por persona + rubrica 3 eixos + cálculo de nível) e `deep-questions`.
- ✅ **Fase 3** — backbone (`testing`, `code-quality`, `refactor`, `bug-prevention`, `security`) + `persona-p0`.
- ✅ **Fase 3b** — instruções de sistema (`snapshot`, `migration`, `health-check`).
- ✅ **Fase 4 (revisada → 2.1)** — em vez de "stack packs", a escolha de stack virou responsabilidade da LLM no `setup`, registrada por projeto em `memory/stack.md`. Pasta `stacks/` removida; backbone (`testing`, `code-quality`) re-apontado.
- ✅ **Revisão de arquitetura (2.1)** — após varredura completa: corrigida a memória mínima por nível (Fix #1); removido token `style` órfão (Fix #3); adicionado **módulo `architecture`** (12ª instrução, invariantes de estrutura, sem catálogo); **loop de feedback** (`memory/feedback.md`); **convenções de versionamento** por nível (setup); **recuperação de desastre** (snapshot). Pendência deliberada: calibrar o gatilho `R≥40` (ex.: "login sozinho" = 25) no dogfood.
- **Aliança está conceitualmente fechada** — as 12 instruções existem e estão registradas no router.

## Próximos passos (em ordem)

1. **Fase 5 — dogfood:** rodar o `setup` num projeto-exemplo real, ver se a rubrica dá um nível sensato, validar a geração de `memory/stack.md` e **calibrar os pesos** (§4 do PROTOCOL).
2. Pendências menores: validar travessia router→instruções com o `health-check`; conferir que nenhuma instrução ainda referencia `stacks/`.

## Como retomar

1. Leia este HANDOFF.md.
2. Leia `alianca/START-HERE.md` e `alianca/router.md` para o modelo mental.
3. Comece pela Fase 5 (dogfood): rode o `setup` num projeto-exemplo e observe se a rubrica e o `memory/stack.md` saem coerentes.

> A memória persistente (`MEMORY.md` + `projeto-keel-harness-universal.md` no diretório de memória) também reflete este estado.
