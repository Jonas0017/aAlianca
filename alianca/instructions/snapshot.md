---
trigger: antes de uma tarefa grande/multi-etapa, ao concluir um marco, ou quando a sessão fica longa
keywords: snapshot, snapshots, retomada, ponto de retomada, marco concluido, retomar o projeto, salvar o contexto, sessao longa
load-when: execução
applies-to: níveis ≥ 1
priority: lifecycle (fora da ordem de precedência de código)
---

# snapshot — pontos de retomada

Um snapshot é um documento **autocontido** que permite outra sessão (outro modelo, outra ferramenta, contexto zerado) retomar o projeto **sem nenhum acesso ao histórico anterior**. É o seguro contra perda de contexto.

## Quando gerar

- **Antes** de iniciar uma tarefa grande/arriscada (para ter um ponto de retorno).
- **Ao concluir** um marco.
- Quando a **sessão fica longa** e há risco de compactação/corte — gere e ofereça nova sessão.
- No nível 4: automático a cada marco.

## Conteúdo obrigatório

```markdown
# Snapshot — <projeto> — AAAA-MM-DD

## Estado atual
<onde o projeto está agora, em 3–6 linhas>

## Arquitetura vigente
<resumo; ponteiros para memory/architecture.md>

## Decisões vigentes
<lista curta; ponteiros para memory/decisions/>

## Em andamento
<o que está aberto/no meio>

## Próximos passos
<lista concreta e ordenada — o suficiente para alguém continuar sozinho>

## Como retomar
<qual instrução/arquivo abrir primeiro>
```

## Regras

- **Autossuficiente:** se você precisaria do histórico para entender, o snapshot está incompleto.
- Nome: `snapshots/snapshot-AAAA-MM-DD-<slug>.md`. Se houver mais de um no mesmo dia/slug, acrescente um sufixo (`-2` ou a hora `-HHMM`).
- O mais recente é a **fonte de verdade** para retomada (ver `START-HERE.md` §2).
- Ao gerar, **atualize também `memory/active-context.md`** para apontar ao snapshot.

## Handoff de contexto

Quando a sessão estiver pesada: gere o snapshot, salve o essencial na memória e diga ao usuário, em uma linha, **como continuar numa nova sessão** ("abra uma nova conversa e diga: continue a partir do snapshot mais recente").

## Recuperação de desastre

Se a memória corromper, a sessão sair dos trilhos, ou você chegar a um projeto sem saber o estado, **reconstrua** — não adivinhe:

1. Leia o **snapshot mais recente** em `snapshots/` (fonte de verdade do estado).
2. Cruze com `memory/decisions/` (o porquê das escolhas) e `memory/active-context.md` (o que estava em andamento).
3. Confirme o estado real **contra o código e o histórico de versão** — não confie só na memória; o que a memória diz e o repositório contradiz, o repositório vence (e você corrige a memória).
4. Rode o `health-check` para validar integridade antes de retomar.
5. Registre o que reconstruiu em `active-context.md` e gere um novo snapshot.

Princípio: o estado essencial vive em disco e é **redundante** (snapshot + decisions + código). Qualquer uma das fontes sozinha já permite recomeçar.
