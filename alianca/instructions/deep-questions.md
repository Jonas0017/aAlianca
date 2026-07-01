---
trigger: a triagem do setup indicou algum eixo ≥ banda 2 (score ≥ 41)
keywords: triagem, aprofundamento, deep questions, banda 2, eixo critico
load-when: bootstrap
applies-to: níveis ≥ 2
priority: bootstrap (logo após a triagem do setup)
---

# Deep Questions — aprofundamento condicional

Refina **apenas o(s) eixo(s)** que a triagem marcou como ≥ banda 2. Cada resposta produz um score preciso que **substitui** o provisório da triagem. Continue uma pergunta por vez; adapte a linguagem à persona.

---

## Se Estrutura (E) ≥ banda 2 — refine E (0–100)

Some os fatores e normalize para 0–100 (limite 100):

| Fator | Pergunta | Pontos |
|---|---|---|
| Módulos/serviços | "Quantas partes independentes terá?" | 1 → 0 · 2–3 → 15 · 4–6 → 30 · 7+ → 45 |
| Camadas | "Tem frontend, backend, mobile, infra cloud?" | +10 por camada além da 1ª (máx +30) |
| Integrações externas | "Vai conversar com serviços de terceiros/APIs?" | 0 · 1–2 → 5 · 3–5 → 12 · 6+ → 20 |
| Persistência | "Guarda dados? Como?" | nenhuma 0 · arquivo/KV +2 · relacional +6 · distribuída +10 |

---

## Se Risco (R) ≥ banda 2 — confirme e detalhe R

Reconfirme os itens da triagem (login, dados pessoais, pagamentos, regulado) e aprofunde só o que **move a decisão**:

- **Que categorias de dado sensível** entram (pessoal, financeiro, saúde, credencial)?
- **Há norma regulatória específica** aplicável? Qual?

> Mantenha a pontuação R da triagem (soma dos fatores, limite 100). Estas respostas alimentam `memory/security.md` e o conteúdo da instrução `security`.

---

## Se Longevidade (L) ≥ banda 2 — refine L

- **Versionamento:** haverá releases/versões? Suporte a versões antigas?
- **Evolução:** o escopo deve crescer? Em que ritmo?
- **Equipe/conhecimento:** mais devs vão entrar? A documentação precisa preservar conhecimento?

> Ajuste L dentro da sua faixa (meses 41–70 · anos/contínuo 71–100) conforme intensidade de evolução e necessidade de preservar conhecimento.

---

## Se persona P2/P3 — questões técnicas

- Stack e versões já decididas?
- Padrões arquiteturais preferidos (camadas, hexagonal, eventos…)?
- CI/CD e ferramentas já em uso (para a Aliança integrar, não substituir)?
- Requisitos não-funcionais (latência, disponibilidade, escala)?

---

## Saída

Devolva os scores **finais** de E, L e R ao Passo 3 do `setup` para o cálculo do nível.
