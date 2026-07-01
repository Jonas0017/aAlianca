# active-context — desenvolvimento da Aliança

> Estado de trabalho corrente deste repo. Atualize a cada marco (loop do `START-HERE §4`, passo PERSISTIR).

## Projeto

Desenvolvimento da **Aliança 2.2** — o próprio harness. Este repo é o produto; a pasta `alianca/` é a implementação de referência que os projetos-alvo copiam.

## Estado (2026-07-01)

- **Kernel operacional** — 3 portões determinísticos (Claude Code): `route.py` (UserPromptSubmit), `gate.py` (PreToolUse), `verify.py` (Stop) + `klog`/`kernel.log` + `selftest.py` (58 PASS) + `compile.py` (gera `router.index.json` com grafo `pulls`).
- **Portão PERSISTIR ligado** — o `verify.py` (Stop) agora cobra atualização de `memory/active-context.md` em turnos com escrita substancial (5/5 passos do loop com enforcement).
- **Roteador calibrado (2026-07-01)** — keywords curadas nos 10 módulos que derivavam do trigger + força mínima 2 para keywords derivadas; falsos positivos reais desta rodada zerados (verificado com prompts-fixture no selftest).
- **18 instruções prontas**, incluindo `tasks`, `questions` e `x9` (auditoria de pontas soltas).
- **Auditoria X9 + parecer de arquiteto concluídos em 2026-07-01**; correções aplicadas (contagens, precedência com `interface`, fim do corte R≥40 como ativação, reposicionamento honesto "Claude Code first", HANDOFF atualizado, CLAUDE.md da raiz criado). Detalhe em `x9-state.md`.
- **Validação:** 2 rounds em `VALIDATION.md` (A/B Claude+Copilot · kernel+Ollama local).

## Próximos marcos (em ordem)

1. **Dogfood real** — usar a Aliança para construir um projeto de verdade por 2–3 semanas.
2. **Empacotar como plugin do Claude Code** (resolve instalação/update/snippet).
3. **Decisão pendente do usuário:** onde a memória vive no projeto-alvo — raiz (`memory/`, como diz VALIDATION.md aprendizado 1) ou `alianca/memory/` (como dizem START-HERE §5 e route.py). Hoje os docs se contradizem.
