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
- **Benchmark entregabilidade (2026-07-02, Ollama local `qwen2.5-coder:7b`) — 3 testes:**
  - **T1 tarefa curta (tiro único, 5 tarefas × 3 reps):** SEM **9.5** · COM **9.1**. Empate (4/5 em 10/10); a Aliança até perdeu no CPF por autoteste errado sem loop p/ corrigir. **Tiro único não é o jogo.**
  - **T2 longo prazo arquivo único (pressão de contexto, curva de janela):** retenção SEM cai p/ **4/10** quando janela<arquivo (ctx=800); COM **10/10** em todas. No mundo real código>>janela ⇒ esse é o caso padrão.
  - **T3 projeto real 3 arquivos c/ contratos ARBITRÁRIOS (o decisivo, 2 reps):** pressão (janela 1200) → SEM **4/10 integração 0%** (alucina o contrato, `pedido.finalizar` não existe, projeto não monta) · COM **10/10 integração 100%**. Controle (janela 20000) → **empatam 10/10** (prova anti-viés: diferença vem SÓ da pressão de contexto).
  - **Aprendizado central (validado):** o diferencial da Aliança **não** aparece em tarefa curta; aparece no **longo prazo quando o trabalho excede a janela** — estado em disco + recarregar o essencial evita a alucinação de contrato/perda de requisito. Relatórios em `RELATORIO-FINAL-alianca.md`, `RELATORIO-fase1-longo-prazo.md`, `RELATORIO-teste-alianca.md` (raiz). Ver [[ollama-flash-attention-corrompe]].
- **Frota atualizada (2026-07-01):** as 6 instalações em campo (`1 bilhão na conta`, `entrega segura`, `Instrutores`, `sacerdotisa`, `videos gnosis`, `teste de harness`) receberam a 2.2 calibrada — selftest 58 PASS provado em cada destino; memórias/snapshots/customizações preservados.

## Aprendizados da atualização em campo (insumo pro plugin)

- **Projetos customizam arquivos distribuídos**: `entrega segura` estendeu `interface.md` (design tokens RN); `sacerdotisa` criou módulo próprio (`docs-governance.md`) e usa launcher `py` no `verify.cmd`. O mecanismo de update precisa de **overlay local** (customização fora dos arquivos que a atualização substitui) — hoje foi merge manual por agente.
- **Rótulo de versão não reflete o conteúdo**: 3 instalações diziam "2.2" com conteúdo pré-calibração ou pré-kernel. O `router.md`/índice precisa de um identificador de build/revisão junto ao `alianca-version`.

## Testes pendentes (bateria noturna — rodar sem estressar a máquina de dia)

- **Preparado e pronto para disparar:** `PROXIMOS-TESTES.md` (raiz) + `tests-bench/run_overnight.sh`. Comando: `! bash "tests-bench/run_overnight.sh"`.
- **Teste B+C (automático):** projeto 3-arquivos em 4 condições 2×2 (isola mecanismo-de-disco vs disciplina-de-prompt) + mede tokens (ROI). Script `tests-bench/phase2_overnight.py`.
- **Teste A' (automático):** curva de retenção mais fina, mais reps. Script `tests-bench/longhorizon.py`.
- **Teste D (supervisionado, NÃO noturno):** kernel real (hooks + subagentes) dirigindo Claude Code numa tarefa longa — falta para sair de "o princípio funciona" para "o produto funciona".

## Próximos marcos (em ordem)

1. **Dogfood real** — usar a Aliança para construir um projeto de verdade por 2–3 semanas.
2. **Empacotar como plugin do Claude Code** (resolve instalação/update/snippet).
3. **Decisão pendente do usuário:** onde a memória vive no projeto-alvo — raiz (`memory/`, como diz VALIDATION.md aprendizado 1) ou `alianca/memory/` (como dizem START-HERE §5 e route.py). Hoje os docs se contradizem.
