---
trigger: começar uma frente nova e INDEPENDENTE (bounded context) que merece memória/agentes próprios — nunca automático, sempre PROPOSTO ao humano
keywords: microprojeto, microprojetos, bounded context, subsistema, dominio, federar, federada, contexto delimitado, memoria federada
load-when: evolução
applies-to: níveis ≥ 2
priority: lifecycle (fora da ordem de precedência de código)
---

# microproject — memória federada por bounded context

Uma memória plana única incha e sobrecarrega a memória principal. A saída é
**federar**: quando o projeto cria uma frente **independente** (um *bounded
context* com fronteira, dono e objetivo próprios), essa frente ganha **memória
local** em `alianca/microprojects/<slug>/memory/` — e a raiz (`alianca/memory/`)
vira o **fallback compartilhado**.

## Princípios (não reabra)

- **Opt-in, nível ≥ 2, sempre PROPOSTO.** Projeto simples (uma landing page, um
  script) segue plano na raiz, como antes. Nunca crie microprojeto sozinho.
- **Nasce LOCAL.** Todo fato começa na memória do microprojeto. A raiz só
  recebe o **compartilhável** — e só pela **regra do 2º consumidor** (hoisting,
  abaixo).
- **Fronteira = bounded context**, não a árvore de código. A memória mora em
  `microprojects/<slug>/memory/`, **não** espelha a estrutura de pastas do
  código; `codeDirs` no registry só serve de pista de escopo pelo `cwd`.
- **Uma memória por ESCOPO ATIVO** (hierárquica, nunca duas em paralelo). É a
  invariante do `START-HERE §5` reinterpretada.

## Ligação com o ciclo de vida (REGRA travada)

- **Nenhum projeto nasce federado.** Todo projeto começa **PLANO** (memória
  única na raiz) via `setup` (novo) ou `adopt` (existente) — **mesmo um sistema
  grande**. Federa-se **só** quando o gatilho acima dispara (a memória plana já
  mistura **≥ 2 bounded contexts** independentes). É YAGNI: a **estrutura
  acompanha a dor**, não a antecipa (coerente com o `load-when: evolução` deste
  módulo). Federar no bootstrap é overhead sem independência real — dívida.
- **Handoff plano → federado.** O `migration` detecta o inchaço (≥ 2 bounded
  contexts no `active-context.md`) e **entrega o gatilho + o "sim" do humano**;
  o `microproject` **recebe** e extrai o **1º bounded context** da memória plana:
  move aquela fatia de `alianca/memory/` para `microprojects/<slug>/memory/` e
  deixa a raiz como **fallback compartilhado**. A operação é **aditiva e
  reversível** — o conhecimento se **move**, não se perde; concluir/rebaixar
  arquiva de volta (§CONCLUIR). Nada é apagado.

## Quando PROPOR (gatilho)

Uma frente que satisfaz **todos**: (a) é **independente** (fronteira clara, pouco
acoplada ao resto); (b) vai **acumular memória própria** (decisões, contexto,
tarefas que não interessam ao resto); (c) idealmente terá **agentes/esteira
próprios**. Sinais típicos: um novo subsistema/domínio, uma integração externa
grande, ou a memória plana já mistura **≥ 2 bounded contexts** no
`active-context.md` (ver `migration`).

> Se é só "mais um arquivo" do mesmo contexto, **não** é microprojeto — é plano
> na raiz. Overhead de federação sem independência real é dívida.

## Anatomia de um microprojeto (árvore completa)

Tudo vive sob `alianca/`. Os **dois arquivos de controle** ficam na raiz de
`microprojects/`; cada slug é uma pasta:

```
alianca/microprojects/
  registry.json            # grafo de TODOS os microprojetos (compartilhado). Nasce {}
  ACTIVE                   # 1 linha: slug do escopo ativo (vazio = raiz)
  <slug>/
    MICROPROJECT.md        # carta do bounded context (template abaixo)
    memory/
      active-context.md    # memória local (semeada 1–3 linhas na criação)
      archive/             # §CONCLUIR arquiva aqui — nunca apaga
    agents/                # (opcional) agentes locais deste contexto — ver abaixo
    instructions/          # (opcional) módulos locais; compilados p/ o índice local
    router.index.json      # (gerado por compile.py) índice local; merge sobrepõe a raiz por nome
    verify.cmd             # (opcional) esteira local; só se há teste próprio
```

## Procedimento — CRIAR (após o "sim" do humano)

1. **Derive o `slug`** do **nome do bounded context**, não da árvore de código:
   minúsculas, ASCII, espaços/acentos → `kebab-case`, sem stopwords, curto e
   estável (ex.: "Gateway de Pagamento" → `pagamento`; "Busca full-text" →
   `busca`). **Cheque UNICIDADE** contra as chaves já existentes em
   `registry.json`: se o slug colidir, **não reuse** — desambigue com um
   qualificador do contexto (`pagamento` → `pagamento-pix`) ou encurte por outro
   eixo; nunca sufixe com número (`pagamento-2` não diz nada). Slug é chave
   primária do grafo: colisão silenciosa mistura duas memórias.
2. **Crie a estrutura** (árvore acima). Mínimo obrigatório:
   - `MICROPROJECT.md` — a carta do bounded context (template na seção abaixo).
   - `memory/active-context.md` — **semeado com 1–3 linhas** (estado inicial +
     próximo passo). Não deixe vazio: memória vazia não é bootstrap.
3. **Registre no grafo** `alianca/microprojects/registry.json`:
   ```json
   "<slug>": { "path": "microprojects/<slug>", "codeDirs": [], "status": "ativo", "hoisted": [] }
   ```
   - `codeDirs`: as pastas de código do contexto (pista de `cwd` p/ `scope.py`),
     se houver — **lista de strings**, `[]` quando nenhuma.
   - `hoisted`: **começa `[]`** (array vazio) e só ganha elementos quando um fato
     sobe pela regra do 2º consumidor; **cada elemento é um objeto**
     `{ "fact", "to", "stub" }` (formato na §hoisting) — nunca uma string solta.
4. **Ative o escopo:** escreva `<slug>` (1 linha) em `alianca/microprojects/ACTIVE`.
5. **Agentes locais (opcional):** se o contexto pede um agente/persona próprio,
   crie-o em `microprojects/<slug>/agents/` (ver §Agentes locais).
6. **Esteira:** herda a raiz por padrão. Crie `microprojects/<slug>/verify.cmd`
   **só** se o microprojeto tem teste próprio — e então ele **precede** o
   `verify.cmd` da raiz no escopo ativo (§Precedência local).
7. **Instruções locais (opcional):** se o contexto precisa de módulos próprios,
   crie `microprojects/<slug>/instructions/*.md` e rode
   `python alianca/kernel/compile.py` (gera o `router.index.json` local; o merge
   sobrepõe a raiz por nome — §Precedência local).
8. **Snapshot inicial** do microprojeto (ver `snapshot`).

## MICROPROJECT.md (template)

A carta do bounded context — enxuta, uma tela. Copie e preencha:

```markdown
# <slug> — <nome do bounded context>

**Fronteira:** <o que este contexto É; onde começa e termina>
**Dono/persona:** <humano ou agente responsável>
**Objetivo:** <o resultado que este contexto entrega, em 1 frase>

**Fora do escopo:** <o que explicitamente NÃO é responsabilidade daqui>

**codeDirs:** <pastas de código que pertencem ao contexto — espelha o registry>

**Stack local (SÓ se divergir da raiz):** <ferramenta/comando que difere do
memory/stack.md da raiz; omita esta linha se herda a stack da raiz sem
divergência — não repita o que já vale globalmente>
```

> A **stack local só existe quando diverge** da raiz (ex.: este contexto usa
> outro runner de teste). Se não diverge, **não escreva** — herdar é o default;
> duplicar a stack da raiz é ruído que envelhece.

## Agentes locais (resolução e hoisting)

- **Onde vivem:** `microprojects/<slug>/agents/` (um arquivo por agente/persona).
  Agente de um contexto só nasce **local**, como a memória.
- **Como são resolvidos — por CONVENÇÃO de pasta, não por código.** Seja honesto:
  `scope.py` resolve o **escopo de memória** e faz o **merge de índices de
  instruções** (`merge_indices`, local sobrepõe a raiz por nome), mas **não**
  tem resolução de agentes embutida. A escolha é do **gerente** (`route`), por
  convenção: dado o escopo ativo, procure o agente **local → raiz → genérico** —
  primeiro `microprojects/<slug>/agents/`, senão `alianca/agents/`, senão o
  comportamento genérico do gerente. O local de mesmo papel **sobrepõe** o da
  raiz (mesma regra do índice).
- **Hoisting de agente (regra do 2º consumidor):** quando um **segundo**
  microprojeto passa a precisar do mesmo agente, **promova-o** para
  `alianca/agents/` (vira compartilhado) e registre o porquê em
  `memory/decisions/` — idêntico ao hoisting de fato. Um consumidor só não
  justifica subir (YAGNI).

## Precedência local (escopo ativo > raiz)

No escopo de um microprojeto ativo, o **local precede a raiz** em tudo que
existir localmente, com a raiz como **fallback compartilhado**:

- **Instruções:** o `router.index.json` local sobrepõe a raiz **por nome de
  módulo** (`scope.py:merge_indices`); módulo só-raiz continua visível.
- **Esteira:** `verify.cmd` local (se existir) manda no escopo ativo; sem ele,
  cai na esteira da raiz.
- **Agentes:** local → raiz → genérico (§Agentes locais).

## Regra de hoisting (promover LOCAL → RAIZ) — só no 2º consumidor

Um fato só sobe para a raiz quando um **segundo** escopo precisa dele (YAGNI: um
consumidor só não justifica compartilhar). Ao promover:

1. **Mova o conteúdo** para a raiz (o arquivo de destino em `alianca/memory/`,
   normalmente um ADR em `alianca/memory/decisions/`).
2. **Deixe um STUB no local** — um ponteiro curto, **não** o conteúdo. O stub
   contém o marcador `hoisted` e aponta para o destino raiz. Nunca duplique: o
   selftest (`kernel/scope.py:validate_graph`) falha se o local tiver conteúdo
   não-stub.
   ```markdown
   > hoisted -> alianca/memory/decisions/<adr>.md (promovido no 2º consumidor)
   ```
3. **Registre a aresta** em `registry.json` do microprojeto, campo `hoisted`:
   ```json
   { "fact": "<slug-do-fato>", "to": "memory/decisions/<adr>.md", "stub": "microprojects/<slug>/memory/<arquivo>.md" }
   ```
4. **Escreva um ADR curto** em `alianca/memory/decisions/` registrando o quê e o
   porquê da promoção.

## Procedimento — CONCLUIR (poda / consolidação)

Ao fechar o microprojeto:

1. **Consolide** a memória local (funda anotações soltas, elimine ruído).
2. **Hoisting final:** promova para a raiz o que ficou **compartilhável** (regra
   do 2º consumidor), deixando stubs.
3. **Snapshot de fechamento** (estado final + como retomar).
4. **Arquive** a memória local em `microprojects/<slug>/memory/archive/` — nunca
   apague (conhecimento se move, não se perde).
5. **Atualize o registry**: `status: "concluido"` (ou `"arquivado"`).
6. **Limpe o `ACTIVE`** (esvazie → volta para a raiz).

## Para P0 (leigo)

Invisível. Não exponha "microprojeto/bounded context"; apenas relate o produto.
