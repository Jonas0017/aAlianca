---
trigger: revisar a saúde do harness (periódico, ao retomar, ou sob demanda)
load-when: review
applies-to: níveis ≥ 2 (recomendado a qualquer nível ao retomar)
priority: lifecycle (fora da ordem de precedência de código)
---

# health-check — autovalidação do harness

Verifica se o harness está íntegro e coerente com o projeto real. Rode periodicamente, ao retomar uma sessão, ou quando algo parecer fora do lugar.

## Checklist

**Integridade estrutural**
- [ ] Toda instrução listada no `router.md` existe em `instructions/`? (sem ponteiro quebrado)
- [ ] Toda instrução em `instructions/` está registrada no `router.md`?
- [ ] Existe `START-HERE.md`, `router.md` e `memory/active-context.md`?

**Memória**
- [ ] Algum arquivo de `memory/` está grande/duplicado demais? → consolidar/dividir.
- [ ] `active-context.md` reflete o estado real (não está defasado)?
- [ ] Há um `snapshot` recente o suficiente para retomar?

**Coerência de nível**
- [ ] O nível declarado bate com os eixos reais hoje? → se não, dispare `migration`.

**Backbone**
- [ ] Testes verdes? (rode e observe — não presuma)
- [ ] Lint limpo?
- [ ] Nenhum segredo commitado? (ver `security`)
- [ ] Docs/memória batem com o comportamento atual do código?

## Saída — relatório de saúde

```
HEALTH-CHECK — <projeto> — AAAA-MM-DD
Estrutura:  OK | <problemas>
Memória:    OK | <problemas>
Nível:      coerente | sugerir migração para N
Backbone:   testes <verde/vermelho> · lint <ok/x> · segredos <ok/x>
Ações:      <lista priorizada do que corrigir>
```

## Score (opcional, níveis ≥ 3)

Componha um índice simples de saúde a partir de: recuperabilidade (snapshot fresco), frescor da memória, cobertura de teste, defasagem de docs. Use para acompanhar tendência ao longo do tempo, não como número absoluto.

## Para P0 (leigo)

Traduza o relatório para uma frase: "Dei uma revisada geral — está tudo saudável" ou "Achei 2 coisas pra ajustar, já cuido delas."
