# memory

A **memória segmentada** da Aliança. Proibido um arquivo gigante único — a memória é tratada como código: versionada, refatorada e dividida quando cresce.

A **memória mínima** (`active-context.md` + `stack.md`) existe desde o **Nível 0** — é o que permite retomar o projeto (ver `START-HERE.md §2`). A segmentação (architecture, business-rules, decisions, archive) cresce com o nível.

> **Fonte única (invariante):** esta pasta é a **única** memória de projeto ativa. Nunca opere com duas em paralelo. Ao adotar um projeto existente (ver `adopt`), o conhecimento antigo é acolhido aqui e o container antigo vai para `archive/`; a memória nativa da ferramenta (ex.: Claude Code) **aponta** para cá em vez de duplicar estado de projeto.

> Este README descreve a **estrutura** e a **operação** da memória; o mapa completo Nível→artefatos é o do `setup` (Passo 5). Os momentos de mexer na memória são disparados pelo `health-check` (audita tamanho/duplicação) e pelo `snapshot`/marco (consolida).

## Estrutura

| Arquivo/pasta | Conteúdo | A partir do nível |
|---|---|---|
| `active-context.md` | estado de trabalho corrente (o que está em andamento) | 0 |
| `stack.md` | ferramentas e comandos concretos do projeto (runner, lint, CI…) — gerado pelo `setup`; o backbone lê daqui | 0 |
| `vision.md` | o que é o projeto, persona, problema, usuários | 1 |
| `feedback.md` | aprendizado do projeto: erro recorrente → regra ("aqui sempre erramos X → faça Y") | qualquer (sob demanda) |
| `questions/` | perguntas sobre o projeto, agrupadas por tópico (um arquivo por assunto, cruzados por link); estados aberta/respondida — ver instrução `questions` | qualquer (sob demanda) |
| `architecture.md` | arquitetura vigente | 2 |
| `business-rules.md` | regras de negócio | 3 |
| `security.md` | postura de segurança | se R ≥ 40 |
| `decisions/` | uma decisão por arquivo (estilo ADR) | 3 |
| `archive/` | conhecimento obsoleto, preservado (nunca apagado) | 3 |

## Operação — quando mexer na memória

A memória é tratada como código: dividida quando cresce, consolidada nos marcos, nunca apagada. Um `memory.md` gigante é proibido — apodrece e ninguém relê.

- **Quebrar um documento:** passou de um tamanho de leitura confortável (não cabe numa leitura rápida, ou mistura assuntos distintos) → divida por responsabilidade, o mesmo critério da `architecture`.
- **Consolidar:** ao fechar um marco, funda anotações soltas no documento certo e remova o ruído; duplicação entre arquivos → eleja uma fonte da verdade, as outras apontam para ela.
- **Arquivar (nunca apagar):** conhecimento obsoleto vai para `archive/`, preservado e fora do caminho. Regra que virou hábito também migra para lá.

## feedback.md — o harness aprende com o próprio projeto

Quando um erro **se repete** neste projeto (o agente erra a mesma coisa duas vezes, ou o usuário corrige o mesmo ponto), registre a lição como uma regra curta e acionável — não o episódio. O `code-quality` e o `health-check` consultam este arquivo para não repetir o erro. Formato:

```
- [AAAA-MM-DD] Sintoma recorrente: <o que deu errado>. Regra: <o que fazer a partir de agora>.
```

Mantenha enxuto: regra que virou hábito ou ficou obsoleta migra para `archive/`. É genérico por natureza — serve a qualquer stack, persona ou nível.

> Em ferramentas com memória nativa (ex.: Claude Code), mapeie para ela em vez de duplicar.
> Vazio nesta Fase 1 — `active-context.md` é criado pelo `setup`, no bootstrap de um projeto real.
