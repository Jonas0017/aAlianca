# x9-state — estado do monitor de pontas soltas

> Memória do modo monitor do `x9` (ver `instructions/x9.md`): registra o que já foi visto, fechado ou **conscientemente adiado**, para a próxima varredura alertar só o delta — sem re-alertar o que já foi decidido.

**Última varredura:** 2026-07-01 (auditoria X9 completa + parecer de arquiteto)

## Fechados nesta rodada (2026-07-01)

- Contagens defasadas ("15/17 instruções", "16 seções") em README, instructions/README e HANDOFF — corrigidas para **18 módulos / 17 seções (§0–§16)**.
- Precedência do PROTOCOL §15.A3 sem `interface` — alinhada ao `router.md`.
- Corte "só se R≥40" como **ativação** do `security` (PROTOCOL §7 e `router.md`) — trocado por "engaja sempre que o gatilho ocorrer; profundidade ∝ risco" (decisão §16.4).
- HANDOFF.md ~7 commits defasado (não conhecia kernel, x9, validação round 2) — reescrito para o estado atual.
- Referência à memória morta "keel" no HANDOFF — removida.
- `CLAUDE.md` da raiz inexistente (a Aliança não aplicava a própria receita de forcing function) — criado.
- `memory/x9-state.md` prometido em `x9.md` (modo monitor) mas nunca criado — este arquivo.
- `memory/active-context.md` do próprio repo inexistente — criado (primeiro dogfood da memória).
- README vendendo "universal" sem ressalva — reposicionado honesto (estrutura `.md` model-agnostic; enforcement determinístico só Claude Code, resto advisory).

## Adiados conscientemente (não re-alertar)

| Ponta solta | Status/decisão | Data |
|---|---|---|
| Dogfood real (usar a Aliança num projeto de verdade, 2–3 semanas) | próximo marco — pendente | 2026-07-01 |
| Adapter determinístico para Cursor / outras ferramentas | roadmap (hoje: modo advisory por prosa) | 2026-07-01 |
| Instalador / plugin do Claude Code | futuro — após dogfood + calibração do roteador | 2026-07-01 |
| Adoção via prosa (instalação manual do snippet, sem instalador) | decisão de design até o plugin existir | 2026-07-01 |
