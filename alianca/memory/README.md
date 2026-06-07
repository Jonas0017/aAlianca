# memory

A **memória segmentada** da Aliança. Proibido um arquivo gigante único — a memória é tratada como código: versionada, refatorada e dividida quando cresce.

## Estrutura

| Arquivo/pasta | Conteúdo | A partir do nível |
|---|---|---|
| `vision.md` | o que é o projeto, persona, problema, usuários | 1 |
| `active-context.md` | estado de trabalho corrente (o que está em andamento) | 1 |
| `architecture.md` | arquitetura vigente | 2 |
| `business-rules.md` | regras de negócio | 3 |
| `security.md` | postura de segurança | se R ≥ 40 |
| `decisions/` | uma decisão por arquivo (estilo ADR) | 3 |
| `archive/` | conhecimento obsoleto, preservado (nunca apagado) | 3 |

> Em ferramentas com memória nativa (ex.: Claude Code), mapeie para ela em vez de duplicar.
> Vazio nesta Fase 1 — `active-context.md` é criado pelo `setup`, no bootstrap de um projeto real.
