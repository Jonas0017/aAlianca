# Aliança (este repo é o desenvolvimento do próprio harness)

Este projeto usa a **Aliança** (harness em `alianca/`) — e é também o produto: aqui a Aliança se constrói usando a si mesma.
Antes de responder QUALQUER prompt:
1. Leia `alianca/router.md` e veja se algum gatilho casa com a ação atual.
2. Siga o loop de `alianca/START-HERE.md §4` (CHECAR→CARREGAR→AGIR→VERIFICAR→PERSISTIR).
Fonte única de memória do projeto: `alianca/memory/`. Não crie/use outra memória de projeto.
O hook `alianca/kernel/route.py` injeta o roteamento determinístico a cada prompt; este arquivo é o reforço sempre-carregado (defesa em profundidade).
Isto não é opcional.
