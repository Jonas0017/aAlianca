# instructions

Módulos de instrução da Aliança. Cada arquivo `.md` aqui é carregado **sob demanda** pelo `../router.md`, no momento em que seu gatilho ocorre — nunca todos de uma vez.

## Regra

- Toda instrução segue o **contrato de cabeçalho** definido em `../router.md` (`trigger`, `load-when`, `applies-to`, `priority`).
- Ao adicionar uma instrução, **registre-a no `../router.md`** e atualize o status para ✅.

## Estado atual

- ✅ Bootstrap: `setup` · `deep-questions` · `persona-p0`
- ✅ Backbone: `testing` · `code-quality` · `refactor` · `bug-prevention` · `security` · `architecture`
- ✅ Sistema: `snapshot` · `migration` · `health-check`
- ✅ Operação: `agents` (múltiplos agentes)

**Todas as 13 instruções estão prontas.** A Aliança está conceitualmente fechada. A stack do projeto não vive aqui: a LLM a decide no `setup` e registra em `memory/stack.md`. Próximo passo é o **dogfood** (rodar o `setup` num projeto real e calibrar a rubrica).
