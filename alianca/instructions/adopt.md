---
trigger: chegar a um projeto que JÁ EXISTE e ainda não usa a Aliança — há código/docs, mas não existe a pasta `alianca/` (nem `memory/active-context.md`)
keywords: adotar, adote, adota, adocao, brownfield, projeto existente, integrar a alianca, instalar a alianca, adotar a alianca
load-when: bootstrap
applies-to: todas as personas (na prática P1–P3; raro em P0)
priority: bootstrap (roda antes de qualquer execução; fora da ordem de precedência de código)
---

# adopt — adoção de um projeto existente (brownfield)

O `setup` é greenfield: parte do zero e **pergunta**. O `adopt` é o inverso: o projeto já existe, então você **lê a realidade** e reconstrói o entendimento a partir dela — e migra a memória antiga **sem criar uma segunda**. Não rode o questionário do `setup` por cima de um projeto que já tem código; isso é o que gera o bootstrap confuso e as duas memórias em conflito.

> **Adoção é integração, não substituição — é um abraço.** O projeto não deixa de ser o que é; a Aliança se molda a ele e o envolve. Nenhuma identidade se perde: o conhecimento antigo é **acolhido** dentro de `memory/`, e o comportamento do código **não muda** nesta etapa. O único que sai de cena é o *container duplicado* que competia pela verdade — o conteúdo dele continua vivo, agora organizado.

## Regra zero — a memória nativa passa a obedecer a Aliança (INEGOCIÁVEL)

> **Em projeto em andamento, isto é a primeira coisa garantida pela adoção e não admite exceção — vale para QUALQUER LLM** (Claude Code, Cursor, Copilot, Gemini, ou outro).

Toda ferramenta de LLM tem memória própria (Claude Code: `CLAUDE.md` + memória nativa do projeto; Cursor: `.cursorrules`/`rules`; outros: `AGENTS.md`, system prompt, notas). **A adoção reescreve TODOS esses arquivos de memória nativa** para que, a partir de agora, eles **sempre** mandem o LLM seguir a Aliança. Sem isso, a adoção **não está feita** — o LLM volta a operar pela memória antiga no próximo prompt.

Cada arquivo de memória nativa, após reescrito, **obriga-se** a:

1. **Mandar rotear pela Aliança em todo turno** — texto explícito do tipo: *"Antes de qualquer ação, leia `alianca/START-HERE.md` e `alianca/router.md` e siga o loop de operação; carregue cada instrução por gatilho."* A memória nativa vira **reforço** do "sempre ligado", não uma fonte concorrente.
2. **Apontar para `alianca/memory/` como fonte única do estado do projeto** — e **parar de duplicar** esse estado. O que era verdadeiro foi acolhido em `memory/` (Passo 3); o resto foi arquivado.
3. **Ceder em qualquer conflito:** se algo na memória nativa contradiz a Aliança, **a Aliança vence** — o nativo é reescrito, nunca mantido em paralelo.

Isto é mais forte que o forcing function (Passo 4): o forcing function injeta o roteamento via mecanismo da ferramenta; a Regra zero garante que a **própria memória do modelo** também o ordene — defesa em profundidade contra "o LLM esquecer a Aliança".

## Passo 1 — Inventário (não pergunte o que dá para ler)

Levante o estado real antes de qualquer pergunta. **Cite `arquivo:linha`** ao afirmar o que encontrou (anti-alucinação):

- **Estrutura e stack:** árvore de pastas, manifestos de dependência, configs de build/test/lint/CI. Isso já decide a maior parte do `memory/stack.md` — não pergunte o que o `package.json`/`pyproject`/etc. respondem.
- **Conhecimento existente:** `README`, `docs/`, `ARCHITECTURE`, comentários de decisão, e **toda memória anterior** — `CLAUDE.md`/`AGENTS.md`/`.cursorrules`, notas soltas, e a **memória nativa da ferramenta** (ex.: a memória do Claude Code para este projeto).
- **Convenções vigentes:** formatter/linter já configurados, padrão de commit, testes existentes. O harness **respeita** o que já está estabelecido — não impõe o seu.
- **Sinais de risco no código:** auth, dados pessoais, pagamento, segredos. Alimentam o eixo R.

## Passo 2 — Inferir persona e eixos da realidade

Use a **rubrica do `setup`** (Passos 2–3) — não a duplique aqui —, mas pontue a partir de **evidência**, não de questionário:

- **Estrutura (E):** nº de módulos/serviços/camadas reais que você inventariou.
- **Longevidade (L):** idade e histórico do repositório + intenção de manutenção. *Isto o código não revela* → é uma das poucas perguntas legítimas.
- **Risco (R):** o que o código realmente toca (auth/dados/pagamento/setor regulado).

Pergunte **só o que o código não mostra** (longevidade pretendida, persona, planos). Tudo o mais, infira e **confirme**, não pergunte.

## Passo 3 — Migração da memória (fonte única da verdade)

O ponto crítico — é aqui que nascem as "duas memórias":

1. **Mover TODOS os `.md` para dentro da Aliança (obrigatório):** **todo** arquivo `.md` do projeto (`README`, `docs/`, `ARCHITECTURE`, notas soltas, design docs, etc.) é **movido para a Aliança** — o conteúdo ainda verdadeiro é **mesclado e adaptado** nos segmentos de `memory/` (`vision`, `architecture`, `business-rules`, `stack`, `decisions/`), no nível inferido; o obsoleto vai para `archive/` (migrar, nunca apagar). Conflito entre fontes antigas → vale o que o **código** mostra. Não sobra documentação espalhada competindo pela verdade.
2. **Única exceção — quebraria o projeto → vira ponteiro:** um `.md` cuja remoção **quebra algo** (ex.: `README.md` que o GitHub/registry/empacotamento espera, docs que alimentam um site/gerador, arquivo referenciado pelo build/CI) **permanece no lugar, reduzido a um ponteiro** para a Aliança — uma linha curta tipo *"Fonte da verdade: `alianca/memory/…`"*, sem conteúdo duplicado. Mover só quando é seguro; quando não é, apontar.
3. **Memória nativa da ferramenta:** aplique a **Regra zero** (acima) — reescreva-a para **mandar seguir a Aliança** e **apontar** para `alianca/memory/` como fonte da verdade; ela não duplica estado de projeto (no máximo guarda fatos de usuário/preferência). Em Claude Code, isto elimina o conflito entre a memória nativa e a da Aliança.

> **Invariante — fonte única:** depois da adoção existe **uma** memória de projeto ativa (`alianca/memory/`). Nunca duas. Toda outra aponta para ela ou está arquivada.

## Passo 4 — Ligar o forcing function ("sempre ligado")

Sem isto, a adoção não "pega": o LLM volta a ignorar o harness no próximo prompt. Instale o forcing function da ferramenta-hospedeira — **molde no `setup` (Passo 8)**. Em Claude Code: kernel no `CLAUDE.md` + hook `UserPromptSubmit`.

## Passo 5 — Dry-run + confirmar (antes de criar ou mover)

Apresente e **peça confirmação** antes de tocar em arquivos:

```
PROPOSTA DE ADOÇÃO — ALIANÇA
Projeto: <nome>  ·  Persona: <P_>  ·  Nível inferido: <0–4>  (E=__ L=__ R=__)
Stack detectada: <do inventário>
Vou mover/mesclar TODOS os .md p/ memory/: <README, docs/, ARCHITECTURE, notas…>
   exceção (fica como ponteiro, mover quebraria): <ex.: README.md raiz, docs do site>
Vou REESCREVER a memória nativa (Regra zero): <arquivos> → mandam seguir a Aliança + apontam p/ memory/
Vou arquivar (obsoleto): <notas vencidas → memory/archive/>
Vou ligar o "sempre ligado": <CLAUDE.md kernel + hook UserPromptSubmit>
Não vou alterar comportamento de código. Confirma? (sim / ajustar)
```

## Passo 6 — Gerar e registrar

Após o "sim": crie a estrutura `alianca/` do nível inferido (ver `setup` Passo 5–7), escreva a `memory/` migrada, instale o forcing function, gere o snapshot inicial `snapshots/snapshot-AAAA-MM-DD-adopt.md` e registre a adoção em `memory/decisions/`. **Semeie o quadro de tarefas** (ver `tasks`) com o que o inventário revelou: o que já existe e funciona entra como *Validada*; pendências/TODOs/issues abertos entram como *A fazer*. A partir daqui, siga o loop do `START-HERE`.

## Para P0 (leigo)

Raro, mas se acontecer: zero jargão. "Vou organizar o que já existe e ligar o assistente pra trabalhar sempre do jeito certo — sem mexer no que já funciona. Pode ser?"
