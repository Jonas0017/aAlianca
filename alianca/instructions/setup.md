---
trigger: iniciar um projeto novo (não existe memory/active-context.md)
load-when: bootstrap
applies-to: todas as personas
priority: bootstrap (roda antes de qualquer execução)
---

# setup — bootstrap da Aliança

O momento em que os dois mundos se alinham. Aqui você **não escreve código** — você descobre com quem fala, dimensiona o projeto e gera o harness sob medida. Conduza **uma pergunta por vez**. Nunca despeje o questionário inteiro.

---

## Passo 0 — Pergunta de abertura (classifica a persona)

Faça **exatamente** esta pergunta, neutra:

> "Me conta, numa frase, o que você quer construir — do jeito que você falaria pra um amigo."

Classifique pela resposta:

| Sinais na resposta | Persona |
|---|---|
| Descreve **produto/problema**, sem termos técnicos | **P0 — Leigo** |
| Sabe o básico, hesita em arquitetura | **P1 — Iniciante** |
| Cita **stack, padrões, requisitos não-funcionais** | **P2 — Dev** |
| Menciona **time, clientes, compliance, escala** | **P3 — Time/Org** |

- Se **P0** → carregue também a instrução `persona-p0` e use a linguagem dela a partir daqui.
- A persona pode ser promovida depois; isso redispara o cálculo de nível.

---

## Passo 1 — Triagem (máx. 5 perguntas, uma por vez)

Traduza cada pergunta para a linguagem da persona (versão P0 entre parênteses). Q1 e Q2 dão contexto; Q3–Q5 **pontuam os eixos**.

**Q1 — O que é e que problema resolve.** *(contexto)*
**Q2 — Quem vai usar.** *(contexto)*

**Q3 — Longevidade.** "Quanto tempo isso precisa durar?"

| Resposta | Pontos L |
|---|---|
| Teste/descartável, uso de um dia | 10 |
| Algumas semanas (MVP/protótipo) | 30 |
| Alguns meses, vai evoluir | 55 |
| Anos / várias versões / manutenção contínua | 85 |

**Q4 — Risco.** "Vai lidar com login, dados de pessoas, dinheiro, ou algo sigiloso?" *(pode marcar mais de um; some os pontos, limite 100)*

| Resposta | Pontos R |
|---|---|
| Nada sensível | 0 |
| Login de usuários | +25 |
| Dados pessoais (nome, e-mail, etc. — LGPD/GDPR) | +25 |
| Pagamentos / dados financeiros | +30 |
| Setor regulado (saúde, gov, fintech) | +35 |

**Q5 — Estrutura.** "É uma coisa só, ou várias partes que conversam?" *(P0: "É um site/app simples, ou tem várias telas e um 'cérebro' que guarda informação?")*

| Resposta | Pontos E |
|---|---|
| Uma coisa só, simples | 15 |
| Algumas partes (ex.: tela + um back simples) | 35 |
| Várias partes que conversam / com integrações | 55 |
| Muitos módulos / vários serviços | 80 |

---

## Passo 2 — Banda provisória e aprofundamento

Converta cada eixo em **banda (0–4)**:

```
0–20 → banda 0 | 21–40 → banda 1 | 41–60 → banda 2 | 61–80 → banda 3 | 81–100 → banda 4
```

- **Se qualquer eixo ≥ banda 2** (score ≥ 41) → carregue a instrução `deep-questions` e refine **aquele(s) eixo(s)** com a rubrica detalhada (substitui o score provisório).
- Caso contrário, os scores da triagem são finais.

---

## Passo 3 — Cálculo do Nível

```
nível_base = banda( max(E, L) )
SE R ≥ 40:  nível = min(nível_base + 1, 4)  E  módulos de segurança tornam-se obrigatórios
SENÃO:      nível = nível_base
```

Risco é o eixo dominante: `R ≥ 40` força `memory/security.md` e a instrução `security`, mesmo que E e L sejam baixos.

---

## Passo 4 — Edição (mapeada à persona)

| Persona | Edição | Postura |
|---|---|---|
| P0 / P1 | **Aliança Start** | máxima automação, linguagem humana, LLM decide a stack |
| P2 | **Aliança Pro** | controle total, integra ferramentas do dev |
| P3 | **Aliança Org** | governança, auditoria, múltiplos agents, compliance |

---

## Passo 5 — O que cada Nível gera

> O **backbone** (testes, qualidade, refatoração, prevenção de bugs) existe em **todos** os níveis — só muda a profundidade.

- **Nível 0:** `README.md`, `TASKS.md`. Backbone automático/invisível.
- **Nível 1:** + `ARCHITECTURE.md`. Backbone simples explícito.
- **Nível 2:** `docs/` (`requirements`, `architecture`), `tasks/backlog.md`, `tests/`, CI básico, `memory/` (vision, active-context).
- **Nível 3:** `docs/` (+ `business-rules`, `security` se R≥40, `decisions`), `memory/` segmentada, `tests/` completo, snapshots periódicos. Agents conforme a stack.
- **Nível 4:** + `agents/`, `workflows/`, `security/`, `audits/`, `metrics/`, `governance/`. Time completo de agents + coordinator. Snapshots automáticos.

Escolha o **stack pack** (`stacks/`) pela stack (P2/P3 informam; P0/P1 → você decide e justifica em linguagem simples). Se não houver pacote pronto para a stack, registre como pendência.

---

## Passo 6 — Proposta + dry-run (confirme ANTES de criar)

Apresente um resumo e **peça confirmação** antes de tocar em arquivos:

```
PROPOSTA DE HARNESS — ALIANÇA
Projeto: <nome/descrição>
Persona: <P_>  ·  Edição: <Start/Pro/Org>
Eixos:  Estrutura E=__  ·  Longevidade L=__  ·  Risco R=__
Nível: <0–4>   (regra aplicada: <base | base+1 por risco>)
Stack: <stack pack ou "a definir">
Vou criar: <lista de pastas/arquivos do nível>
Confirma? (sim / ajustar)
```

Para **P0**, traduza isso para linguagem humana (ver `persona-p0`): "Vou montar X, Y e Z pra você. Pode ser?"

---

## Passo 7 — Gerar e registrar

Após o "sim":

1. Crie a estrutura do nível.
2. Escreva `memory/vision.md` (o quê, persona, problema, usuários) e `memory/active-context.md` (estado inicial, próximos passos).
3. Gere o **snapshot inicial** em `snapshots/snapshot-AAAA-MM-DD-setup.md`.
4. Ative o stack pack escolhido (instale/configure ferramentas; ver `stacks/`).
5. Configure higiene mínima: `.gitignore` + `.env.example` (nível ≥ 1).
6. Atualize o `router.md` se alguma instrução passou a ser relevante para este projeto.

A partir daqui, siga o **loop de operação** do `START-HERE.md`.
