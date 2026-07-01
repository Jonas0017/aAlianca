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

A Aliança é a pasta [`alianca/`](alianca/). **Um comando basta** — "baixa e instala esse harness neste projeto" / "integra a Aliança aqui". A partir daí:

1. **Copie a pasta `alianca/`** para a raiz do seu projeto (ou peça ao LLM para fazê-lo).
2. **Aponte seu LLM para [`alianca/START-HERE.md`](alianca/START-HERE.md)** e diga para lê-lo primeiro. Esse arquivo + o [`router.md`](alianca/router.md) bastam para o LLM entender tudo que precisa fazer.
3. Em um **projeto novo** (vazio), o LLM conduz o `setup` (questionário curto), dimensiona e gera a estrutura sob medida — confirmando antes de criar nada.
4. Em um **projeto que já existe**, o LLM roda a `adopt`: **lê o código e os docs**, infere o nível, **acolhe a memória antiga numa fonte única** e integra o harness — sem recomeçar e sem mexer no comportamento (é integração, não substituição).
5. Em um **projeto Aliança em andamento**, o LLM lê o snapshot mais recente e retoma de onde parou.

> **Sempre ligado:** no bootstrap, o LLM instala um *forcing function* — o mecanismo que faz **todo prompt** passar pelo harness automaticamente, sem você precisar lembrar o LLM de usá-lo a cada vez.

**Onde cada coisa funciona (honestidade sobre o alcance):** a estrutura `.md` é model-agnostic — qualquer LLM que lê arquivos consegue seguir o `START-HERE.md` → `router.md`, e isso foi **validado na prática** em modelos diferentes (ver [`VALIDATION.md`](VALIDATION.md)). Já o **forcing function determinístico** — o microkernel de hooks em [`alianca/kernel/`](alianca/kernel/) (roteamento por prompt + portões de segurança e verificação) — hoje existe **apenas para Claude Code**. Nas demais ferramentas o harness opera em **modo advisory**: prosa (regra "always apply" / preâmbulo) mandando seguir o router — funciona, mas é mais fraco, porque depende do modelo honrar o texto. Adapters determinísticos para outras ferramentas são roadmap.

**Mapeamento por ferramenta:**

| Ferramenta | Como a Aliança se encaixa |
|---|---|
| **Claude Code** | **suporte completo:** kernel de hooks determinístico (route/gate/verify) + `CLAUDE.md`; memória e subagents nativos |
| **Cursor / outros** | **modo advisory:** `router.md` via regra "always apply"/system prompt; instruções lidas sob demanda |
| **Qualquer LLM** | **modo advisory:** basta ler arquivos — siga o `START-HERE.md` → `router.md` |

---

## Como funciona (em 1 minuto)

1. **Persona primeiro** — o harness descobre com quem fala: **P0** (leigo) · **P1** (iniciante) · **P2** (dev) · **P3** (time/org). A linguagem e o nível de automação se adaptam.
2. **Três eixos** — pontua **Estrutura**, **Longevidade** e **Risco** com uma rubrica explícita.
3. **Nível 0–4** — a combinação dos eixos dá o nível do harness (do mínimo à plataforma de org). É uma **estimativa inicial**: o harness observa o comportamento real e **reajusta** ao longo do projeto.
4. **Backbone inegociável** — testes, qualidade, refatoração, prevenção de bugs e segurança em **todos** os níveis; só muda a profundidade.
5. **Memória segmentada + snapshots** — o que importa vive em disco e é recuperável por qualquer modelo, em qualquer sessão.

---

## As 18 instruções

Carregadas **uma por vez, por gatilho** (índice completo em [`alianca/router.md`](alianca/router.md)):

| Instrução | Carregue quando… |
|---|---|
| [`setup`](alianca/instructions/setup.md) | iniciar um projeto novo (bootstrap) |
| [`adopt`](alianca/instructions/adopt.md) | integrar a Aliança a um projeto que já existe (brownfield) |
| [`persona-p0`](alianca/instructions/persona-p0.md) | o usuário é leigo (P0) |
| [`deep-questions`](alianca/instructions/deep-questions.md) | a triagem indicou um eixo ≥ 2 |
| [`testing`](alianca/instructions/testing.md) | criar/alterar lógica testável |
| [`code-quality`](alianca/instructions/code-quality.md) | antes de commit / ao abrir PR |
| [`architecture`](alianca/instructions/architecture.md) | criar/alterar estrutura: módulo, camada, fronteira |
| [`refactor`](alianca/instructions/refactor.md) | detectar duplicação ou função longa demais |
| [`bug-prevention`](alianca/instructions/bug-prevention.md) | código com risco de erro (entrada externa, estado, concorrência) |
| [`security`](alianca/instructions/security.md) | tocar em auth, dados pessoais, pagamentos ou segredos |
| [`interface`](alianca/instructions/interface.md) | criar/alterar superfície humana: tela, layout, fluxo, CLI, texto de UI |
| [`tasks`](alianca/instructions/tasks.md) | criar uma tarefa ou movê-la entre os 4 estados (A fazer · Em andamento · Realizada · Validada) |
| [`questions`](alianca/instructions/questions.md) | perguntar algo sobre o projeto, adiar uma resposta ou registrá-la (por tópico) |
| [`snapshot`](alianca/instructions/snapshot.md) | antes de tarefa grande ou ao concluir um marco |
| [`migration`](alianca/instructions/migration.md) | o projeto cresceu/encolheu e o nível precisa mudar |
| [`health-check`](alianca/instructions/health-check.md) | revisar a saúde do harness (periódico) |
| [`x9`](alianca/instructions/x9.md) | auditar pontas soltas do projeto — coisas criadas/prometidas pela metade |
| [`agents`](alianca/instructions/agents.md) | decidir dividir trabalho entre vários agentes |

---

## Estrutura do repositório

```
.
├─ README.md            ← você está aqui
├─ PROTOCOL.md          ← a teoria/spec completa (17 seções, §0–§16)
├─ HANDOFF.md           ← estado e decisões do desenvolvimento da Aliança
├─ VALIDATION.md        ← validação prática (testes A/B com e sem harness)
└─ alianca/             ← a implementação de referência (é isto que você copia)
   ├─ START-HERE.md     ← ponto de entrada de qualquer LLM
   ├─ router.md         ← índice das instruções + gatilhos + precedência
   ├─ router.index.json ← índice compilado (gerado por kernel/compile.py)
   ├─ instructions/     ← as 18 instruções carregadas por gatilho
   ├─ kernel/           ← microkernel (Claude Code): hooks route/gate/verify + log
   ├─ memory/           ← memória do projeto (contexto, stack, decisões, arquivo)
   └─ snapshots/        ← pontos de retomada
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

Versão **2.2** (rascunho, em evolução). As 18 instruções estão prontas e a Aliança está conceitualmente fechada; o calibre fino da rubrica continua se ajustando no uso real, pelo próprio loop adaptativo (estimativa → observa → reajusta). A **2.2** trouxe o módulo `interface` (design/ergonomia/acessibilidade), o caminho `adopt` (integrar a projetos que já existem, com memória de fonte única), o **forcing function "sempre ligado"** (todo prompt passa pelo harness, sem depender do modelo lembrar) e o módulo `x9` (auditoria de pontas soltas). **Validada na prática** em dois rounds — teste A/B em duas LLMs (Claude e Copilot) e teste controlado com kernel + LLM local — ver [`VALIDATION.md`](VALIDATION.md).

**Alcance honesto:** a estrutura `.md` funciona em qualquer LLM leitor de arquivos (é isso que a validação mostra); o **enforcement determinístico** — o microkernel de hooks (`alianca/kernel/`) — hoje é **só Claude Code**. Nas demais ferramentas o harness roda em modo advisory (mais fraco). A ambição universal continua; adapters para outras ferramentas são o roadmap, não o presente. Idioma de trabalho: **PT-BR** (artefatos gerados seguem o idioma do usuário).

---

<sub>**Tópicos:** harness para LLM · scaffolding para agentes de IA · model-agnostic LLM harness · context engineering · agentic coding · AI pair programming · memória persistente para agentes · Claude Code · Cursor · prompt/instruction routing just-in-time · gerador de harness adaptativo.</sub>
