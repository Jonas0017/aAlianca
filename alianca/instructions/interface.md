---
trigger: criar ou alterar qualquer superfície que um humano vê ou usa — tela, página, layout, componente, formulário, fluxo, CLI/TUI, texto de interface ou mensagem de erro
load-when: execução
applies-to: todos os níveis (a profundidade escala); qualquer superfície humana, gráfica ou não
priority: interface — junto ao code-quality, é o piso da superfície que o humano usa; acessibilidade não cede a estilo
---

# interface — design, ergonomia e acessibilidade

A Aliança **não** traz catálogo de telas, paleta ou framework de UI — você (LLM) já conhece os padrões e a stack escolhida (`memory/stack.md`). Este módulo é o oposto de uma enciclopédia: são as **regras invariantes** que mantêm a superfície humana usável, **qualquer que seja o meio** (web, app, desktop, CLI, TUI, voz).

## Invariantes — acessibilidade (não é opcional)

É o análogo do `security` para quem usa: nunca sacrificada por estilo ou pressa.

- **Operável sem depender de um único meio.** Funciona por teclado, não só mouse/toque; **foco visível** em onde se está.
- **Contraste suficiente** entre texto e fundo; legível por quem enxerga pouco.
- **Não comunique só por cor.** Erro/estado também por texto, ícone ou forma — daltonismo existe.
- **Alternativa textual** para conteúdo não-textual (rótulo, legenda, texto alternativo) — leitor de tela depende disso.
- **Estrutura semântica correta** (títulos, hierarquia, rótulos associados ao campo), não só aparência.
- **Respeite as preferências do sistema** do usuário: tema, movimento reduzido, tamanho de fonte, idioma.
- **Alvos de toque/clique** grandes o suficiente para errar pouco.

## Invariantes — ergonomia (heurísticas atemporais)

- **Todo ato tem resposta.** O sistema sempre diz o que aconteceu; nada de ação muda sem sinal.
- **Cubra os estados, não só o caminho feliz:** carregando, vazio, erro, sucesso, sem permissão.
- **Prevenir erro > tratar erro.** Confirme o que é destrutivo/irreversível; ofereça **desfazer** quando der.
- **Mensagem de erro útil:** o que houve **e** como resolver, na linguagem de quem usa — nunca código cru ou stack trace na cara do usuário (e sem vazar dado sensível — ver `security`).
- **Consistência:** a mesma coisa tem o mesmo nome, lugar e comportamento. **Reconhecer > lembrar** — mostre as opções, não exija memória.
- **Controle de quem usa:** dá para cancelar, voltar, sair.
- **Padrão conhecido > invenção.** Reaproveite convenções e componentes prontos antes de criar o seu — é o "usa o que já existe" (`architecture`) aplicado à experiência.

## Invariantes — layout e hierarquia

- **Hierarquia clara:** o mais importante salta primeiro; um só foco por tela/passo.
- **Agrupe o relacionado** (proximidade), **alinhe**, e use **espaço em branco** como ferramenta — não encha.
- **Adapte-se ao tamanho e contexto** da tela/janela (fluido, não quebrado no celular).
- **Legibilidade:** tamanho de fonte, comprimento de linha e espaçamento que cansam pouco.

## Sistema e reuso

Valores de cor, espaçamento e tipografia repetidos à mão são o "número mágico" da interface: extraia para **tokens/componentes reutilizáveis** e use a biblioteca da stack antes de reinventar. Reaproveitar > reinventar (ver `code-quality`, `architecture`).

## Gates por nível

| Nível | Gate |
|---|---|
| 0–1 | acessibilidade básica (contraste, teclado, rótulos, alternativa textual); estados carregando/vazio/erro; usar componentes/padrões prontos da stack |
| 2–3 | tokens/sistema de design; checagem de acessibilidade no review de PR; testar em telas e dispositivos diferentes |
| 4 | auditoria de acessibilidade como gate bloqueante (padrão reconhecido, ex.: WCAG); teste com usuário real e leitor de tela; design system versionado |

## Verificação (antes de dizer "ficou bom")

Não declare uma superfície pronta sem **observá-la renderizada** (casa com os rituais de verificação do backbone): veja a tela real, navegue por teclado, confira o contraste e os estados de erro/vazio. "Parece certo no código" não é ter visto.

## Para P0 (leigo)

Não exponha "acessibilidade" nem "UX". Ele quer que **funcione pra todo mundo e seja fácil de usar**. Garanta o piso por baixo (contraste, teclado, mensagens claras, funciona no celular) e, antes de fechar, **mostre o visual e confirme** em linguagem dele — "ficou assim, pode ser?" (casa com o bootstrap reversível do `setup`).
