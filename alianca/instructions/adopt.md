---
trigger: chegar a um projeto que JÁ EXISTE e ainda não usa a Aliança — há código/docs, mas não existe a pasta `alianca/` (nem `memory/active-context.md`)
load-when: bootstrap
applies-to: todas as personas (na prática P1–P3; raro em P0)
priority: bootstrap (roda antes de qualquer execução; fora da ordem de precedência de código)
---

# adopt — adoção de um projeto existente (brownfield)

O `setup` é greenfield: parte do zero e **pergunta**. O `adopt` é o inverso: o projeto já existe, então você **lê a realidade** e reconstrói o entendimento a partir dela — e migra a memória antiga **sem criar uma segunda**. Não rode o questionário do `setup` por cima de um projeto que já tem código; isso é o que gera o bootstrap confuso e as duas memórias em conflito.

> **Adoção é integração, não substituição — é um abraço.** O projeto não deixa de ser o que é; a Aliança se molda a ele e o envolve. Nenhuma identidade se perde: o conhecimento antigo é **acolhido** dentro de `memory/`, e o comportamento do código **não muda** nesta etapa. O único que sai de cena é o *container duplicado* que competia pela verdade — o conteúdo dele continua vivo, agora organizado.

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

1. **Acolher:** todo conhecimento **ainda verdadeiro** vira `memory/` segmentado (`vision`, `architecture`, `business-rules`, `stack`, `decisions/`), no nível inferido. Conflito entre fontes antigas → vale o que o **código** mostra.
2. **Recolher o container duplicado (migrar, não apagar):** depois de acolher o conteúdo, o container antigo (CLAUDE.md legado, notas, docs redundantes) vai para `memory/archive/legacy-<origem>.md` com um ponteiro. Ele **deixa de competir como fonte** — fica preservado, fora do caminho. O conhecimento não morre; só para de existir em dois lugares ao mesmo tempo.
3. **Memória nativa da ferramenta:** reconfigure-a para **apontar** para `alianca/memory/` como fonte da verdade do projeto; ela não duplica estado de projeto (no máximo guarda fatos de usuário/preferência). Em Claude Code, isto evita o conflito entre a memória nativa e a da Aliança.

> **Invariante — fonte única:** depois da adoção existe **uma** memória de projeto ativa (`alianca/memory/`). Nunca duas. Toda outra aponta para ela ou está arquivada.

## Passo 4 — Ligar o forcing function ("sempre ligado")

Sem isto, a adoção não "pega": o LLM volta a ignorar o harness no próximo prompt. Instale o forcing function da ferramenta-hospedeira — **molde no `setup` (Passo 8)**. Em Claude Code: kernel no `CLAUDE.md` + hook `UserPromptSubmit`.

## Passo 5 — Dry-run + confirmar (antes de criar ou mover)

Apresente e **peça confirmação** antes de tocar em arquivos:

```
PROPOSTA DE ADOÇÃO — ALIANÇA
Projeto: <nome>  ·  Persona: <P_>  ·  Nível inferido: <0–4>  (E=__ L=__ R=__)
Stack detectada: <do inventário>
Vou migrar p/ memory/: <vision, architecture, business-rules…>
Vou arquivar: <CLAUDE.md legado, notas redundantes → memory/archive/>
Vou ligar o "sempre ligado": <CLAUDE.md kernel + hook UserPromptSubmit>
Não vou alterar comportamento de código. Confirma? (sim / ajustar)
```

## Passo 6 — Gerar e registrar

Após o "sim": crie a estrutura `alianca/` do nível inferido (ver `setup` Passo 5–7), escreva a `memory/` migrada, instale o forcing function, gere o snapshot inicial `snapshots/snapshot-AAAA-MM-DD-adopt.md` e registre a adoção em `memory/decisions/`. A partir daqui, siga o loop do `START-HERE`.

## Para P0 (leigo)

Raro, mas se acontecer: zero jargão. "Vou organizar o que já existe e ligar o assistente pra trabalhar sempre do jeito certo — sem mexer no que já funciona. Pode ser?"
