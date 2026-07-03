# Relatório Final — A Aliança protege a entrega no longo prazo?

> Bateria de testes comparativos (COM vs SEM Aliança) usando uma IA rodando localmente na máquina
> (modelo `qwen2.5-coder:7b` via ollama). Mesma IA nos dois lados — a única diferença é operar ou
> não sob o método da Aliança. Objetivo: medir **entregabilidade**, com foco no **longo prazo**.

---

## Resumo em uma página (para qualquer pessoa entender)

Fizemos três testes, em ordem de importância crescente:

1. **Tarefa curta (tiro único)** — a IA resolve um probleminha isolado.
   → **Empate.** SEM 9.5/10, COM 9.1/10. Quando a tarefa é pequena e cabe tudo na cabeça da IA,
   a Aliança não faz diferença (e num azar de autoteste até ficou 0.4 atrás). **Esse não é o jogo.**

2. **Longo prazo, arquivo único (pressão de contexto)** — a IA trabalha muitos turnos até a
   conversa não caber mais na "memória de trabalho" (janela de contexto).
   → Quando o trabalho fica **maior que a janela**, a IA crua **começa a perder pedaços** do que
   foi pedido; a Aliança, que guarda tudo em disco e recarrega, **não perde**.

3. **Longo prazo, projeto real de 3 arquivos que se importam** — o teste mais fiel à realidade.
   → **Resultado decisivo** (tabela abaixo): sob pressão, a IA crua **alucina o contrato** entre os
   arquivos e o programa **não monta**; a Aliança monta e roda certo. Sem pressão, os dois empatam.

**Conclusão honesta:** o valor da Aliança **não** aparece em tarefinha curta — aparece exatamente
onde você projetou para aparecer: **no longo prazo, quando o trabalho excede a janela de contexto**.
Aí a diferença é entre "entrega funcionando" e "entrega quebrada por esquecimento/alucinação".

---

## Antes de tudo: conserto do ollama (transparência)

A primeira rodada foi **descartada**. O ollama estava com o recurso *flash attention* corrompendo o
texto gerado (duplicava e cortava o código) nos **dois** modelos instalados — quebrava quase todo
código e daria nota falsa. Corrigimos de forma permanente (`OLLAMA_FLASH_ATTENTION=0`) e **só então**
rodamos os testes válidos. (Não foi preciso reinstalar; era configuração, não instalação corrompida.)

---

## Teste 1 — Tarefa curta (linha de base)

5 tarefas isoladas (palíndromo, validação de CPF, FizzBuzz, calculadora RPN, número romano), 3
repetições cada, código **executado de verdade** contra casos reais.

| | SEM Aliança | COM Aliança |
|---|:--:|:--:|
| Nota geral | **9.5/10** | **9.1/10** |

4 das 5 tarefas: 10/10 nos dois lados. A diferença veio de uma só (CPF), onde a diretriz "inclua
testes" fez a IA anexar um autoteste com valor errado que, **sem um ciclo para rodá-lo e corrigir**,
derrubou a entrega. Em tiro único a Aliança mostra só metade do método (pede verificação, mas não há
como executá-la). **Detalhe em `RELATORIO-teste-alianca.md`.**

---

## Teste 2 — Longo prazo, arquivo único (pressão de contexto)

Uma spec de 10 funções, entregue ao longo de vários turnos que enchem a janela. Mede quantas
sobrevivem no fim, em vários tamanhos de janela.

| Janela | Retenção SEM | Retenção COM | Correção SEM | Correção COM |
|---|:--:|:--:|:--:|:--:|
| **800** (janela < arquivo) | **4/10** | **10/10** | 2/10 | 10/10 |
| 1500 | 10/10 | 10/10 | 0/10 | 10/10 |
| 3000 | 10/10 | 10/10 | 6/10 | 10/10 |
| 20000 (controle) | 10/10 | 10/10 | 0/10 | 10/10 |

A IA crua só **perde requisitos** quando a janela fica menor que o arquivo (em 800, guardou 4 de 10).
Como aqui o arquivo é minúsculo, isso só apareceu no menor tamanho — mas **num projeto real o código é
sempre muito maior que a janela**, então essa é a situação normal. **Detalhe em
`RELATORIO-fase1-longo-prazo.md`.**

---

## Teste 3 — Longo prazo, projeto real de 3 arquivos (o decisivo)

Três arquivos que se importam (`catalogo.py` → `desconto.py` → `pedido.py`) com **contratos
arbitrários** (nomes e regras específicos do projeto, que a IA não consegue adivinhar). Escrever o 3º
exige lembrar as assinaturas do 1º e 2º. Mede se o projeto montado **roda e devolve o valor certo**
(`finalizar(['AX9','KT3','MZ7'],'ZK88') == 85.8`). 2 repetições por célula.

| Janela | SEM Aliança | COM Aliança |
|---|:--:|:--:|
| **1200 (pressão)** | **4/10 · 4/10** — integração quebrada | **10/10 · 10/10** — roda, `total=85.8` |
| **20000 (controle)** | **10/10 · 10/10** — roda | 10/10 — roda |

**O que aconteceu, em português:**
- **Sob pressão**, quando chegou a hora de escrever o 3º arquivo, o contrato dos primeiros já tinha
  saído da janela. A IA crua **inventou** o nome da função (`pedido.finalizar` não existia) → o
  programa nem monta. Aconteceu nas **duas** vezes.
- **Com a Aliança**, o contrato foi **recarregado do disco** antes de escrever cada arquivo → chamou
  certo → o projeto montou e rodou.
- **No controle** (janela grande, contrato sempre visível), a IA crua **acertou 10/10** também.
  Isso é a prova anti-viés: a diferença vem **só da pressão de contexto**, não do teste ser injusto.

Este é o retrato exato do problema que a Aliança ataca: **a alucinação de longo prazo, quando o
trabalho excede a janela de contexto.**

---

## Veredito geral

- Em **tarefa curta**, a Aliança é neutra — e tudo bem, não é para isso que ela existe.
- Em **longo prazo com pressão de contexto** (o cenário real de projetos de verdade), a Aliança faz a
  diferença entre **entrega que funciona** e **entrega quebrada por esquecimento/alucinação**.
- O mecanismo comprovado: **estado em disco + recarregar o essencial a cada passo** mantém a IA fiel
  ao que foi combinado, mesmo quando a janela não cabe mais tudo. Custa mais tokens — e entrega o que
  foi pedido.

## Limitações honestas

- Modelo local pequeno (7B) e poucas repetições (N=1 a 3): há ruído nos números absolutos; o que é
  sólido é o **padrão** (pressão → crua quebra, Aliança segura; controle → empatam).
- Parte da vantagem da Aliança mistura dois fatores: o mecanismo de disco **e** a disciplina de
  verificação embutida no método. Ambos fazem parte do produto.
- Inferência mais lenta por causa do conserto do ollama (flash attention desligado).
