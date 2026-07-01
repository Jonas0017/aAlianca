# Snapshot / Handoff — Projeto Aliança — 2026-07-01

> Ponto de retomada autossuficiente. Abra uma nova sessão e diga: **"continue a partir do HANDOFF.md"**. Tudo que você precisa para continuar está aqui.

## O que é o projeto

Construir a **Aliança** — um *gerador de harness* adaptativo e **model-agnostic** (qualquer LLM + outras ferramentas) que serve de base para qualquer projeto de qualquer dev. Não é um harness único: produz estruturas diferentes conforme a **persona** (P0 leigo → P3 time/org) e a **stack**. Slogan: "o elo que liga os dois mundos".

Princípios-chave: dimensionamento **multi-eixo** (Estrutura/Longevidade/Risco) com rubrica determinística; **backbone inegociável** (testes, qualidade, refatoração, prevenção de bugs); carregamento **just-in-time** de instruções por gatilho; **estado em disco** (memória/snapshots), não em % de contexto; e, desde a fase kernel, **enforce → observe → prove**: o que é crítico migra de prosa (advisory) para portão determinístico (enforcement).

## Decisões travadas

- **Nome do produto:** Aliança. Edições comerciais: Start (P0/P1), Pro (P2), Org (P3).
- **Nomenclatura simples** (usuário rejeitou nomes poéticos): `START-HERE.md`, `router.md`, `instructions/`, `memory/`, `snapshots/`, `kernel/`; instrução `setup` (bootstrap); `agents`, `coordinator`, `health-check`, `x9`.
- **Formato de entrega:** pasta-referência em `.md` puro (model-agnostic) + microkernel Python opcional (hoje só Claude Code).
- **Sem `stacks/` (decisão 2.1).** Sugerir ferramentas é trabalho da LLM, não do harness. A stack é **decidida no `setup`** e **registrada por projeto** em `memory/stack.md`.
- **Segurança proporcional ao risco, não corte em R≥40** (§16.4): qualquer sinal sensível engaja o `security`; a profundidade acompanha R.
- **Posicionamento honesto "Claude Code first":** a estrutura `.md` é model-agnostic (validada — ver `VALIDATION.md`), mas o **forcing function determinístico** (kernel de hooks) hoje existe só para Claude Code; nas demais ferramentas o harness roda em modo advisory (prosa). Adapters determinísticos = roadmap.
- Idioma de trabalho: PT-BR.

## Estrutura atual no disco

```
harness ai/
├─ README.md              ← visão geral + posicionamento honesto
├─ PROTOCOL.md            ← teoria/spec completa (17 seções, §0–§16)
├─ HANDOFF.md             ← este arquivo
├─ VALIDATION.md          ← 2 rounds de validação prática
├─ CLAUDE.md              ← kernel sempre-carregado (a receita aplicada ao próprio repo)
└─ alianca/               ← implementação de referência
   ├─ START-HERE.md       ← ponto de entrada do LLM
   ├─ router.md           ← índice de 18 instruções + gatilhos + precedência
   ├─ router.index.json   ← índice compilado (gerado por kernel/compile.py; grafo `pulls`)
   ├─ instructions/       ← TODAS as 18 prontas ✅
   │   setup · adopt · deep-questions · persona-p0 · testing · code-quality · architecture ·
   │   refactor · bug-prevention · security · interface · tasks · questions · snapshot ·
   │   migration · health-check · x9 · agents
   ├─ kernel/             ← microkernel cognitivo (Claude Code)
   │   route.py (UserPromptSubmit) · gate.py (PreToolUse) · verify.py (Stop) ·
   │   klog.py + kernel.log · compile.py · selftest.py · settings.snippet.json · verify.cmd
   ├─ memory/             ← memória do próprio desenvolvimento (active-context, x9-state)
   └─ snapshots/
```

> A **stack não tem pasta**: `memory/stack.md` é gerado por projeto no `setup` (decisão 2.1).

## Estado (o que está pronto)

- ✅ **Fases 1–4 + revisões 2.1/2.2** — espinha operacional, `setup`/`adopt`, backbone completo, instruções de sistema, módulo `interface`, forcing function "sempre ligado". Histórico detalhado no git (commits até 2026-06-10) e no PROTOCOL §15.
- ✅ **18 instruções prontas** — as 15 originais + `tasks` (4 estados de tarefa), `questions` (perguntas por tópico) e `x9` ("Rei das Pontas Soltas": auditoria de coisas criadas/prometidas pela metade, com modo monitor e estado em `memory/x9-state.md`).
- ✅ **Microkernel cognitivo operacional (Claude Code)** — 3 portões determinísticos de hook:
  1. `route.py` (`UserPromptSubmit`) — casa o prompt contra `router.index.json` e injeta quais módulos carregar (roteamento determinístico, não depende do modelo ler o router); injeta também o contexto necessário não-dito via grafo `pulls`.
  2. `gate.py` (`PreToolUse`) — portão de segurança antes de ferramentas.
  3. `verify.py` (`Stop`) — 3º portão: bloco Verification, impede declarar pronto sem observar.
  Suporte: `klog.py` grava `kernel.log` (dmesg do harness, observável); `compile.py` gera o `router.index.json` (com grafo `pulls`); `selftest.py` com **24 PASS**; `settings.snippet.json` + `verify.cmd` para instalação/verificação.
- ✅ **Validação — 2 rounds em `VALIDATION.md`:** (1) A/B com vs sem harness em duas LLMs (Claude e Copilot, 2026-06-08) — harness ganha em testes/memória/estrutura/segurança registrada, model-agnostic confirmado; (2) kernel + Ollama local (`qwen2.5-coder:7b`, 2026-07-01) — o contexto injetado virou a chave do defeito nº1 (senha em texto puro → bcrypt) num modelo 7B.
- ✅ **Auditoria X9 + parecer de arquiteto (2026-07-01)** — aprovaram correções, todas aplicadas: contagens/precedência/R≥40 corrigidos nos docs, README reposicionado honesto, `CLAUDE.md` da raiz criado (a Aliança aplicando a própria receita), memória do repo iniciada (`alianca/memory/active-context.md` + `x9-state.md`).

## Próximos passos (em ordem)

1. **Dogfood real:** usar a Aliança para construir um projeto de verdade por 2–3 semanas — é o que valida rubrica, memória e kernel sob uso contínuo (não só em teste pontual).
2. **Calibrar o roteador** com dados do `kernel.log`: quais gatilhos casam, quais módulos são injetados e ignorados, falsos positivos/negativos das keywords.
3. **Empacotar como plugin do Claude Code:** resolve instalação, update e o snippet de settings de uma vez (hoje a instalação é manual via `settings.snippet.json`).

## Como retomar

1. Leia este HANDOFF.md.
2. Leia `alianca/START-HERE.md` e `alianca/router.md` para o modelo mental; `alianca/memory/active-context.md` tem o estado corrente.
3. Rode `alianca/kernel/selftest.py` para confirmar o kernel (esperado: 24 PASS) e comece o passo 1 (dogfood real).
