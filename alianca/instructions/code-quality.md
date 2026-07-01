---
trigger: antes de commit, ao abrir PR, ou ao finalizar um bloco de código
keywords: commit, commitar, lint, linter, formatar, formatacao, estilo, style, padrao, padroes, qualidade, precommit, gitignore
load-when: review
applies-to: todos os níveis (gates escalam com o nível)
priority: code-quality — última na ordem do router; é o piso (inclui estilo/formatação)
---

# code-quality — qualidade de código

Código é lido muito mais vezes do que escrito. Otimize para o próximo humano (ou LLM) que vai mexer nele.

## Sempre

- **Formatter + linter** rodando, com os comandos de **`memory/stack.md`**. Código formatado antes de commitar.
- **Escreva como o código ao redor.** Combine naming, estilo e idiomas do arquivo/projeto — não imponha o seu.
- **Nomes claros** > comentários. Variáveis e funções dizem o que são.
- **Funções pequenas, uma responsabilidade.** Se precisa de "e" para descrever o que faz, divida.
- **Comentários explicam o "porquê"**, não o "o quê". Sem código morto/comentado — apague (o histórico guarda).
- **Sem números/strings mágicos** — extraia para constantes nomeadas.

## Gates por nível

| Nível | Gate |
|---|---|
| 0–1 | formatter + linter com defaults; rodar antes de commit |
| 2–3 | regras de projeto definidas; **pre-commit hook**; review de PR |
| 4 | + análise estática, limite de complexidade ciclomática, gate bloqueante no PR |

## Antes de fechar (checklist rápido)

- [ ] Lint limpo e formatado.
- [ ] Nomes legíveis; sem código morto.
- [ ] Sem segredo hardcoded (ver `security`).
- [ ] Testes verdes (ver `testing`).
- [ ] Docs/memória atualizados se o comportamento mudou.
- [ ] Consultei `memory/feedback.md` — não repeti um erro já registrado. Se errei algo **de novo**, adicionei a regra lá.

## Para P0 (leigo)

Isso é invisível para ele. Apenas mantenha o padrão — é o que evita que o projeto vire um emaranhado difícil de evoluir depois.
