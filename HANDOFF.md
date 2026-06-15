# Snapshot / Handoff — Projeto Aliança — 2026-06-08

> Ponto de retomada autossuficiente. Abra uma nova sessão e diga: **"continue a partir do HANDOFF.md"**. Tudo que você precisa para continuar está aqui.

## O que é o projeto

Construir a **Aliança** — um *gerador de harness* adaptativo e **model-agnostic** (qualquer LLM + outras ferramentas) que serve de base para qualquer projeto de qualquer dev. Não é um harness único: produz estruturas diferentes conforme a **persona** (P0 leigo → P3 time/org) e a **stack**. Slogan: "o elo que liga os dois mundos".

Princípios-chave: dimensionamento **multi-eixo** (Estrutura/Longevidade/Risco) com rubrica determinística; **backbone inegociável** (testes, qualidade, refatoração, prevenção de bugs); carregamento **just-in-time** de instruções por gatilho; **estado em disco** (memória/snapshots), não em % de contexto.

## Decisões travadas

- **Nome do produto:** Aliança. Edições comerciais: Start (P0/P1), Pro (P2), Org (P3).
- **Nomenclatura simples** (usuário rejeitou nomes poéticos): `START-HERE.md`, `router.md`, `instructions/`, `memory/`, `snapshots/`; instrução `setup` (bootstrap); `agents`, `coordinator`, `health-check`.
- **Formato de entrega:** pasta-referência em `.md` puro (model-agnostic).
- **Sem `stacks/` (decisão 2.1).** Sugerir ferramentas é trabalho da LLM, não do harness — catálogo `.md` seria redundante, inflaria contexto e apodreceria. A stack é **decidida no `setup`** e **registrada por projeto** em `memory/stack.md` (molde genérico que se adapta ao projeto do dev final). Tudo que a Aliança cria deve ser genérico e adaptável.
- Idioma de trabalho: PT-BR.

## Estrutura atual no disco

```
harness ai/
├─ PROTOCOL.md            ← teoria/spec completa (16 seções)
├─ HANDOFF.md             ← este arquivo
└─ alianca/               ← implementação de referência
   ├─ START-HERE.md       ← ponto de entrada do LLM
   ├─ router.md           ← índice de 15 instruções + gatilhos + precedência
   ├─ instructions/       ← TODAS as 15 prontas ✅
   │   setup · adopt · deep-questions · persona-p0 · testing · code-quality · architecture ·
   │   refactor · bug-prevention · security · interface · snapshot · migration · health-check · agents
   ├─ memory/README.md    ← documenta vision, active-context, stack.md, decisions…
   └─ snapshots/README.md
```

> A **stack não tem pasta**: `memory/stack.md` é gerado por projeto no `setup` (decisão 2.1).

## Estado (o que está pronto)

- ✅ **Fase 1** — espinha operacional (START-HERE, router, estrutura de pastas).
- ✅ **Fase 2** — `setup` (questionário progressivo por persona + rubrica 3 eixos + cálculo de nível) e `deep-questions`.
- ✅ **Fase 3** — backbone (`testing`, `code-quality`, `refactor`, `bug-prevention`, `security`) + `persona-p0`.
- ✅ **Fase 3b** — instruções de sistema (`snapshot`, `migration`, `health-check`).
- ✅ **Fase 4 (revisada → 2.1)** — em vez de "stack packs", a escolha de stack virou responsabilidade da LLM no `setup`, registrada por projeto em `memory/stack.md`. Pasta `stacks/` removida; backbone (`testing`, `code-quality`) re-apontado.
- ✅ **Revisão de arquitetura (2.1)** — após varredura completa: corrigida a memória mínima por nível (Fix #1); removido token `style` órfão (Fix #3); adicionado **módulo `architecture`** (12ª instrução, invariantes de estrutura, sem catálogo); **loop de feedback** (`memory/feedback.md`); **convenções de versionamento** por nível (setup); **recuperação de desastre** (snapshot). Pendência deliberada: calibrar o gatilho `R≥40` (ex.: "login sozinho" = 25) no dogfood.
- **Aliança está conceitualmente fechada** — as 15 instruções existem e estão registradas no router.
- ✅ **2.2 (2026-06-10)** — três adições: (1) módulo **`interface`** (design, ergonomia, acessibilidade — a superfície humana, lacuna do backbone); (2) caminho brownfield **`adopt`** (integrar a Aliança a projetos que já existem: inventário em vez de questionário, persona/nível inferidos da realidade, **migração da memória antiga** para fonte única — adoção é integração/"abraço", não substituição); (3) **forcing function "sempre ligado"** (`setup` Passo 8 + §13): o harness deixa de ser passivo — em Claude Code, kernel no `CLAUDE.md` + hook `UserPromptSubmit` (determinístico) fazem todo prompt passar pelo roteamento sem o usuário precisar lembrar. Invariante novo: **uma só memória de projeto ativa**.
- ✅ **Auto-revisão (2026-06-08)** — corrigida coerência (token `style` órfão, snapshot só a partir do Nível 1, headers de precedência alinhados ao router); completude entregue (B3 separação de ambientes, D3 observabilidade, migração de versão da Aliança, DoD por tarefa via `TASKS.md`, §15 com status); e o **módulo novo `agents`** (quando usar múltiplos agentes). As regras de operação da memória (quando quebrar/consolidar/arquivar) ficaram consolidadas em `memory/README.md` — sem módulo separado, para não colidir com a pasta `memory/`. Pendência deliberada mantida: calibrar o gatilho `R≥40` no dogfood (login=25, pagamentos=30 e regulado=35 ficam abaixo do limiar).
- ✅ **Passe "menos é mais" (2026-06-08)** — sob a régua *arquiteto, não construtor*: enxugado `security` (catálogo OWASP → invariantes), removida a tabela duplicada em `agents` (vira ponteiro p/ §11) e a anti-alucinação repetida em `bug-prevention`; molde de `stack.md` sem viés de ferramenta; `deep-questions` (Risco) sem cardápio de siglas; `snapshots/README` virou ponteiro p/ a instrução. Coerência: `coordinator` unificado (§11), `business-rules`/`security`/`decisions` movidos de `docs/` para `memory/` (Nível 3), gatilho de migração 2→3 corrigido (memória mínima já tem 2 docs), reversibilidade do bootstrap explícita (P0/F2), Nível 0 "invisível" honesto (roda no VERIFICAR).
- ✅ **Modelo de nível e risco (2026-06-08, decisões do usuário)** — §16.2/§16.4/§16.5 fechadas. (1) O nível do `setup` é **estimativa inicial**, não veredito: o harness observa o comportamento real e **reajusta** (sobe/rebaixa) via `migration`/`health-check`; longevidade alta sozinha não infla estrutura. (2) Segurança **proporcional ao risco** (não corte em R≥40): qualquer sinal sensível engaja a base e é **sugerido** ao usuário; `.env` obrigatório sempre que houver credencial; o harness **valida** as boas práticas, não reensina. (3) P0: o LLM **confirma cada decisão estrutural** e pergunta melhor na linguagem do leigo — não assume. (4) Idioma dos artefatos segue o usuário (a LLM já faz). O calibre fino dos pesos segue evoluindo no uso real (sem projeto-exemplo no repo, por decisão).

## Próximos passos (em ordem)

1. **Fase 5 — dogfood:** rodar o `setup` num projeto-exemplo real, ver se a rubrica dá um nível sensato, validar a geração de `memory/stack.md` e **calibrar os pesos** (§4 do PROTOCOL).
2. Pendências menores: validar travessia router→instruções com o `health-check`; conferir que nenhuma instrução ainda referencia `stacks/`.

## Como retomar

1. Leia este HANDOFF.md.
2. Leia `alianca/START-HERE.md` e `alianca/router.md` para o modelo mental.
3. Comece pela Fase 5 (dogfood): rode o `setup` num projeto-exemplo e observe se a rubrica e o `memory/stack.md` saem coerentes.

> A memória persistente (`MEMORY.md` + `projeto-keel-harness-universal.md` no diretório de memória) também reflete este estado.
