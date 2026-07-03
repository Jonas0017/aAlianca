# Relatório do Teste: Aliança vs. sem Aliança

> Teste comparativo e isolado do harness **Aliança**, usando um modelo de IA rodando localmente na máquina (via **ollama**), para medir **entregabilidade**: se a IA realmente entrega o que foi pedido, funcionando.

## 1. Em uma frase

Rodamos a **mesma IA** resolvendo as **mesmas 5 tarefas**, uma vez **sem** a Aliança e uma vez **com** a Aliança, e medimos quanto do que foi pedido saiu funcionando de verdade. Resultado: **SEM Aliança 9.5/10** · **COM Aliança 9.1/10** (diferença de -0.4) → **SEM Aliança**.

## 2. Como o teste foi feito (para qualquer pessoa entender)

Imagine dois candidatos idênticos numa prova de programação. São a **mesma pessoa** (o mesmo modelo de IA, `qwen2.5-coder:7b`), com a **mesma prova** e as **mesmas regras de correção**. A única diferença:

- **Candidato SEM Aliança:** recebe só a tarefa. É o comportamento cru da IA.
- **Candidato COM Aliança:** recebe a tarefa **mais as instruções da Aliança** (o método: entregar algo completo, pensar nos casos de borda, conferir antes de entregar, não inventar).

Para ser **justo**, tudo o mais é igual: mesmo modelo, mesma temperatura, mesma 'semente' de aleatoriedade, mesmo formato de resposta pedido. Cada tarefa foi repetida **3 vezes** em cada lado (para não depender de sorte), num total de **30 respostas geradas**.

**O ponto central — entregabilidade:** não julgamos se o texto *parece* bom. Cada resposta é **executada de verdade** no computador e testada contra casos reais. Ou o código roda e acerta, ou não. Sem achismo.

### Como cada resposta virou uma nota de 0 a 10

| Critério | Vale | O que mede |
|---|---|---|
| Extraível | 2 | A IA entregou um bloco de código de fato? |
| Executa | 2 | O código roda sem quebrar e cria a função pedida? |
| **Correto** | **4** | Passa nos casos principais da tarefa? (o que mais pesa) |
| Robusto | 2 | Aguenta os casos de borda (vazio, inválido, limite)? |

## 3. As 5 tarefas, uma a uma

### Detector de palíndromo

**O que é:** Uma função que diz se uma frase é um palíndromo — se lê igual de trás para frente — ignorando maiúsculas, espaços e pontuação. Ex.: "A man, a plan, a canal: Panama" → sim.

**Como testamos:** Pedimos a função `is_palindrome(texto)`. Testamos 5 frases certas/erradas e 3 casos de borda (texto vazio, só pontuação, uma letra).

**Notas:** SEM Aliança **10.0/10** · COM Aliança **10.0/10** (+0.0)

- Rodou sem quebrar: SEM 100% · COM 100% das vezes
- Acertou o principal: SEM 100% · COM 100%
- Aguentou as bordas: SEM 100% · COM 100%

### Validador de CPF

**O que é:** Uma função que confere se um CPF brasileiro é válido, pela conta dos dois dígitos verificadores. Aceita com ou sem pontos/traço.

**Como testamos:** Pedimos `valida_cpf(cpf)`. Testamos 5 casos principais (CPFs válidos e inválidos reais) e 5 bordas (todos dígitos iguais, vazio, curto demais).

**Notas:** SEM Aliança **7.6/10** · COM Aliança **5.7/10** (-1.9)

- Rodou sem quebrar: SEM 100% · COM 67% das vezes
- Acertou o principal: SEM 40% · COM 27%
- Aguentou as bordas: SEM 100% · COM 67%

> **Por que o CPF puxou as duas notas para baixo?** O modelo pequeno erra a conta dos dígitos verificadores: a função que ele escreve acaba rejeitando CPFs válidos. É um erro **do modelo**, e acontece igual nos dois lados.
>
> **E por que a Aliança ficou atrás aqui?** A Aliança pede para 'sempre incluir testes e verificar'. O modelo então anexou autotestes (`assert`) ao código — mas escreveu um deles com o valor errado. Como este teste era uma **resposta única** (a IA não pôde rodar, ver o erro e corrigir), esse autoteste furado **derrubou o programa inteiro** ao abrir, zerando aquela tentativa. Num agente real que roda em ciclo, esse mesmo autoteste seria executado, o erro apareceria e seria corrigido — virando vantagem, não defeito.

### FizzBuzz

**O que é:** O exercício clássico: contar de 1 a N trocando múltiplos de 3 por 'Fizz', de 5 por 'Buzz', e de 3 e 5 por 'FizzBuzz'.

**Como testamos:** Pedimos `fizzbuzz(n)` devolvendo uma lista. Conferimos 7 posições específicas e 3 bordas (n=1, n=0, n=3).

**Notas:** SEM Aliança **10.0/10** · COM Aliança **10.0/10** (+0.0)

- Rodou sem quebrar: SEM 100% · COM 100% das vezes
- Acertou o principal: SEM 100% · COM 100%
- Aguentou as bordas: SEM 100% · COM 100%

### Calculadora RPN (a mais difícil)

**O que é:** Avalia contas em 'notação polonesa reversa', onde o operador vem depois dos números. Ex.: ['2','1','+','3','*'] = (2+1)*3 = 9.

**Como testamos:** Pedimos `eval_rpn(tokens)`. Testamos 5 contas principais e 3 bordas (divisão com vírgula, resultado negativo, número negativo na entrada).

**Notas:** SEM Aliança **10.0/10** · COM Aliança **10.0/10** (+0.0)

- Rodou sem quebrar: SEM 100% · COM 100% das vezes
- Acertou o principal: SEM 100% · COM 100%
- Aguentou as bordas: SEM 100% · COM 100%

### Conversor para número romano

**O que é:** Converte um número (1 a 3999) para algarismo romano. Ex.: 1994 → MCMXCIV.

**Como testamos:** Pedimos `int_to_roman(n)`. Testamos 5 conversões conhecidas e 4 bordas (3999, 40, 90, 400).

**Notas:** SEM Aliança **10.0/10** · COM Aliança **10.0/10** (+0.0)

- Rodou sem quebrar: SEM 100% · COM 100% das vezes
- Acertou o principal: SEM 100% · COM 100%
- Aguentou as bordas: SEM 100% · COM 100%

## 4. Placar final

| Tarefa | SEM Aliança | COM Aliança | Diferença |
|---|:--:|:--:|:--:|
| Detector de palíndromo | 10.0 | 10.0 | +0.0 |
| Validador de CPF | 7.6 | 5.7 | -1.9 |
| FizzBuzz | 10.0 | 10.0 | +0.0 |
| Calculadora RPN (a mais difícil) | 10.0 | 10.0 | +0.0 |
| Conversor para número romano | 10.0 | 10.0 | +0.0 |
| **NOTA GERAL** | **9.5** | **9.1** | **-0.4** |

## 5. Observação de honestidade (importante)

Antes deste teste valer, a primeira rodada foi **descartada**: o ollama estava com um recurso (*flash attention*) que corrompia o texto gerado (duplicava e cortava o código) nos **dois** modelos instalados. Isso quebrava quase todo código e teria dado uma nota falsa. Corrigimos o ollama (desligamos esse recurso, de forma permanente) e **só então** rodamos o teste que gerou os números acima. As notas refletem a IA funcionando de verdade.

## 6. Leitura honesta do resultado

**Neste teste, a Aliança NÃO melhorou a nota — empatou na maioria e ficou levemente atrás no total (9.5 vs 9.1).** Não vamos maquiar isso. O que os números dizem, com honestidade:

- **Nas 4 tarefas diretas** (palíndromo, FizzBuzz, RPN, romano) deu **10/10 nos dois lados**. Quando a tarefa é clara e o modelo dá conta, a Aliança não atrapalha nem precisa fazer mágica — o resultado já sai completo.
- **A diferença veio inteira de UMA tarefa (CPF) e de UM detalhe:** a Aliança levou o modelo a escrever autotestes; um autoteste saiu com valor errado e, **sem um ciclo para rodá-lo e corrigir**, derrubou aquela entrega. Ou seja, a parte da Aliança que apareceu foi a que **pede** verificação; a parte que **executa** a verificação (o passo VERIFICAR) não existe numa resposta única de ollama.
- **Isto na verdade confirma a tese da Aliança:** o valor dela está no **ciclo** planejar → agir → **verificar rodando** → corrigir. Tirado o ciclo (como neste teste de tiro único), sobra só metade do método. Num agente de verdade (Claude Code, p.ex.), o autoteste do CPF teria sido executado, o erro apareceria, e a entrega seria consertada antes de fechar.

**Conclusão em uma linha:** com um modelo pequeno e em resposta única, a Aliança teve efeito praticamente neutro (ligeiramente negativo por um acaso de autoteste). O teste que faria a Aliança brilhar é um **agente em loop** — e é assim que ela é usada de verdade. Este experimento foi justo, isolado e reprodutível; a limitação está no formato de tiro único, não no método.
