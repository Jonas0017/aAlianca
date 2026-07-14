# Snapshot — Aliança (desenvolvimento do próprio harness) — 2026-07-14

> Ponto de retomada autossuficiente. Nova sessão (outro modelo/ferramenta, contexto zerado) retoma daqui **sem histórico anterior**. Abra uma nova conversa e diga: "continue a partir do snapshot mais recente".

## Estado atual

Este repo é o desenvolvimento da **Aliança 2.2** — o próprio harness (a pasta `alianca/` é a implementação de referência que os projetos-alvo copiam; o repo é o produto, dogfood de si mesmo). O **kernel está íntegro** (3 portões de hook do Claude Code operacionais) e acaba de ganhar **memória federada por microprojetos (bounded context)** + **route manager scope-aware**. Selftest: **89 PASS, exit 0**. A tese central já está validada (o diferencial aparece no longo prazo, sob pressão de contexto — ver `VALIDATION.md` e relatórios de benchmark na raiz). Próximo grande marco de produto continua sendo o **dogfood real** e o **empacotamento como plugin**.

## Arquitetura vigente

- **Kernel cognitivo (Claude Code), 3 portões determinísticos** — `kernel/route.py` (UserPromptSubmit: casa o prompt contra `router.index.json`, injeta módulos a carregar + contexto via grafo `pulls`, e injeta o papel "gerente por padrão"; **agora scope-aware**), `kernel/gate.py` (PreToolUse: segurança antes de ferramentas), `kernel/verify.py` (Stop: 3º portão, exige bloco Verification e trava "pronto" sem esteira armada; **agora consulta o escopo na persistência**). Suporte: `klog.py`+`kernel.log`, `compile.py` (gera `router.index.json`, grafo `pulls`), `selftest.py` (89 PASS), `session_start.py` (SessionStart/startup: roda selftest + injeta X9 obrigatória), `settings.snippet.json`, `verify.cmd`.
- **Federação de memória (novo)** — `kernel/scope.py` é o módulo **puro** que decide tudo: `resolve_scope` (marcador `microprojects/ACTIVE` + pista `[mp:<slug>]` no prompt como sinal primário; `cwd`/`codeDirs` como bônus; slug tem de estar em `registry.json` senão degrada para a raiz — **fail-open**), `merge_indices` (índice local sobrepõe a raiz por nome; módulos só-raiz continuam como fallback) e `validate_graph` (barra microprojeto sem `memory/`, `ACTIVE` órfão, hoisting quebrado e duplicação local↔raiz). Estrutura: `microprojects/{registry.json,ACTIVE,README.md}`; cada microprojeto vive em `microprojects/<slug>/` com `MICROPROJECT.md` + `memory/`. Regras completas em `instructions/microproject.md`.
- **Backbone e docs** — 18+ instruções em `instructions/` carregadas just-in-time por gatilho (`router.md`/`router.index.json`); memória federada da raiz em `memory/`; snapshots em `snapshots/`; teoria completa em `PROTOCOL.md`.

## Decisões vigentes

- **Memória federada por microprojetos** (novo, 2026-07-14) — tudo nasce local; raiz só recebe o compartilhável pela regra do 2º consumidor (hoisting com stub). Opt-in, nível ≥ 2, sempre proposto. ADR completo: `memory/decisions/2026-07-14-memoria-federada-microprojetos.md`.
- Nome/edições, nomenclatura simples, formato de entrega (`.md` + microkernel Python só Claude Code), sem `stacks/`, segurança proporcional ao risco, posicionamento "Claude Code first", PT-BR, gerente-por-padrão, esteira desde o onboarding — travadas. Detalhe: `HANDOFF.md`, git, `memory/active-context.md`.

## Em andamento

- **Follow-up da federação (aberto):** o `CMD_FILE`/`verify.cmd` do Stop hook (`verify.py`) ainda roda **sempre a esteira da RAIZ** — não seleciona a esteira local do microprojeto ativo. Resolver `CMD_FILE` via `scope.py` no `verify.py`.
- Pontas do X9 ainda abertas (ver `memory/x9-state.md`): paridade do `settings.snippet.json`, `vision.md`/mapa da pasta.
- Desativar de vez a memória nativa do Claude Code (não só apontar) — vira regra distribuída no `adopt`.

## Próximos passos

1. **Follow-up curto:** esteira local por escopo no `verify.py` (`CMD_FILE` via `scope.py`).
2. **Dogfood real** — usar a Aliança num projeto de verdade por 2–3 semanas.
3. **Empacotar como plugin do Claude Code** (resolve instalação/update/snippet).
4. Resolver a decisão pendente de onde a memória vive no projeto-alvo (raiz vs `alianca/memory/`) — docs se contradizem.

## Como retomar

1. Leia **este snapshot** (mais recente em `snapshots/`, fonte de verdade do estado).
2. Cruze com `memory/decisions/` (o porquê) e `memory/active-context.md` (o que está em andamento) e `memory/x9-state.md` (pontas soltas).
3. Confirme o estado real contra o código/git — em conflito, o repositório vence e você corrige a memória.
4. Rode `python alianca/kernel/selftest.py` (deve terminar em **89 PASS, exit 0**) antes de retomar.
5. Modelo mental do harness: `alianca/START-HERE.md` + `alianca/router.md`.
