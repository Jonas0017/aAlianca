---
trigger: detectar duplicação (3x), função longa demais, ou módulo com responsabilidades misturadas
load-when: execução
applies-to: todos os níveis
priority: refactor — 5ª na ordem do router (abaixo de architecture, acima de code-quality)
---

# refactor — refatoração contínua

Dívida técnica se paga em parcelas pequenas e frequentes, nunca num "grande refactor" no fim. Melhore o terreno por onde você passa.

## Gatilhos concretos

- **Regra de três:** duplicou pela 3ª vez → extraia uma abstração.
- **Função longa / muitos parâmetros / aninhamento profundo** → divida.
- **Nome que mente** (faz mais do que diz) → renomeie ou separe.
- **Responsabilidades misturadas** num mesmo módulo → separe por responsabilidade.

## Regras de segurança

- **Só refatore sob testes verdes.** Sem teste cobrindo, escreva o teste **primeiro** (ver `testing`), depois refatore.
- **Passos pequenos.** Uma transformação por vez; rode os testes entre elas.
- **Refatoração e feature em commits separados.** Nunca misture mudança de comportamento com reorganização — fica impossível revisar.
- Comportamento **idêntico** antes e depois: refatorar não muda o que o código faz.

## Dívida técnica por nível

| Nível | Tratamento |
|---|---|
| 0–1 | aplicar a regra de três no momento; sem rastreio formal |
| 2–3 | revisar dívida a cada marco; anotar pendências em `tasks/` |
| 4 | orçamento de dívida rastreado em `metrics/`; itens com dono e prazo |

## Para P0 (leigo)

Não exponha o termo. Se uma refatoração for necessária antes de avançar, traduza: "Vou organizar uma parte por dentro pra ficar mais fácil de crescer — sem mudar nada do que você vê."
