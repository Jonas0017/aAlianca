# microprojects — memória federada por bounded context

A memória da Aliança é **federada**: além da raiz (`alianca/memory/`), cada
**microprojeto** (bounded context que mereceu memória/agentes próprios) tem a
sua memória local aqui, em `microprojects/<slug>/memory/`. Isso evita que uma
memória plana única inche e sobrecarregue a memória principal.

> Microprojeto é **opt-in** (nível ≥ 2), sempre **PROPOSTO** ao humano, nunca
> automático. Projeto simples (ex.: landing page) segue plano na raiz, como
> antes. A criação é conduzida pela instrução `instructions/microproject.md`.

## Grafo (os dois arquivos de controle)

| Arquivo | Papel |
|---|---|
| `registry.json` | grafo dos microprojetos: `{ "<slug>": { "path", "codeDirs", "status", "hoisted": [] } }`. Nasce `{}`. |
| `ACTIVE` | 1 linha com o slug do escopo ativo; **vazio = raiz**. Sinal em disco lido pelo kernel. |

## Como o kernel resolve o escopo (`kernel/scope.py`)

Precedência em `resolve_scope`: pista `[mp:<slug>]` no prompt **>** match do
`cwd` em `registry.codeDirs` **>** marcador `ACTIVE` **>** raiz. Degrada para a
raiz em **qualquer** erro (fail-open) — o roteamento nunca trava a sessão.

## Estrutura de um microprojeto

```
microprojects/<slug>/
  MICROPROJECT.md          # carta do bounded context (fronteira, dono, objetivo)
  memory/
    active-context.md      # memória local (semeada 1-3 linhas na criação)
    archive/               # fechamento arquiva aqui
  agents/                  # (opcional) agentes locais — convenção de pasta; hoisting no 2º consumidor
  instructions/            # (opcional) instruções locais — compiladas p/ router.index.json local
  router.index.json        # (gerado) índice local; o merge sobrepõe a raiz por nome
  verify.cmd               # (opcional) esteira local, só se o microprojeto tem teste próprio
```

## Invariante (reinterpretada)

"Uma só memória" **não morreu**: virou **uma por ESCOPO ATIVO** — hierárquica,
nunca duas em paralelo; a raiz é o **fallback compartilhado**. O guarda mecânico
é o selftest de integridade do grafo (`kernel/scope.py:validate_graph`): fato
*hoisted* não pode ter conteúdo não-stub no local (anti-duplicação).
