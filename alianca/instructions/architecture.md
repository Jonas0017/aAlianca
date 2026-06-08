---
trigger: criar ou alterar a estrutura do projeto — novo módulo, nova camada, fronteira, ou decisão de dependência
load-when: execução
applies-to: todos os níveis (a profundidade escala; em níveis baixos, mantenha simples)
priority: architecture (abaixo de testing, acima de refactor)
---

# architecture — invariantes de estrutura

A Aliança **não** traz catálogo de padrões — você (LLM) já conhece camadas, hexagonal, eventos, e escolhe o que cabe no projeto. Este módulo é o oposto de uma enciclopédia: são as **regras invariantes** que mantêm a estrutura sã, **qualquer que seja o padrão escolhido**.

## Invariantes (valem em qualquer arquitetura)

- **Dependa para dentro.** O detalhe (UI, banco, framework, API externa) depende da regra de negócio — nunca o contrário. A regra não conhece o detalhe.
- **Fronteira segue responsabilidade.** Um módulo = uma razão para mudar. Se duas partes mudam por motivos diferentes, separe (casa com o eixo **Estrutura** do `setup`).
- **A estrutura mais simples que cabe no nível.** Não introduza camada, abstração ou serviço antes da dor existir. Sobre-arquitetar é dívida tão cara quanto não arquitetar — sobretudo em P0 / níveis baixos.
- **Acoplamento baixo, coesão alta.** O que muda junto fica junto; o que é independente não se enrosca.
- **Um sentido de fluxo.** Evite dependência circular entre módulos.

## Ao decidir estrutura

- Toda decisão estrutural **significativa** (escolher/trocar padrão, criar camada, definir fronteira de serviço) vira registro: um **ADR** em `memory/decisions/` (nível ≥ 3) ou uma nota em `ARCHITECTURE.md` (níveis 1–2) — **o quê, por quê, e a alternativa descartada**.
- Mantenha a arquitetura vigente em `memory/architecture.md` (nível ≥ 2); o `snapshot` aponta para ela.
- A estrutura é reavaliada na `migration`: se o eixo Estrutura cresceu, **suba de nível antes** de inchar pastas no nível errado.

## Segurança da mudança estrutural

- **Só reestruture sob testes verdes** (ver `testing`); a separação de módulos é uma refatoração — comportamento idêntico antes e depois (ver `refactor`).
- Mudança de estrutura e mudança de comportamento em **commits separados**.

## Profundidade por nível

| Nível | Estrutura |
|---|---|
| 0–1 | uma estrutura óbvia e plana; sem camadas cerimoniais. Decisão anotada em `ARCHITECTURE.md`, se houver. |
| 2–3 | fronteiras de módulo explícitas; `docs/architecture.md` + ADRs em `memory/decisions/`. |
| 4 | arquitetura governada; revisão por marco; agente **Architect** (ver PROTOCOL §11). |

## Para P0 (leigo)

Não exponha o termo. Escolha a estrutura mais simples que resolve e siga em frente. Se precisar separar algo, traduza: "vou organizar isso em duas partes, pra cada uma fazer bem o seu trabalho — sem mudar nada do que você vê."
