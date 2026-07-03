# active-context — desenvolvimento da Aliança

> Estado de trabalho corrente. Atualize a cada marco (loop `START-HERE §4`, passo PERSISTIR). O detalhe histórico mora nos arquivos citados — aqui fica só o essencial pra retomar.

## O projeto

Desenvolvimento da **Aliança 2.2** — o próprio harness. Este repo é o produto; `alianca/` é a implementação de referência que os projetos-alvo copiam.

## Onde estamos (2026-07-02)

- **Kernel operacional** — 3 portões (Claude Code): `route.py` (UserPromptSubmit) · `gate.py` (PreToolUse) · `verify.py` (Stop), + `klog`/`kernel.log`, `selftest.py` (58 PASS), `compile.py` (gera `router.index.json` com grafo `pulls`). Decisões e detalhe: git + `x9-state.md`.
- **18 instruções prontas** (inclui `tasks`, `questions`, `x9`). Roteador calibrado (keywords curadas + força mínima 2 p/ derivadas). Auditoria X9 + parecer de arquiteto fechados — `x9-state.md`.
- **Validação** (`VALIDATION.md` + benchmark Ollama `qwen2.5-coder:7b`): confirma a tese central — **o diferencial só aparece no longo prazo, quando o trabalho excede a janela.** Sob pressão de contexto, SEM alucina o contrato (integração 0%); COM mantém 100%. Em janela folgada, empatam (prova anti-viés: a diferença vem só da pressão). Números completos: `RELATORIO-FINAL-alianca.md`, `RELATORIO-fase1-longo-prazo.md`, `RELATORIO-teste-alianca.md` (raiz).
- **Frota:** 6 instalações em campo com a 2.2 calibrada (selftest 58 PASS em cada; memórias/customizações preservadas).
- **Regra nova — esteira no onboarding (2026-07-03):** bootstrap (`setup`/`adopt`) não fecha sem a esteira de testes armada e **verde** + `alianca/kernel/verify.cmd` apontando pro teste do projeto (existente → esteira completa já; novo → entende primeiro). Encodada em `testing` (§Esteira desde o onboarding), `adopt`, `setup`, `START-HERE §5`, `feedback`. **Trava mecânica no kernel (feita, 62 PASS):** `verify.py` agora bloqueia o "pronto" quando o projeto está em andamento (`active-context.md` existe) mas `verify.cmd` não está armado — `_is_bootstrapped()` + 4 fixtures novas no `selftest`. Permite setup em curso (sem `active-context` ainda) e respeita `[verify:skip]`. "Não pode falhar" fechado ponta a ponta.
- **Regra — gerente por padrão (2026-07-03):** o agente pai só coordena/decide/delega; **toda** execução (mesmo pequena) vai a subagente, o pai não põe a mão no código. Diretriz **sempre-ligada** no `route.py` (LOOP) + invariante reforçado no `START-HERE §5`. **Enforcement é diretriz (soft):** a distinção parent/subagente por campo de hook **não é confirmada** na doc, então hard-block via `PreToolUse` ficou **pendente** (precisa de teste empírico antes). Exceção consciente registrada: infra com risco de recursão/fork-bomb (ex.: o próprio `session_start`).
- **Regra — SessionStart / arranque de conversa (2026-07-03):** conversa **nova** dispara `alianca/kernel/session_start.py` (hook `SessionStart`, `matcher: "startup"`) → roda o selftest (**kernel starta verde**, ou reporta falha) + injeta a diretriz **OBRIGATÓRIA de rodar a X9** como primeiro ato, delegada a subagente. Só em `startup` (não `resume`/`clear`). Trava anti-recursão via env `ALIANCA_SS_NO_SELFTEST`. 64 PASS; e2e provado. Distribuído no `settings.snippet.json`.
- **Saúde da memória (2026-07-02):** a memória nativa do Claude Code operava como fonte concorrente (violava a Regra Zero) e alimentava a alucinação de longo prazo. Memória global **limpa**; os 3 fatos únicos migraram para `feedback.md` (PT-BR + nomes comerciais; arquiteto-não-construtor) e `stack.md` (bug de flash attention da máquina). **Em curso:** desativar a memória nativa de vez + tornar a regra explícita no `adopt` — apontar não basta, ela reenche.

## Insumos pro plugin (não perder)

- **Regra Zero deve DESATIVAR a memória nativa do Claude Code**, não só reescrever o `CLAUDE.md` p/ apontar — senão reenche sozinha e volta a competir. (Correção em andamento neste repo; virar regra distribuída.)
- **Overlay local no update:** projetos customizam arquivos distribuídos (`entrega segura` estendeu `interface.md`; `sacerdotisa` criou `docs-governance.md` + launcher `py`). O update precisa preservar customização fora dos arquivos que substitui — hoje é merge manual.
- **Build/revisão no rótulo:** 3 instalações diziam "2.2" com conteúdo pré-calibração. O índice precisa de identificador de build junto ao `alianca-version`.

## Testes pendentes (bateria noturna)

Pronto pra disparar: `PROXIMOS-TESTES.md` + `tests-bench/run_overnight.sh` (`! bash "tests-bench/run_overnight.sh"`).
- **B+C** (auto): projeto 3-arquivos em 4 condições 2×2 (isola disco vs disciplina-de-prompt) + tokens/ROI — `tests-bench/phase2_overnight.py`.
- **A'** (auto): curva de retenção mais fina, mais reps — `tests-bench/longhorizon.py`.
- **D** (supervisionado, não noturno): kernel real (hooks + subagentes) dirigindo Claude Code numa tarefa longa — falta pra sair de "o princípio funciona" → "o produto funciona".

## Próximos marcos (em ordem)

1. **Dogfood real** — usar a Aliança num projeto de verdade por 2–3 semanas.
2. **Empacotar como plugin do Claude Code** (resolve instalação/update/snippet).
3. **Decisão pendente:** onde a memória vive no projeto-alvo — raiz (`memory/`, VALIDATION.md aprend. 1) vs `alianca/memory/` (START-HERE §5 / route.py). Os docs se contradizem.
