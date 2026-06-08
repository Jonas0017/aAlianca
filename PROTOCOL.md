# Aliança — Harness Adaptativo Universal

> **O elo que liga os dois mundos.**
> Plataforma que gera o harness ideal para cada projeto, persona e stack — usável por qualquer LLM em conjunto com outras ferramentas.
> **Versão:** 2.1 (rascunho) · substitui o conceito "APBP" v1 · Arquitetura de marca em §14.
>
> **2.0 → 2.1:** removido o conceito de *stack packs* (pasta `stacks/`). Sugerir ferramentas é trabalho da LLM, não do harness — qualquer modelo já conhece as opções, e um catálogo `.md` só inflaria o contexto e apodreceria. A escolha agora é **decidida no `setup`** e **registrada por projeto** em `memory/stack.md` (genérico, adapta-se ao projeto do dev final). Ver §15.B1.

---

## 0. O que mudou da v1 para a v2

A v1 (APBP) era um bom esqueleto, mas tratava o harness como **um produto único** dimensionado por **um número só**. A v2 reposiciona o conceito:

| v1 (APBP) | v2 (Aliança) |
|---|---|
| Um harness, dimensionado por nível | Um **gerador** de harness; produz harnesses diferentes por persona e stack |
| Índice de complexidade único (0–100) sem fórmula | **Três eixos** (Estrutura, Longevidade, Risco) com **rubrica explícita** |
| Questionário fixo de 23 perguntas | **Questionário progressivo e adaptado à persona** (leigo vs dev) |
| Instruções despejadas no contexto | **Módulos just-in-time** carregados por gatilho ("no momento exato") |
| Política de contexto por % da janela (não observável) | Política por **eventos e artefatos** (observáveis) |
| Multiagente fixo de 8 papéis | Multiagente **atrelado ao nível** |
| Reinventa estrutura | **Usa primitivas existentes** da ferramenta-alvo via adapters |

---

## 1. Princípios Fundamentais

1. **Persona primeiro.** Antes de qualquer pergunta de projeto, a Aliança descobre *com quem está falando*. As perguntas, a linguagem, o nível de automação e a própria estrutura gerada dependem disso.
2. **Dimensionamento multi-eixo.** Complexidade não é um escalar. Estrutura, Longevidade e Risco são medidos separadamente — um script de pagamentos é estruturalmente simples mas de alto risco, e o harness precisa refletir os dois.
3. **Backbone de qualidade inegociável.** Todo projeto, em qualquer nível, recebe instruções de testes, qualidade de código, refatoração e prevenção de bugs — *dimensionadas* ao nível, nunca ausentes.
4. **Just-in-time.** O harness não carrega tudo de uma vez. Mantém um índice enxuto e **busca o módulo de instrução certo no momento exato** (por gatilho). Contexto fica leve; capacidade fica profunda.
5. **Artefatos, não percentuais.** O agente controla arquivos (memória, snapshots, tarefas), não a porcentagem da própria janela de contexto. A política de continuidade é baseada em eventos observáveis.
6. **Usa o que já existe.** O Aliança é model-agnostic, mas em cada ferramenta-alvo (Claude Code, Cursor, etc.) ele mapeia para as primitivas nativas (skills, memória, subagents) em vez de competir com elas.

---

## 2. Camada 1 — Detecção de Persona

A **primeira** interação determina a persona. Não se pergunta a stack a quem nunca programou.

### Personas-base

| Persona | Sinais | Estilo de pergunta | Harness gerado |
|---|---|---|---|
| **P0 — Leigo** | "nunca programei", descreve o produto, não a tecnologia | Linguagem natural, zero jargão, uma pergunta por vez | Máxima automação; LLM decide a stack; arquivos que o humano lê são em linguagem simples; testes/qualidade rodam por baixo dos panos |
| **P1 — Iniciante** | sabe o básico, hesita em arquitetura | Guiado, com explicações curtas do "porquê" | Automação alta com pontos de decisão explicados; defaults seguros |
| **P2 — Dev experiente** | fala em stack, padrões, trade-offs | Direto, técnico, denso | Controle total; integra com ferramentas existentes; assume que o dev gerencia config |
| **P3 — Time/Org** | múltiplos devs, compliance, escala | Técnico + governança | Estrutura completa: governança, auditoria, múltiplos agentes, RBAC de conhecimento |

### Regra de detecção

A pergunta de abertura é **única e neutra**, e a resposta classifica a persona:

> "Me conta em uma frase o que você quer construir — do jeito que você falaria pra um amigo."

- Descreve **produto/problema** sem termos técnicos → P0/P1.
- Cita **stack, arquitetura, requisitos não-funcionais** → P2/P3.
- Menciona **time, clientes, compliance** → P3.

A persona pode ser **promovida** durante o projeto (um leigo aprende; um protótipo vira produto). A promoção dispara reavaliação do nível (ver §11).

---

## 3. Camada 2 — Questionário Progressivo

Substitui o bloco fixo de 23 perguntas. **Triagem curta primeiro; aprofundamento só se necessário.**

### Fase A — Triagem (todas as personas, máx. 5 perguntas)

Traduzida para a linguagem da persona. Cada pergunta alimenta um eixo (§4).

1. **O que é** e **que problema resolve**. *(contexto)*
2. **Quem usa.** *(contexto)*
3. **Quanto tempo precisa durar** — teste/descartável, alguns meses, ou anos? *(eixo Longevidade)*
4. **Vai guardar/usar dados de pessoas, dinheiro, ou algo sigiloso?** *(eixo Risco)*
5. **É uma coisa só, ou várias partes que conversam?** *(eixo Estrutura)*

> Para P0, a pergunta 5 vira: *"É um site/app simples, ou tem várias telas e um 'cérebro' que guarda informação?"*

### Fase B — Aprofundamento condicional

Disparado **apenas** quando a triagem indica nível ≥ 2 em algum eixo. Carregado como **módulo just-in-time** (§7), não fica no prompt base.

- **Se Estrutura ≥ 2:** módulos, integrações, persistência, frontend/backend/mobile/infra.
- **Se Risco ≥ 2:** autenticação, pagamentos, dados pessoais (LGPD/GDPR), requisitos regulatórios, ameaças.
- **Se Longevidade ≥ 2:** versionamento, evolução esperada, crescimento de equipe/documentação.
- **Se P2/P3:** stack, padrões arquiteturais, CI/CD, ferramentas já em uso.

---

## 4. Camada 3 — Dimensionamento Multi-Eixo (a rubrica)

O furo nº1 da v1 era "calcule um índice" sem fórmula. Aqui está a fórmula.

Três eixos, cada um pontuado **0–100**. **Não se somam num número só** — combinam-se por matriz (§5).

### Eixo E — Estrutura (tamanho/complexidade do sistema)

| Fator | 0 | +pontos |
|---|---|---|
| Nº de módulos/serviços | 1 | 2–3: +15 · 4–6: +30 · 7+: +45 |
| Camadas presentes (front, back, mobile, infra) | nenhuma além de 1 | +10 por camada adicional (máx +30) |
| Integrações externas | nenhuma | 1–2: +5 · 3–5: +12 · 6+: +20 |
| Persistência | nenhuma | simples (arquivo/KV): +2 · relacional: +6 · distribuída: +10 |

### Eixo L — Longevidade (tempo de vida e evolução)

| Resposta | Pontos |
|---|---|
| Descartável / teste de um dia | 0–15 |
| Semanas (MVP/protótipo) | 16–40 |
| Meses (produto em evolução) | 41–70 |
| Anos / múltiplas versões / manutenção contínua | 71–100 |

### Eixo R — Risco (sensibilidade, segurança, compliance)

| Fator | Pontos |
|---|---|
| Sem dados sensíveis, sem auth | 0–15 |
| Autenticação de usuários | +25 |
| Dados pessoais (LGPD/GDPR) | +25 |
| Pagamentos / dados financeiros | +30 |
| Requisito regulatório explícito (saúde, fintech, gov) | +35 |

> R é **clampeado em 100**. Qualquer sinal sensível **engaja a segurança** — proporcional ao risco (base para login/dados; profundo para pagamento/regulado), nunca dependente de E ou L. R alto **sugere** subir o nível (ver §5).

---

## 5. Camada 4 — Mapa de Níveis e Matriz

O **Nível do Harness** (0–4) vem da combinação dos eixos, não de uma soma.

```
Nível base = faixa de  max(E, L)        // tamanho e tempo definem a "espinha"
Ajuste de risco        = R alto sugere +1 nível (cap 4); qualquer sinal sensível engaja segurança (proporcional)
```

> O nível é uma **estimativa inicial**, revisada continuamente pelo comportamento real do projeto (ver §12 e a instrução `migration`) — sobe ou rebaixa. Não é um veredito do questionário.

| max(E, L) | Nível base |
|---|---|
| 0–20 | 0 |
| 21–40 | 1 |
| 41–60 | 2 |
| 61–80 | 3 |
| 81–100 | 4 |

### O que cada nível gera

> **Fonte operacional desta tabela:** `alianca/instructions/setup.md` (Passo 5). Ao mudar o que um nível gera, atualize lá primeiro e espelhe aqui.

> Em **todos** os níveis, o Backbone de Qualidade (§6) está presente — só muda a profundidade.

- **Nível 0 — Mínimo**
  `README.md`, `TASKS.md` + memória mínima (`memory/active-context.md`, `memory/stack.md`). Backbone em modo "automático invisível" (testes e lint configurados, rodando sem o usuário gerenciar). Ideal para P0/landing/script.

- **Nível 1 — Leve**
  `README.md`, `TASKS.md`, `ARCHITECTURE.md` + `memory/vision.md`. Backbone explícito mas simples.

- **Nível 2 — Estruturado**
  `/docs` (`requirements.md`, `architecture.md`), `/tasks` (`backlog.md`), `/tests`, `memory/` segmentada começa (`architecture.md`). Backbone com CI básico.

- **Nível 3 — Robusto**
  `/docs` (`requirements`, `architecture`), `/tasks`, `/tests`, `/memory` segmentada (`business-rules`, `security` se R≥40, `decisions/`, `archive/`). Backbone com pipeline completo. Multiagente opcional.

- **Nível 4 — Plataforma/Org**
  `/docs`, `/memory`, `/agents`, `/workflows`, `/tests`, `/security`, `/audits`, `/metrics`, `/governance`. Multiagente completo. Snapshots periódicos. Governança de conhecimento.

### Gatilhos de migração (o que faltava na v1)

Promover de nível quando **qualquer** condição cruza:

| De → Para | Gatilho |
|---|---|
| 0 → 1 | > 1 arquivo de código com lógica não-trivial, ou expectativa de retomada futura |
| 1 → 2 | ≥ 3 módulos, ou ≥ 2 devs, ou primeira integração externa |
| 2 → 3 | ≥ 6 módulos, ou dados pessoais/auth introduzidos, ou memória segmentada além da mínima (`active-context` + `stack`) |
| 3 → 4 | múltiplos times, compliance regulatório, ou ≥ 3 agentes especializados ativos |

Rebaixar (simplificar) quando a complexidade real cai e a estrutura está ociosa — a Aliança **arquiva** o excedente, não apaga.

---

## 6. Camada 5 — Backbone de Qualidade Universal

**Inegociável em todo projeto.** Entra como instrução no bootstrap. O que muda por nível é a *profundidade*, nunca a *presença*.

| Pilar | Nível 0–1 | Nível 2–3 | Nível 4 |
|---|---|---|---|
| **Esteira de testes** | smoke test mínimo, roda local | unit + integração, CI on push | + e2e, cobertura mínima exigida, testes de carga/segurança |
| **Qualidade de código** | formatter + linter com defaults | regras de projeto, pre-commit | + gates de PR, análise estática, complexidade ciclomática |
| **Refatoração** | gatilho: "duplicou 3x → extraia" | revisão de débito por marco | orçamento de débito técnico rastreado em `/metrics` |
| **Prevenção de bugs** | tipos quando a stack permite, guard clauses | code review obrigatório, contratos | + property-based tests, fuzzing onde aplicável |
| **Arquitetura** | estrutura plana e óbvia, sem camadas cerimoniais | fronteiras de módulo explícitas, ADRs em `decisions/` | arquitetura governada, revisão por marco |

Cada pilar é um **módulo just-in-time** (§7): a instrução completa só é carregada quando o gatilho ocorre (ex.: o módulo de refatoração só entra no contexto quando o agente detecta duplicação).

---

## 7. Camada 6 — Sistema de Módulos Just-in-Time (o "no momento exato")

O coração da v2. Em vez de um prompt gigante, a Aliança mantém **módulos de instrução** indexados por gatilho. O agente lê só o **índice** por padrão e **puxa o módulo** quando o gatilho dispara.

### Estrutura

```
/alianca
  START-HERE.md      # ponto de entrada: o LLM lê primeiro
  router.md          # índice enxuto: lista de instruções + gatilho de cada uma
  /instructions
    setup.md         # gatilho: "iniciar projeto novo"
    testing.md       # gatilho: "ao criar/alterar lógica testável"
    refactor.md      # gatilho: "ao detectar duplicação ou função > N linhas"
    code-quality.md  # gatilho: "antes de commit / em PR"
    security.md      # gatilho: "ao tocar auth, dados pessoais ou pagamento"  (só se R≥40)
    persona-p0.md    # gatilho: "usuário classificado como leigo"
    deep-questions.md# gatilho: "triagem indicou eixo ≥ 2"
    ...
  /memory   /snapshots
```

### Contrato de um módulo

Cada módulo declara, no topo:

```
---
trigger: <condição observável que faz o agente carregar este módulo>
load-when: <fase do ciclo: bootstrap | execução | review | migração>
applies-to: <personas/níveis aplicáveis>
---
<instruções completas>
```

### Como o roteador funciona (model-agnostic)

- O `router.md` contém **só** nome + trigger de cada módulo (poucos tokens).
- O agente, a cada ação, verifica se algum trigger casa; se sim, carrega aquele módulo antes de agir.
- **Mapeamento por ferramenta:**
  - *Claude Code:* cada módulo vira uma **skill** (o campo `trigger` é a linha TRIGGER da skill); o roteamento é nativo.
  - *Cursor / outros:* `router.md` é incluído no system prompt; os módulos ficam em arquivos lidos sob demanda via tool de leitura.
  - *Genérico:* qualquer LLM com leitura de arquivos consegue seguir o `router.md`.

Isso é o que te dá "buscar cada coisa no momento exato" sem inchar o contexto.

---

## 8. Camada 7 — Memória Segmentada

Proibido `memory.md` gigante (regra mantida da v1). Uma **memória mínima** (`active-context.md` + `stack.md`) existe desde o **Nível 0** — é o que torna o projeto retomável (§2/`START-HERE`). A estrutura **segmentada** abaixo cresce a partir do Nível 2-3:

```
/memory
  active-context.md    # estado de trabalho corrente (desde o Nível 0)
  stack.md             # ferramentas e comandos do projeto (desde o Nível 0)
  vision.md
  feedback.md          # aprendizado: erro recorrente → regra (sob demanda)
  architecture.md
  business-rules.md
  security.md          # se R ≥ 40
  /decisions           # um arquivo por decisão (ADR-style)
  /archive             # conhecimento obsoleto, preservado
```

**Memória é tratada como código:** versionada, refatorada, dividida quando cresce demais. Em ferramentas com sistema de memória nativo (ex.: Claude Code), a Aliança mapeia para ele em vez de duplicar.

> Operação (quando quebrar, consolidar, arquivar) documentada em `memory/README.md`; os momentos são disparados por `health-check` (audita) e `snapshot`/marco (consolida).

---

## 9. Camada 8 — Política de Contexto (reformulada)

A v1 amarrava ações a percentuais da janela (50/65/80/85/90%) que o agente **não consegue medir de forma confiável**, e que ferramentas como o Claude Code já compactam sozinhas. A v2 troca por **eventos observáveis**:

| Evento observável | Ação |
|---|---|
| Antes de iniciar uma tarefa grande/multi-etapa | Gerar/atualizar snapshot (§10) |
| Ao concluir um marco | Consolidar memória; arquivar o que ficou obsoleto |
| Quando um documento ultrapassa um tamanho de leitura confortável | Refatorar/dividir o documento |
| Quando a ferramenta sinaliza compactação iminente | Persistir estado em `active-context.md` antes de perder histórico |
| Handoff entre agentes | Passar **resumo**, nunca histórico completo |

Princípio: o agente não tenta administrar a janela; ele garante que **o estado essencial vive em disco**, então qualquer compactação/nova sessão é recuperável.

---

## 10. Camada 9 — Snapshots

Snapshot = documento autocontido que permite reiniciar uma sessão **sem depender do histórico**. Contém:

- Estado atual e o que está em andamento.
- Arquitetura vigente (resumo).
- Decisões vigentes (ponteiros para `/decisions`).
- Tarefas abertas.
- Próximos passos concretos.

A partir do Nível 3, snapshots são periódicos; no Nível 4, automáticos por marco.

---

## 11. Camada 10 — Sistema Multiagente (atrelado ao nível)

Não é um time fixo de 8. Escala com o nível:

| Nível | Agentes |
|---|---|
| 0–1 | Nenhum especializado (um agente faz tudo) |
| 2 | Opcional: separar QA/Documentação sob demanda |
| 3 | Architect, Backend, Frontend, QA conforme a stack |
| 4 | Time completo: coordinator, Architect, Backend, Frontend, QA, Security, Documentation, DevOps |

**Regras invariantes (mantidas da v1):**
- O **coordinator** coordena, nunca executa tarefa técnica.
- O **coordinator** consome **apenas resumos** dos especialistas, nunca histórico completo.
- *Mapeamento:* em Claude Code, especialistas = subagents (tool Agent); o resumo retornado é o handoff.

> Operacionalizado na instrução `agents` (quando dividir o trabalho e como o coordinator faz o handoff).

---

## 12. Camada 11 — Evolução Automática do Harness

O Aliança monitora sinais e **propõe** mudanças estruturais (com gatilhos concretos, §5):

- Cresceu (mais módulos/integrações/agentes/docs) → propõe subir de nível e criar estruturas.
- Encolheu (estrutura ociosa) → propõe simplificar e arquivar.
- Documento grande demais → propõe refatorar/dividir.
- Memória fragmentada/duplicada → propõe consolidar.

O harness é tratado como **sistema vivo**: a cada marco, a Aliança reavalia persona, eixos e nível.

---

## 13. Mapeamento para ferramentas (model-agnostic + adapters)

| Conceita Aliança | Claude Code | Cursor / genérico |
|---|---|---|
| Instrução just-in-time | Skill (com TRIGGER) | Arquivo em `/alianca/instructions` + `router.md` no prompt |
| Especialista | Subagent (tool Agent) | Sessão/role separada com prompt dedicado |
| Memória | Sistema de memória nativo | `/memory` em disco |
| Backbone | Skills de testing/quality/refactor | Mesmos módulos via router |
| Snapshot | Arquivo em `/memory` ou nativo | Arquivo `SNAPSHOT.md` |

---

## 14. Nomenclatura e edições

**Produto:** **Aliança** — *Slogan:* "o elo que liga os dois mundos."

**Princípio de nomes:** os componentes usam **termos simples e convencionais** que todo dev já entende, sem jargão temático. Nome óbvio > nome poético — reduz carga cognitiva e elimina jargão imposto ao leigo (P0).

### Componentes (nomes simples)

| Componente | Nome | É |
|---|---|---|
| Entrada | `START-HERE.md` | o que o LLM lê primeiro |
| Roteador just-in-time | `router.md` | índice de instruções + gatilhos |
| Módulos de instrução | `instructions/` | cada arquivo é uma instrução carregada por gatilho |
| Bootstrap / questionário | `setup` (instrução) | dimensiona o projeto |
| Memória segmentada | `memory/` | conhecimento preservado e versionado |
| Snapshots | `snapshots/` | pontos de retomada |
| Stack do projeto | `memory/stack.md` | ferramentas e comandos concretos, decididos no `setup` e registrados por projeto |
| Agentes especializados | **agents** | os especialistas |
| Agente gerente | **coordinator** | coordena os agents; consome só resumos |
| Autovalidação | **health-check** | saúde do harness |

### Edições por persona/escala (expansão comercial)

Mapeia direto sobre as personas (§2) e dá uma trilha de crescimento:

| Edição | Persona | Promessa |
|---|---|---|
| **Aliança Start** | P0/P1 (leigo, iniciante) | máxima automação, linguagem humana, "do zero ao no ar" |
| **Aliança Pro** | P2 (dev experiente) | controle total, integra com suas ferramentas |
| **Aliança Org** | P3 (time/empresa) | governança, auditoria, múltiplos agents, compliance |

Um projeto **sobe de edição** conforme persona/nível evoluem (mesma mecânica de migração do §5) — sem recomeçar.

### Expansão

- Nova instrução → mais um arquivo em `instructions/` + uma linha no `router.md`.
- Nova stack → a LLM decide e registra em `memory/stack.md` do projeto; nada muda na Aliança.
- Novo especialista → mais um agent.
- Novo público → nova edição.

---

## 15. Melhorias propostas (curadoria do arquiteto)

Ideias que não estavam no escopo original mas que, na minha avaliação, são o que separa um "gerador de pastas" de um harness que realmente reduz risco de alucinação, retrabalho e perda de contexto. Agrupadas por objetivo.

> **Status:** ✅ implementado · ⏳ parcial · ✂️ ajustado/descartado. Itens sem marca explícita também já estão refletidos nas instruções.

### A. Robustez do próprio harness

- **A1. Versionamento + migração da Aliança.** ✅ *Implementado:* `alianca-version` no `router.md` + procedimento de migração de versão na instrução `migration` (aditivo, arquiva o obsoleto, valida com `health-check`). Projetos antigos migram sem quebrar.
- **A2. health-check (autovalidação).** Um check que o agente roda periodicamente: o `router.md` aponta para módulos que existem? Há memória duplicada ou inchada? Algum doc passou do tamanho saudável? Testes estão verdes? O nível declarado bate com os eixos reais? Retorna um relatório de saúde acionável.
- **A3. Precedência entre módulos.** ✅ *Implementado* no `router.md`: ordem declarada `security > bug-prevention > testing > architecture > refactor > code-quality`; os módulos de ciclo de vida ficam fora dela. (Estilo/formatação não é módulo — é o piso do `code-quality`.)
- **A4. Recuperação de desastre.** ✅ *Implementado* no `snapshot` (seção "Recuperação de desastre"): reconstruir o estado a partir do último snapshot + `memory/decisions/` + código/histórico, validar com `health-check`. Snapshot não serve de nada se ninguém sabe restaurar a partir dele.

### B. Concretude (tirar do abstrato)

- **B1. Stack registrada por projeto (não "stack packs").** O backbone (testes/qualidade/refac) é abstrato até ser amarrado a comandos concretos — mas esse vínculo **não** se faz com catálogos pré-escritos na Aliança. Sugerir ferramenta é trabalho da **LLM**: qualquer modelo já sabe "site → framework web, API → framework backend", e um `.md` congelado seria redundante, inflaria o contexto (viola o Princípio 4) e apodreceria a cada release de ferramenta. O que **é** do harness: garantir que a LLM (a) **decida** a stack no `setup` (P0/P1 → ela escolhe e justifica simples; P2/P3 → respeita a do dev) e (b) **registre** a escolha em `memory/stack.md` — fonte da verdade, por projeto, que `testing`/`code-quality` leem. Assim o estado vive em disco (Princípio 5), sobrevive a troca de sessão/modelo, e cada projeto recebe ferramentas sob medida sem a Aliança carregar enciclopédia alguma.
- **B2. Definition of Done por tarefa.** ✅ *Implementado* no `setup` (molde de `TASKS.md`: cada tarefa carrega um contrato de conclusão — testes verdes, lint limpo, docs/memória atualizados). Fecha a porta para "terminei" sem verificação.
- **B3. Separação de ambientes.** ✅ *Implementado* no `security` (dev/stage/prod e gestão de segredos por ambiente a partir do Nível 2).
- **B4. Convenções de controle de versão por nível.** ✅ *Implementado* no `setup` (Passo 7): Nível 0 git opcional; Nível 1+ repositório no bootstrap, `.gitignore` da stack, commits pequenos e descritivos; Nível 2+ mensagem padronizada e commit que não quebra o build; Nível 3+ estratégia de branches.

### C. Confiabilidade do agente (anti-alucinação)

- **C1. Rituais de verificação.** Regra dura no backbone: nunca declarar algo pronto sem executar/observar; citar o arquivo/linha ao afirmar fatos sobre o código; rodar teste antes de marcar tarefa concluída.
- **C2. Ponto de entrada único (`START-HERE.md`).** Um arquivo que *qualquer* LLM ou humano lê primeiro e se orienta sozinho: o que é o projeto, persona, nível, onde está a memória, onde está o router, qual o próximo passo. Essencial para algo model-agnostic e multi-sessão — é o que permite trocar de ferramenta/modelo sem perder o fio.
- **C3. Loop de feedback / aprendizado por projeto.** ✅ *Implementado:* erros recorrentes viram regras em `memory/feedback.md` ("aqui sempre erramos X; faça Y"), consultadas pelo `code-quality` e revisadas pelo `health-check`. O harness melhora ao longo do projeto, não só entre projetos.

### D. Saúde e observabilidade

- **D1. Health Score do harness.** Métrica composta (recuperabilidade de contexto, frescor da memória, cobertura de teste, defasagem de docs) exibida no health-check. Transforma "saúde do contexto" da v1, que era vaga, em algo medível.
- **D2. Orçamento de contexto por módulo.** ✂️ *Ajustado:* um orçamento numérico por módulo apodreceria e contraria "carregue o mínimo". Em vez de números, o `router.md` prioriza por **precedência** e instrui a carregar uma instrução por vez quando o contexto aperta — custo qualitativo, não tabela de tokens.
- **D3. Observabilidade do produto.** ✅ *Implementado* no `bug-prevention` (logging estruturado e rastreio de erro a partir do Nível 3).

### E. Segurança do próprio harness

- **E1. Gestão de segredos por padrão.** `.gitignore` com segredos, `.env.example`, regra "nunca commitar credencial" — embutido desde o Nível 1. Um harness "base para todos os devs" que vaza segredo por default é um desastre em escala.
- **E2. Higiene de dependências** (lockfile, checagem de licença/vulnerabilidade) a partir do Nível 2.

### F. Experiência do leigo (P0)

- **F1. Relatórios em linguagem humana.** A cada sessão, o P0 recebe um resumo do tipo "o que foi feito / o que falta / o que preciso de você" — zero jargão. É o que mantém um não-programador no controle.
- **F2. Bootstrap reversível (dry-run).** Antes de criar arquivos, mostrar a estrutura proposta e pedir confirmação; permitir desfazer. Reduz o medo do leigo e o retrabalho do dev.

---

## 16. Decisões em aberto (a resolver com o usuário)

1. ~~Nome definitivo~~ → **resolvido: Aliança**, slogan "o elo que liga os dois mundos" (§14).
2. ~~Idioma dos artefatos gerados~~ → **resolvido: seguem o idioma do usuário** — a LLM já faz isso naturalmente, então o harness não instrui nada a respeito (evita carregar o que o modelo já sabe).
3. ~~Formato de entrega da Aliança~~ → **resolvido: pasta-referência em `.md` puro** (model-agnostic; adapters por ferramenta no §13).
4. ~~Calibração da rubrica~~ → **encaminhada:** o nível do `setup` é estimativa inicial; o harness observa o comportamento real e reajusta (sobe/rebaixa) via `migration`/`health-check`. Segurança é **proporcional ao risco**, não um corte em R≥40. Pesos finos seguem evoluindo no uso real.
5. ~~P0: até onde automatizar~~ → **resolvido:** o LLM decide o técnico reversível, mas **confirma cada decisão estrutural** em linguagem do leigo — e pergunta melhor em vez de assumir. O leigo sabe o que quer; sair fazendo sem perguntar é o jeito mais fácil de errar.
```
