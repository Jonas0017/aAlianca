# START-HERE — Aliança

> **O elo que liga os dois mundos.**
> Você (LLM) chegou a um projeto Aliança. **Leia este arquivo inteiro antes de qualquer ação.** Ele + o `router.md` bastam para operar; a teoria completa fica em [`../PROTOCOL.md`](../PROTOCOL.md) e você só precisa dela se for evoluir o próprio harness.

---

## 1. O que é a Aliança

Um **harness adaptativo**: estrutura + instruções que se moldam ao **projeto**, à **pessoa** e à **stack**, para que qualquer LLM trabalhe com baixo risco de alucinação, retrabalho, perda de contexto e dívida técnica. A Aliança não despeja tudo no seu contexto — ela mantém um índice (`router.md`) e você **carrega cada instrução no momento exato** em que o gatilho dela ocorre.

---

## 2. Sua primeira decisão: projeto novo ou em andamento?

- **`memory/active-context.md` NÃO existe** → projeto **novo** → vá para o §3 (Setup).
- **`memory/active-context.md` existe** → projeto **em andamento** → leia o **snapshot** mais recente em `snapshots/`, depois `memory/active-context.md`, e **retome de onde parou** sem depender de histórico anterior.

---

## 3. Setup — bootstrap (só em projeto novo)

**Sua primeira responsabilidade NÃO é escrever código. É criar o ambiente certo.** Antes de qualquer linha:

1. Carregue a instrução **`setup`** (veja `router.md`) e conduza o **questionário progressivo**.
2. **Classifique a persona** pela pergunta de abertura: P0 (leigo) · P1 (iniciante) · P2 (dev) · P3 (time/org).
3. **Pontue os 3 eixos** — Estrutura (E), Longevidade (L), Risco (R) — e calcule o **Nível (0–4)**: nível base = faixa de `max(E,L)`; se `R ≥ 40`, sobe +1 nível e força módulos de segurança.
4. **Mostre a estrutura proposta e confirme (dry-run)** antes de criar arquivos.
5. **Gere** a estrutura do nível: memória mínima (`memory/active-context.md` + `memory/stack.md`; `vision.md` a partir do Nível 1) e, **a partir do Nível 1**, um snapshot inicial em `snapshots/`.

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

- **Backbone inegociável:** testes, qualidade de código, refatoração e prevenção de bugs estão **sempre** presentes — só a profundidade varia por nível.
- **Use o que já existe:** antes de construir algo não-trivial, veja se há pronto — skill, ferramenta, biblioteca ou serviço (MCP) que resolva. Reaproveitar > reinventar; construa do zero só quando nada serve. Dependência externa entra com higiene (proveniência, licença, scan — ver `security`).
- **Definition of Done:** uma tarefa só fecha com **testes passando, lint limpo e docs/memória atualizados**.
- **Anti-alucinação:** nunca declare algo pronto sem rodar/observar; **cite `arquivo:linha`** ao afirmar fatos sobre o código.
- **Estado vive em disco:** o que importa fica em `memory/` e `snapshots/`, nunca só na janela de contexto. Não tente administrar % de contexto — garanta recuperabilidade.
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
