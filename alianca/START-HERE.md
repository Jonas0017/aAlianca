# START-HERE — Aliança

> **O elo que liga os dois mundos.**
> Você (LLM) chegou a um projeto Aliança. **Leia este arquivo inteiro antes de qualquer ação.** Ele + o `router.md` bastam para operar; a teoria completa fica em [`../PROTOCOL.md`](../PROTOCOL.md) e você só precisa dela se for evoluir o próprio harness.

---

## 0. Te pediram para "instalar / integrar a Aliança neste projeto"?

Se o comando do usuário foi algo como *"baixa e instala esse código aqui"*, *"integra a Aliança nesse projeto"* ou *"usa esse harness"* — **este arquivo é o ponto de partida e você já tem tudo para agir**, sem pedir mais instruções:

1. **Garanta que a pasta `alianca/` está na raiz do projeto** (se ainda não está, copie/clone a pasta-referência para cá).
2. **Decida o caminho** pela regra do §2 abaixo: projeto que **já tem código** → instrução **`adopt`** (integração/"abraço": lê a realidade, acolhe a memória antiga, não recomeça nada); projeto **vazio** → **`setup`**.
3. **O `adopt`/`setup` instala o forcing function** (kernel no `CLAUDE.md` + hook `UserPromptSubmit`; `setup` Passo 8). É o passo que torna a instalação **permanente**: a partir dele, **todo prompt** passa pelo harness automaticamente — o usuário nunca mais precisa lembrar você de usá-lo.

> Em resumo: **um comando de instalação é suficiente.** Você lê este arquivo, roda `adopt` (ou `setup`), e liga o "sempre ligado". Daí em diante o harness se conduz sozinho.

---

## 1. O que é a Aliança

Um **harness adaptativo**: estrutura + instruções que se moldam ao **projeto**, à **pessoa** e à **stack**, para que qualquer LLM trabalhe com baixo risco de alucinação, retrabalho, perda de contexto e dívida técnica. A Aliança não despeja tudo no seu contexto — ela mantém um índice (`router.md`) e você **carrega cada instrução no momento exato** em que o gatilho dela ocorre.

---

## 2. Sua primeira decisão: novo, existente ou em andamento?

- **`memory/active-context.md` existe** → projeto Aliança **em andamento** → leia o **snapshot** mais recente em `snapshots/`, depois `memory/active-context.md`, e **retome de onde parou** sem depender de histórico anterior.
- **NÃO existe `active-context.md`, e o projeto já tem código/docs** (mas nunca usou a Aliança) → **adoção** → carregue a instrução `adopt`. Você **lê a realidade** e integra o harness ao que já existe — **não** rode o questionário do `setup` por cima. (É um abraço: o projeto continua sendo o que é; a memória antiga é acolhida, não substituída.) **Regra zero, inegociável e válida para qualquer LLM:** a primeira coisa garantida pela adoção é **reescrever TODOS os arquivos de memória nativa** para que sempre mandem seguir a Aliança e apontem para `alianca/memory/` (ver `adopt`).
- **NÃO existe `active-context.md`, e não há código ainda** → projeto **novo** → vá para o §3 (Setup).

---

## 3. Setup — bootstrap (só em projeto novo)

**Sua primeira responsabilidade NÃO é escrever código. É criar o ambiente certo.** Antes de qualquer linha:

1. Carregue a instrução **`setup`** (veja `router.md`) e conduza o **questionário progressivo**.
2. **Classifique a persona** pela pergunta de abertura: P0 (leigo) · P1 (iniciante) · P2 (dev) · P3 (time/org).
3. **Pontue os 3 eixos** — Estrutura (E), Longevidade (L), Risco (R) — e calcule o **Nível (0–4)**, uma **estimativa inicial**: base = `banda(E)`; **+1** se Longevidade alta, **+1** se Risco alto (cap 4). Qualquer sinal sensível engaja a segurança, proporcional ao risco.
4. **Mostre a estrutura proposta e confirme (dry-run)** antes de criar arquivos.
5. **Gere** a estrutura do nível: memória mínima (`memory/active-context.md` + `memory/stack.md`; `vision.md` a partir do Nível 1) e, **a partir do Nível 1**, um snapshot inicial em `snapshots/`.
6. **Instale o forcing function** (`setup` Passo 8) — sem ele, o harness não fica "sempre ligado".

---

## 4. O loop de operação (todo turno)

```
1. CHECAR   → leia router.md. Algum gatilho casa com o que vou fazer agora?
2. CARREGAR → se sim, leia aquela instrução ANTES de agir (just-in-time).
3. AGIR
4. VERIFICAR→ nada é "feito" sem executar/observar (ver §5).
5. PERSISTIR→ atualize memory/active-context.md; ao fechar um marco,
             gere um snapshot e consolide a memória.
```

> **É um loop, não uma fila:** se o VERIFICAR falha, diagnostique a causa e volte ao AGIR com a abordagem ajustada — não insista no que não funcionou nem declare pronto. Erro que **se repete** vira regra em `memory/feedback.md` — o harness aprende e não erra duas vezes.

---

## 5. Invariantes (valem sempre, em todos os níveis)

- **Sempre ligado:** o loop do §4 não é opcional — **todo prompt** passa pelo roteamento do `router.md` antes de qualquer ação. Quem garante isso sem depender de você lembrar é o **forcing function** instalado no bootstrap (Claude Code: kernel no `CLAUDE.md` + hook `UserPromptSubmit`; ver `setup` Passo 8). Se ele não existe neste projeto, **instale-o**.
- **Uma só memória de projeto:** a fonte da verdade é `alianca/memory/`. Nunca opere com duas memórias ativas em paralelo — memória nativa da ferramenta ou docs legados **apontam** para `memory/` ou são arquivados (ver `adopt`). **Na adoção isto é inegociável e vale para qualquer LLM:** toda memória nativa é **reescrita** para mandar seguir a Aliança e apontar para `memory/` (Regra zero do `adopt`), nunca mantida como fonte concorrente.
- **Backbone inegociável:** testes, qualidade de código, refatoração e prevenção de bugs estão **sempre** presentes — só a profundidade varia por nível.
- **Use o que já existe:** antes de construir algo não-trivial, veja se há pronto — skill, ferramenta, biblioteca ou serviço (MCP) que resolva. Reaproveitar > reinventar; construa do zero só quando nada serve. Dependência externa entra com higiene (proveniência, licença, scan — ver `security`).
- **Definition of Done:** uma tarefa só fecha com **testes passando, lint limpo e docs/memória atualizados**.
- **Esteira desde o onboarding:** o bootstrap (`setup`/`adopt`) **não fecha** sem a esteira de testes **armada e verde** — `alianca/kernel/verify.cmd` apontando para o comando de teste do projeto (projeto novo: **entenda antes**, depois monte; em andamento: monte a esteira **completa já**). Sem `verify.cmd` o 3º portão fica inerte. Ver `testing` §Esteira desde o onboarding.
- **Anti-alucinação:** nunca declare algo pronto sem rodar/observar; **cite `arquivo:linha`** ao afirmar fatos sobre o código.
- **Estado vive em disco:** o que importa fica em `memory/` e `snapshots/`, nunca só na janela de contexto. Não tente administrar % de contexto — garanta recuperabilidade.
- **Coordenador por padrão:** a sessão principal **coordena**; execução pesada e autocontida (implementação inteira, mudança multi-arquivo, varredura, pesquisa, verificação que roda coisas) vai para um **subagente** e volta como **resumo** — isso descarrega a janela *de trabalho*, complementando o "estado vive em disco" (que descarrega a janela *persistente*). Ajuste trivial e decisões ficam inline. O hook `kernel/route.py` injeta esse lembrete nos turnos de execução; você não precisa pedir.
- **Segredos:** nunca commitar credencial; `.gitignore` + `.env.example` a partir do Nível 1 (quando há repositório).
- **Persona P0 (leigo):** linguagem humana, zero jargão. Entregue a ele "o que foi feito / o que falta / o que preciso de você".
- **O harness aprende:** erro que se repete neste projeto vira regra em `memory/feedback.md` — não erre a mesma coisa duas vezes.

---

## 6. Mapa da pasta

| Caminho | Para quê |
|---|---|
| `START-HERE.md` | orientação inicial de qualquer LLM/humano (este arquivo) |
| `router.md` | índice de instruções + gatilhos; leia a cada turno |
| `instructions/` | módulos de instrução carregados por gatilho |
| `memory/` | memória do projeto (vision, contexto ativo, `stack.md`, decisões, arquivo) |
| `snapshots/` | pontos de retomada |
| `../PROTOCOL.md` | a teoria / spec completa do harness |

> A **stack não tem pasta**: a LLM decide as ferramentas no `setup` (do próprio conhecimento) e registra os comandos concretos em `memory/stack.md`, sob medida para cada projeto.
