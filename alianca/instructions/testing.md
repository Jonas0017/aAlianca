---
trigger: criar ou alterar lógica testável (função, regra de negócio, endpoint, componente)
keywords: teste, testes, testar, testavel, tdd, cobertura, spec, unitario, integracao, regressao, mock, assert, pytest, jest, vitest, unittest, endpoint, componente
load-when: execução
applies-to: todos os níveis (profundidade escala com o nível)
priority: testing — 3ª na ordem do router (abaixo de bug-prevention, acima de architecture)
---

# testing — a esteira de testes

Teste não é opcional. É o que separa "achei que funciona" de "funciona". A esteira existe em **todo** projeto; só a profundidade varia.

## Regra de ouro

- **Nada é "feito" sem teste verde.** Faz parte da Definition of Done.
- **Rode os testes e relate a saída real.** Nunca afirme que passou sem executar (anti-alucinação).
- **Nunca apague ou pule (`skip`/`xfail`) um teste para ficar verde.** Conserte a causa raiz. Se um skip for inevitável, registre o motivo e a condição de remoção.

## Esteira desde o onboarding (obrigatória e verificada)

A esteira nasce no **bootstrap**, não "depois que der". Isto não pode falhar:

- **Projeto em andamento (`adopt`):** monte a esteira **completa já**, casada ao que o inventário revelou (runner/framework detectado). Há testes? Faça-os rodar. Não há? Crie o mínimo do nível. Nunca deixe o projeto sem esteira "pra depois".
- **Projeto novo (`setup`):** **entenda primeiro** (persona, eixos, stack — Passos 0–3), **depois** crie a esteira do nível. A ordem importa: sem entender o projeto, a esteira sai errada.
- **Arme o portão:** aponte **`alianca/kernel/verify.cmd`** para o comando de teste do projeto (de `memory/stack.md`). Sem esse arquivo, o 3º portão (`verify.py`) fica **inerte** e ninguém cobra o verde — é a causa nº1 de "passou sem rodar".
- **Prova (a trava):** o bootstrap **não fecha** enquanto `verify.cmd` não rodar e voltar **verde**. Se algo real impede (ex.: legado sem como testar ainda), o motivo é **registrado** e vira tarefa *A fazer* — nunca silêncio, nunca "depois" implícito.

## O que testar

- **Comportamento, não implementação.** Teste o que a função promete, não como ela faz.
- **Caminhos de erro e bordas:** entrada vazia, nula, limite, inválida; falha de dependência externa.
- Escreva o teste **junto** com o código (ou antes, quando o comportamento estiver claro).

## Profundidade por nível

| Nível | Esteira |
|---|---|
| 0–1 | smoke test mínimo: o app sobe / a função principal responde. Roda local. |
| 2–3 | unit + integração; CI roda a cada push; testes para cada regra de negócio. |
| 4 | + e2e, **cobertura mínima exigida** (gate de PR), testes de carga e de segurança. |

## Convenções

- Runner e comandos concretos vêm de **`memory/stack.md`** (gerado no `setup` para este projeto). Siga-os.
- Teste isolado e determinístico: sem depender de ordem, rede real ou estado compartilhado (use fakes/fixtures).
- Um teste que falha deve apontar **claramente** o que quebrou.

## Para P0 (leigo)

Os testes rodam invisíveis. Não peça a ele para gerenciá-los; apenas garanta que existam e relate "está tudo funcionando como esperado" quando verdes.
