# Validação prática — a Aliança funciona?

> Teste A/B real: o **mesmo pedido**, com e sem o harness, em **duas LLMs diferentes**.
> Resumo honesto — inclusive onde deu empate. (Honestidade é a marca da casa: o harness existe justamente para não declarar "funciona" sem rodar e observar.)

## A pergunta

O harness faz diferença **mensurável**, ou é só cerimônia? E ele é mesmo **model-agnostic**?

## Metodologia

- **Mesmo pedido** nos dois lados: uma API Node.js de cadastro + login, *"pra manter e ir melhorando com o tempo"*.
- **Duas pastas isoladas e separadas:** uma vazia (controle, sem harness) e uma com a `alianca/` instalada. Pastas irmãs, **fora** do repositório do harness — para o controle não "descobrir" o método sozinho (contaminação observada e corrigida durante o próprio teste).
- **Controle de justiça:** num segundo round a **stack foi fixada** (Node + Express + SQLite) nos dois lados, isolando a única variável que importa — a presença do harness.
- **Duas LLMs:** Claude e GitHub Copilot — para checar a promessa *model-agnostic*.

## Resultados

### Empates honestos (o harness não faz milagre)

- **Segurança base:** as duas LLMs, mesmo **sem** harness, já fazem hash de senha (bcrypt), erro de login genérico e query parametrizada. Um modelo bom não guarda senha em texto puro sozinho.
- **Erro `EADDRINUSE` ao rodar os dois juntos:** foi conflito de porta (ambos sobem na 3000), **não** defeito de código — empate técnico.

### Onde o harness ganhou (com a stack travada)

| Critério | Sem harness | Com harness |
|---|---|---|
| Testes automatizados | ❌ nenhum | ✅ presentes |
| Memória / snapshot (retomar depois) | ❌ nada | ✅ sim |
| Segurança registrada (decisões, LGPD) | ❌ implícita no código | ✅ documentada |
| Docs / dimensionamento (persona, nível) | ❌ nada | ✅ sim |
| Estrutura (app / servidor / banco separados) | plana | em camadas |

**Tradução:** o código de hoje empata; o harness ganha no que faz o projeto **sobreviver** — testes que pegam regressões, memória que preserva contexto, estrutura que aguenta crescer. É **sustentabilidade a longo prazo**, não código mais bonito hoje.

### Model-agnostic: confirmado

O Copilot, com o harness, reproduziu o método (memória, testes, docs, snapshot, dimensionamento). O **processo transferiu** para uma LLM diferente do Claude.

### Achado honesto: a fidelidade acompanha o modelo

O harness levanta o piso de **qualquer** modelo, mas um modelo mais forte preenche o esqueleto mais fundo. No teste, o Claude registrou nível, eixos E/L/R e um `security.md` com tabela LGPD; o Copilot seguiu a **forma**, porém mais raso. O harness **organiza o trabalho — não transforma um modelo fraco em forte.**

## Aprendizados que o teste gerou (dogfood → melhoria)

1. **Caminho da memória:** instalado como subpasta `alianca/`, um modelo pode gravar a memória do projeto *dentro* dela em vez da raiz. Correção: deixar explícito que `memory/`, `snapshots/`, `docs/` e o código vivem na **raiz do projeto** — a `alianca/` é referência read-only.
2. **Registrar o dimensionamento:** reforçar que persona / eixos / nível entrem no `active-context.md` mesmo em modelos que tendem a pular isso.

## Conclusão

A Aliança **funciona e é model-agnostic.** Não promete código perfeito nem salva de tudo — promete (e entrega) **processo**: testes, memória, estrutura e segurança registrada, **proporcionais ao projeto**, em qualquer LLM. Para algo feito "pra durar e melhorar", essa é a diferença entre um protótipo e um projeto sustentável.

## Segundo round — kernel NextGen + Ollama local (2026-07-01)

Depois de a Aliança ganhar o **microkernel de hooks** (roteamento + portões determinísticos), um teste mais controlado, com LLM **local**.

- **Setup justo:** mesmo modelo (`qwen2.5-coder:7b`), mesmo prompt, mesma amostragem (`temperature=0.2`, `seed=42`). Única variável: o contexto que o kernel injetaria (±Aliança).
- **Prompt escolhido pra discriminar:** função Python de cadastro que recebe e-mail + senha e salva no PostgreSQL.
- **Três braços:**

| Braço | Resultado |
|---|---|
| `sem-alianca` | código funcional, mas **senha em texto puro** + credencial no código; "use bcrypt" só como nota não implementada |
| `com-alianca` (preâmbulo restritivo *"não escreva antes de obedecer"*) | **recusou** entregar código — supercorrigiu |
| `com-alianca-neutro` (preâmbulo neutro, fiel ao que o kernel injeta) | entregou **código seguro**: bcrypt, query parametrizada, transação com rollback |

**Conclusões honestas:**
1. O harness **virou a chave do defeito nº1** (senha em texto puro → bcrypt) mesmo num modelo 7B.
2. A recusa do braço restritivo era o **enquadramento da injeção**, não o `security.md`. O kernel real (`route.py`) injeta de forma **neutra**, então se comporta como o braço neutro — o `security.md` **não precisou de ajuste**. (O teste que faríamos pra "consertar" provou que não havia o que consertar.)
3. Limite honesto: mesmo com Aliança, o 7B ainda **hardcodou a credencial do banco** e **pulou testes** — limite do **modelo pequeno**, não do harness. Um modelo maior fecha esses também.

**Aprendizado que virou arquitetura:** o que é crítico deve migrar do **texto-injetado (advisory)** para os **portões determinísticos (enforcement)** — é a origem do 3º portão (`Verification`) e do papel do `X9` como mecanismo de integridade.

> Teste realizado em 2026-07-01 · LLM: `qwen2.5-coder:7b` via Ollama local · 3 braços · tarefa: função de cadastro em Python/PostgreSQL.

## Reproduza você mesmo

1. Crie duas pastas separadas e vazias, **fora deste repositório**: `sem-harness/` e `com-harness/`.
2. Na `com-harness/`, coloque a pasta `alianca/` (copie, ou `git clone` deste repo).
3. Cole o **mesmo** prompt nas duas:
   > *"Preciso de uma API em Node.js pra cadastrar usuários e fazer login. Vai guardar nome, e-mail e senha das pessoas. É um projeto que eu quero manter e ir melhorando com o tempo. Use Express e banco SQLite (better-sqlite3)."*
   - Na `com-harness/`, prefixe: *"Leia alianca/START-HERE.md e siga-o. Depois atenda:"* (ou use um `CLAUDE.md` de uma linha apontando para o START-HERE).
4. Compare: tem testes? memória/snapshot pra retomar? segurança registrada? estrutura em camadas? dimensionou (persona/nível)?

> Teste realizado em 2026-06-08 · LLMs: Claude e GitHub Copilot · tarefa: API de cadastro/login em Node.
