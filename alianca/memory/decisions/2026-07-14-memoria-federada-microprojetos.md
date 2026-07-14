# ADR — Memória federada por microprojetos (bounded context)

- **Data:** 2026-07-14
- **Status:** aceita e implementada (selftest 89 PASS, exit 0)

## Contexto

Uma memória plana única na raiz (`alianca/memory/`) incha e **sobrecarrega a memória principal** conforme o projeto vira um sistema completo: `active-context.md` passa a misturar ≥ 2 bounded contexts, o índice fica ruidoso e o custo de contexto de cada turno cresce. Era o problema central que sabotava a tese de longo prazo (estado em disco, janela do pai limpa).

## Decisão

Adotar **memória federada por microprojetos**. Um bounded context independente (fronteira, dono e objetivo próprios) ganha **memória local** em `alianca/microprojects/<slug>/memory/`; a raiz vira o **fallback compartilhado**. Regras:

- **Nasce local.** Todo fato começa na memória do microprojeto. A raiz só recebe o **compartilhável**, e só pela **regra do 2º consumidor** (hoisting: move para a raiz, deixa **stub** com marcador `hoisted` no local — `validate_graph` barra duplicação).
- **Opt-in, nível ≥ 2, sempre PROPOSTO ao humano.** Projeto simples segue plano na raiz. Nunca criar microprojeto sozinho.
- **Uma memória por escopo ativo** (hierárquica, nunca duas em paralelo). O kernel resolve **um** escopo por turno.
- **Kernel scope-aware.** `kernel/scope.py` (módulo puro) decide o escopo: sinal primário = marcador `microprojects/ACTIVE` + pista `[mp:<slug>]` no prompt; `cwd`/`codeDirs` são bônus. Slug precisa estar em `registry.json` senão **degrada para a raiz**. `merge_indices` faz o índice local sobrepor a raiz por nome; `validate_graph` guarda a integridade do grafo.

## Consequências

- **Positivas:** a raiz nunca mais sobrecarrega; cada frente acumula sua própria memória/decisões/tarefas; back-compat total (registro vazio → raiz) e **fail-open** (registry corrompido → raiz, sem crash) verificados; +25 testes no selftest (64 → 89 PASS).
- **Custo:** overhead de federação só se paga com independência real — microprojeto para "mais um arquivo" do mesmo contexto é dívida (documentado em `microproject.md`).
- **Superfície nova:** `kernel/scope.py`, `instructions/microproject.md`, `microprojects/{registry.json,ACTIVE,README.md}`; alterados route/verify/compile/session_start/selftest, router.md, START-HERE §5, memory/README, x9/snapshot.

## Decisão residual em aberto (para o humano)

O **`CMD_FILE`/`verify.cmd` do Stop hook (`verify.py`) ainda roda sempre a esteira da RAIZ** — não seleciona a esteira local do microprojeto ativo. Follow-up curto: **resolver `CMD_FILE` via `scope.py` no `verify.py`** para que o 3º portão execute a esteira do escopo ativo. Até lá, um microprojeto com teste próprio (`microprojects/<slug>/verify.cmd`) não é exercido automaticamente pelo Stop hook.
