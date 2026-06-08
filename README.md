# Aliança — Harness Adaptativo Universal para LLMs

> **O elo que liga os dois mundos.**
> A Aliança é um **gerador de harness** adaptativo e **model-agnostic**: uma pasta-referência em Markdown puro que dá a qualquer LLM (Claude, GPT, Gemini, Llama…) a estrutura, a memória e o processo certos para trabalhar em **qualquer projeto**, com baixo risco de alucinação, retrabalho, perda de contexto e dívida técnica.

*A harness/scaffolding for AI coding agents — model-agnostic, Markdown-only. It adapts to the person (beginner → team), to the project's lifespan and risk, and loads instructions just-in-time. Works with Claude Code, Cursor, or any file-reading LLM.*

---

## Por que existe

Um LLM trabalhando sozinho num projeto **esquece o contexto, refaz o que já estava pronto, inventa fatos sobre o código e acumula dívida técnica**. As soluções comuns ou despejam um prompt gigante (que incha o contexto e apodrece), ou são rígidas demais para servir do script de um dia ao sistema de uma empresa.

A Aliança resolve isso sendo um **arquiteto, não um construtor**: ela não entrega a casa pronta — ela **dimensiona o projeto, decide as ferramentas, diz como fazer e mantém o estado em disco**, carregando só a instrução certa no momento exato.

## Princípios inegociáveis

- **Processo, invariantes e gatilhos — nunca enciclopédia.** O harness não carrega o que a LLM já sabe; carrega o que ela precisa *fazer* e *quando*.
- **Adaptável a qualquer projeto e qualquer dev.** Do script descartável ao sistema de uma org; do leigo (P0) ao time/empresa (P3).
- **Menos é mais.** Poucas peças, cada uma completa, suficientes para compor a obra — sem redundância.
- **Estado vive em disco** (`memory/` + `snapshots/`), não em % de contexto.
- **Just-in-time.** Um índice enxuto (`router.md`) e cada instrução carregada por gatilho.
- **Nomes simples e convencionais.** Zero jargão poético.

---

## Como usar

A Aliança é a pasta [`alianca/`](alianca/). Para usá-la em um projeto:

1. **Copie a pasta `alianca/`** para a raiz do seu projeto.
2. **Aponte seu LLM para [`alianca/START-HERE.md`](alianca/START-HERE.md)** e diga para lê-lo primeiro. Esse arquivo + o [`router.md`](alianca/router.md) bastam para operar.
3. Em um **projeto novo**, o LLM conduz o `setup` (questionário curto), dimensiona o projeto e gera a estrutura sob medida — confirmando com você antes de criar nada.
4. Em um **projeto em andamento**, o LLM lê o snapshot mais recente e retoma de onde parou.

**Mapeamento por ferramenta:**

| Ferramenta | Como a Aliança se encaixa |
|---|---|
| **Claude Code** | cada instrução vira uma *skill* (o `trigger` é a linha TRIGGER); memória e subagents nativos |
| **Cursor / outros** | `router.md` no system prompt; instruções lidas sob demanda |
| **Qualquer LLM** | basta ler arquivos: siga o `START-HERE.md` → `router.md` |

---

## Como funciona (em 1 minuto)

1. **Persona primeiro** — o harness descobre com quem fala: **P0** (leigo) · **P1** (iniciante) · **P2** (dev) · **P3** (time/org). A linguagem e o nível de automação se adaptam.
2. **Três eixos** — pontua **Estrutura**, **Longevidade** e **Risco** com uma rubrica explícita.
3. **Nível 0–4** — a combinação dos eixos dá o nível do harness (do mínimo à plataforma de org). É uma **estimativa inicial**: o harness observa o comportamento real e **reajusta** ao longo do projeto.
4. **Backbone inegociável** — testes, qualidade, refatoração, prevenção de bugs e segurança em **todos** os níveis; só muda a profundidade.
5. **Memória segmentada + snapshots** — o que importa vive em disco e é recuperável por qualquer modelo, em qualquer sessão.

---

## As 13 instruções

Carregadas **uma por vez, por gatilho** (índice completo em [`alianca/router.md`](alianca/router.md)):

| Instrução | Carregue quando… |
|---|---|
| [`setup`](alianca/instructions/setup.md) | iniciar um projeto novo (bootstrap) |
| [`persona-p0`](alianca/instructions/persona-p0.md) | o usuário é leigo (P0) |
| [`deep-questions`](alianca/instructions/deep-questions.md) | a triagem indicou um eixo ≥ 2 |
| [`testing`](alianca/instructions/testing.md) | criar/alterar lógica testável |
| [`code-quality`](alianca/instructions/code-quality.md) | antes de commit / ao abrir PR |
| [`architecture`](alianca/instructions/architecture.md) | criar/alterar estrutura: módulo, camada, fronteira |
| [`refactor`](alianca/instructions/refactor.md) | detectar duplicação ou função longa demais |
| [`bug-prevention`](alianca/instructions/bug-prevention.md) | código com risco de erro (entrada externa, estado, concorrência) |
| [`security`](alianca/instructions/security.md) | tocar em auth, dados pessoais, pagamentos ou segredos |
| [`snapshot`](alianca/instructions/snapshot.md) | antes de tarefa grande ou ao concluir um marco |
| [`migration`](alianca/instructions/migration.md) | o projeto cresceu/encolheu e o nível precisa mudar |
| [`health-check`](alianca/instructions/health-check.md) | revisar a saúde do harness (periódico) |
| [`agents`](alianca/instructions/agents.md) | decidir dividir trabalho entre vários agentes |

---

## Estrutura do repositório

```
.
├─ README.md          ← você está aqui
├─ PROTOCOL.md        ← a teoria/spec completa (16 seções)
├─ HANDOFF.md         ← estado e decisões do desenvolvimento da Aliança
└─ alianca/           ← a implementação de referência (é isto que você copia)
   ├─ START-HERE.md   ← ponto de entrada de qualquer LLM
   ├─ router.md       ← índice das instruções + gatilhos + precedência
   ├─ instructions/   ← as 13 instruções carregadas por gatilho
   ├─ memory/         ← memória do projeto (contexto, stack, decisões, arquivo)
   └─ snapshots/      ← pontos de retomada
```

> A **stack não tem pasta**: a LLM decide as ferramentas no `setup` (do próprio conhecimento) e registra os comandos concretos em `memory/stack.md`, sob medida para cada projeto.

---

## Edições (trilha de crescimento)

| Edição | Persona | Promessa |
|---|---|---|
| **Aliança Start** | P0/P1 (leigo, iniciante) | máxima automação, linguagem humana, "do zero ao no ar" |
| **Aliança Pro** | P2 (dev experiente) | controle total, integra com suas ferramentas |
| **Aliança Org** | P3 (time/empresa) | governança, auditoria, múltiplos agentes, compliance |

Um projeto **sobe de edição** conforme a persona e o nível evoluem — sem recomeçar.

---

## Documentação

- **[`alianca/START-HERE.md`](alianca/START-HERE.md)** — comece por aqui (modelo mental + loop de operação).
- **[`alianca/router.md`](alianca/router.md)** — índice das instruções e ordem de precedência.
- **[`PROTOCOL.md`](PROTOCOL.md)** — a spec completa; só necessária para evoluir o próprio harness.
- **[`VALIDATION.md`](VALIDATION.md)** — validação prática: teste A/B (com vs sem harness) em duas LLMs, com método, resultados e os empates assumidos.

## Status

Versão **2.1** (rascunho, em evolução). As 13 instruções estão prontas e a Aliança está conceitualmente fechada; o calibre fino da rubrica continua se ajustando no uso real, pelo próprio loop adaptativo (estimativa → observa → reajusta). **Validada na prática** com um teste A/B em duas LLMs (Claude e Copilot) — ver [`VALIDATION.md`](VALIDATION.md). Idioma de trabalho: **PT-BR** (artefatos gerados seguem o idioma do usuário).

---

<sub>**Tópicos:** harness para LLM · scaffolding para agentes de IA · model-agnostic LLM harness · context engineering · agentic coding · AI pair programming · memória persistente para agentes · Claude Code · Cursor · prompt/instruction routing just-in-time · gerador de harness adaptativo.</sub>
