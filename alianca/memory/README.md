# memory

A **memória segmentada** da Aliança. Proibido um arquivo gigante único — a memória é tratada como código: versionada, refatorada e dividida quando cresce.

A **memória mínima** (`active-context.md` + `stack.md`) existe desde o **Nível 0** — é o que permite retomar o projeto (ver `START-HERE.md §2`). A segmentação (architecture, business-rules, decisions, archive) cresce com o nível.

## Estrutura

| Arquivo/pasta | Conteúdo | A partir do nível |
|---|---|---|
| `active-context.md` | estado de trabalho corrente (o que está em andamento) | 0 |
| `stack.md` | ferramentas e comandos concretos do projeto (runner, lint, CI…) — gerado pelo `setup`; o backbone lê daqui | 0 |
| `vision.md` | o que é o projeto, persona, problema, usuários | 1 |
| `architecture.md` | arquitetura vigente | 2 |
| `business-rules.md` | regras de negócio | 3 |
| `security.md` | postura de segurança | se R ≥ 40 |
| `decisions/` | uma decisão por arquivo (estilo ADR) | 3 |
| `archive/` | conhecimento obsoleto, preservado (nunca apagado) | 3 |

> Em ferramentas com memória nativa (ex.: Claude Code), mapeie para ela em vez de duplicar.
> Vazio nesta Fase 1 — `active-context.md` é criado pelo `setup`, no bootstrap de um projeto real.
