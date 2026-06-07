# Snapshot / Handoff — Projeto Aliança — 2026-06-07

> Ponto de retomada autossuficiente. Abra uma nova sessão e diga: **"continue a partir do HANDOFF.md"**. Tudo que você precisa para continuar está aqui.

## O que é o projeto

Construir a **Aliança** — um *gerador de harness* adaptativo e **model-agnostic** (qualquer LLM + outras ferramentas) que serve de base para qualquer projeto de qualquer dev. Não é um harness único: produz estruturas diferentes conforme a **persona** (P0 leigo → P3 time/org) e a **stack**. Slogan: "o elo que liga os dois mundos".

Princípios-chave: dimensionamento **multi-eixo** (Estrutura/Longevidade/Risco) com rubrica determinística; **backbone inegociável** (testes, qualidade, refatoração, prevenção de bugs); carregamento **just-in-time** de instruções por gatilho; **estado em disco** (memória/snapshots), não em % de contexto.

## Decisões travadas

- **Nome do produto:** Aliança. Edições comerciais: Start (P0/P1), Pro (P2), Org (P3).
- **Nomenclatura simples** (usuário rejeitou nomes poéticos): `START-HERE.md`, `router.md`, `instructions/`, `memory/`, `snapshots/`, `stacks/`; instrução `setup` (bootstrap); `agents`, `coordinator`, `health-check`.
- **Formato de entrega:** pasta-referência em `.md` puro (model-agnostic).
- Idioma de trabalho: PT-BR.

## Estrutura atual no disco

```
harness ai/
├─ PROTOCOL.md            ← teoria/spec completa (16 seções)
├─ HANDOFF.md             ← este arquivo
└─ alianca/               ← implementação de referência
   ├─ START-HERE.md       ← ponto de entrada do LLM
   ├─ router.md           ← índice de 11 instruções + gatilhos + precedência
   ├─ instructions/       ← TODAS as 11 prontas ✅
   │   setup · deep-questions · persona-p0 · testing · code-quality ·
   │   refactor · bug-prevention · security · snapshot · migration · health-check
   ├─ memory/README.md
   ├─ snapshots/README.md
   └─ stacks/README.md
```

## Estado (o que está pronto)

- ✅ **Fase 1** — espinha operacional (START-HERE, router, estrutura de pastas).
- ✅ **Fase 2** — `setup` (questionário progressivo por persona + rubrica 3 eixos + cálculo de nível) e `deep-questions`.
- ✅ **Fase 3** — backbone (`testing`, `code-quality`, `refactor`, `bug-prevention`, `security`) + `persona-p0`.
- ✅ **Fase 3b** — instruções de sistema (`snapshot`, `migration`, `health-check`).
- **Aliança está conceitualmente fechada** — as 11 instruções existem e estão registradas no router.

## Próximos passos (em ordem)

1. **Fase 4 — primeira stack pack** em `stacks/` (recomendo `next.md` ou `fastapi.md`): runner de teste, lint/format, CI, `.gitignore`/`.env.example`, comandos concretos. Tira o backbone do abstrato.
2. **Fase 5 — dogfood:** rodar o `setup` num projeto-exemplo real, ver se a rubrica dá um nível sensato e **calibrar os pesos** (§4 do PROTOCOL).
3. Pendências menores: validar travessia router→instruções com o `health-check`; decidir 2ª/3ª stack packs.

## Como retomar

1. Leia este HANDOFF.md.
2. Leia `alianca/START-HERE.md` e `alianca/router.md` para o modelo mental.
3. Comece pela Fase 4 (stack pack) — pergunte ao usuário qual stack priorizar se ele não disser.

> A memória persistente (`MEMORY.md` + `projeto-keel-harness-universal.md` no diretório de memória) também reflete este estado.
