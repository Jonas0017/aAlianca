---
trigger: você vai perguntar algo sobre o projeto ao usuário, OU o usuário adiou uma resposta ("responde depois"), OU uma pergunta em aberto foi respondida
keywords: pergunta, perguntas, responde depois, respondo depois, pergunta em aberto, perguntas abertas, duvida registrada
load-when: execução
applies-to: todos os níveis (qualquer nível, sob demanda)
priority: fora da ordem de precedência — módulo de ciclo de vida (coordena o trabalho, não compete com os módulos de código)
---

# questions — perguntas sobre o projeto

> Toda pergunta sua sobre o projeto fica **registrada**, não só dita no chat. Uma pergunta dita e esquecida é contexto perdido; uma pergunta adiada ("responde depois") sem registro vira uma decisão tomada às escuras. Este módulo garante que nenhuma se perca e que a resposta vire conhecimento.

## Por que registrar

Uma pergunta em aberto quase sempre **bloqueia** algo — uma decisão de escopo, de arquitetura, de stack. Se ela só existe no histórico do chat:

- some quando a sessão troca ou o contexto compacta (viola "estado vive em disco", `START-HERE` §5);
- o agente repergunta o que já perguntou, ou pior, **assume** e segue (alucinação);
- quando o usuário pede "responde isso depois", não há onde "o depois" morar.

Por isso a pergunta vive em disco, com estado, e a resposta vira conhecimento do projeto.

## Os 2 estados

| Estado | Significa | Sai daqui quando |
|---|---|---|
| **Aberta** | feita (ou a fazer) e ainda sem resposta. Marque *(adiada em AAAA-MM-DD)* se foi o usuário que pediu pra responder depois | o usuário responde → *Respondida* |
| **Respondida** | resposta registrada no arquivo do tópico | se a resposta **decide** o rumo do projeto, **gradua** para `memory/decisions/` (ADR) e o item aponta para lá |

Pergunta aberta que **bloqueia** o trabalho atual é referenciada em `memory/active-context.md` enquanto pendente — é lá que o próximo turno/sessão a reencontra. O texto da pergunta vive **só** no arquivo do tópico (fonte única); o `active-context` apenas aponta.

## Onde vivem — agrupadas por tópico (nem arquivão, nem mil arquivinhos)

Segmento de memória `memory/questions/`, **um arquivo por tópico** (não por pergunta) — o meio-termo que o esquema índice + arquivo pede aqui:

- **Não** um único `questions.md` gigante (apodrece, ninguém relê).
- **Não** um arquivo por pergunta (centenas de fragmentos, sem visão de conjunto).
- **Sim** poucos arquivos por **assunto**, cada um acumulando as perguntas daquele assunto, **cruzando** com os outros por link relativo.

Os tópicos **emergem** do projeto — não force um catálogo. Sementes genéricas comuns: `produto.md` (escopo, prioridade), `arquitetura.md`, `stack.md`, `interface.md` (UX), `seguranca.md`, `operacao.md`. Comece com um; crie outro quando uma pergunta claramente não pertence a nenhum existente.

> **Regra de tamanho (memória como código):** um tópico que passa de uma leitura confortável, ou que virou dois assuntos, **divide-se** — mesmo critério da `architecture`/`memory/README`. É o que evita o arquivão sem cair na fragmentação.

### Molde de um arquivo de tópico (`memory/questions/<topico>.md`)

```
# Perguntas — <tópico>

> Relaciona-se com: [arquitetura](arquitetura.md) · [stack](stack.md)

## Em aberto
- [ ] <pergunta>  ·  destrava: <o que depende dela>  ·  (adiada pelo usuário AAAA-MM-DD)

## Respondidas
- [x] <pergunta>
      **Resposta:** <o que ficou decidido>  ·  AAAA-MM-DD
      <se virou decisão: ver decisions/<slug>.md>
```

Cruzamento entre tópicos é por **link relativo** (`[stack](stack.md)`) — é o "se comunicam entre si": uma pergunta de arquitetura que depende da stack aponta para lá em vez de duplicar.

## Regras de operação

- **Registre antes de perguntar:** ao fazer uma pergunta sobre o projeto, anote-a como *Aberta* no tópico certo **antes** de esperar a resposta. Assim, se o usuário some ou adia, ela persiste.
- **"Responde depois":** marque *(adiada em AAAA-MM-DD)* e **não represe o trabalho que não depende dela** — siga no que dá, deixe a pendência visível no `active-context`. Não reperguntar enquanto adiada.
- **Não invente resposta:** pergunta aberta que bloqueia → não assuma para "andar"; ou pergunta, ou registra a suposição **explícita** como pergunta aberta a confirmar.
- **Resposta vira conhecimento:** ao responder, mova para *Respondidas* com a resposta; se ela decide o rumo, gradua para `memory/decisions/`. Consolidar/arquivar segue o `memory/README`.
- **P0 (leigo):** pergunte uma coisa por vez, em linguagem de produto, sem jargão (ver `persona-p0`); registre a versão técnica no arquivo, mostre a humana no chat.
