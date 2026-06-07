# stacks

**Stack packs** da Aliança. Um pacote aterra o backbone abstrato (testes, qualidade, refatoração, prevenção de bugs) em **ferramentas e comandos concretos** de uma stack específica. É o que faz a Aliança "funcionar de verdade" — sobretudo para o leigo (P0), que não sabe escolher ferramenta.

## O que um pacote fornece

| Item | Exemplo (Next.js) |
|---|---|
| Runner de testes | Vitest / Playwright |
| Linter + formatter | ESLint + Prettier |
| CI | workflow de pipeline (lint + test no push) |
| `.gitignore` + `.env.example` | da stack |
| Comandos concretos | `install`, `dev`, `test`, `lint`, `build` |

## Convenção

- Nome: `<stack>.md` (ex.: `next.md`, `fastapi.md`).
- O `setup` escolhe o pacote pela stack detectada (ou pela decisão do LLM, no caso P0).

> Nenhum pacote criado ainda — o primeiro (provavelmente `next` ou `fastapi`) é a Fase 4.
