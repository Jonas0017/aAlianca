# Relatório — Fase 1: Fidelidade de Longo Prazo sob Pressão de Contexto

> Teste do diferencial REAL da Aliança: manter a entrega fiel aos requisitos quando a
> conversa cresce e a **janela de contexto** não cabe mais tudo. Modelo local `qwen2.5-coder:7b`
> via ollama; mesma IA, mesma tarefa, mesma sequência de turnos — a única diferença é **como o
> contexto é gerido**.

## O que foi testado

Uma spec com **10 funções checáveis** (`validador.py`), entregue ao longo de vários turnos que
vão enchendo a janela com edições e ruído. Mede-se, no fim, quantos dos 10 requisitos originais
**sobreviveram**.

- **SEM Aliança:** histórico cru acumulando numa janela de tamanho fixo. Quando estoura, o mais
  antigo (a spec) cai fora.
- **COM Aliança:** a spec e o arquivo vivem **em disco** e são **recarregados** a cada turno — a
  janela nunca perde o essencial.

Rodou-se em 4 tamanhos de janela (800 → 20000 chars) para desenhar a curva. O ponto de 20000 é o
**controle**: tudo cabe, então os dois devem empatar (prova anti-viés).

## Resultado (dois eixos, para separar memória de qualidade)

| Janela (chars) | Retenção SEM | Retenção COM | Correção SEM | Correção COM |
|---|:--:|:--:|:--:|:--:|
| **800** (janela < arquivo) | **4/10** | **10/10** | 2/10 | 10/10 |
| 1500 | 10/10 | 10/10 | 0/10 | 10/10 |
| 3000 | 10/10 | 10/10 | 6/10 | 10/10 |
| 20000 (controle) | 10/10 | 10/10 | 0/10 | 10/10 |

- **Retenção** = quantas das 10 funções sobreviveram no texto do arquivo (mede memória pura).
- **Correção** = quantas rodam e passam nos testes (mede entregabilidade final).

## Leitura honesta

1. **Retenção pura:** o baseline só **perde** requisitos quando a janela fica **menor que o
   artefato** (em 800, guardou só 4 das 10 funções — as 6 primeiras saíram da janela e sumiram).
   Acima disso, ele preserva copiando o arquivo anterior. A Aliança manteve **10/10 em todas**.
   - **Por que isso importa mesmo assim:** aqui o arquivo é minúsculo (~1 KB), então só dá para
     apertar além da janela no menor tamanho. **Num projeto real o código é sempre MUITO maior que
     a janela** — logo "janela < artefato" é o **padrão**, não a exceção. A Fase 2 testa isso de
     verdade.

2. **Correção/entregabilidade:** o baseline degrada em **todas** as janelas (0–6/10). As edições
   acumuladas num contexto sem estrutura introduzem bugs (ex.: `return s is not None and try:` —
   Python inválido que derruba o arquivo inteiro). A Aliança ficou **10/10 sempre**.
   - **Ressalva:** essa vantagem mistura dois fatores — recarregar o arquivo limpo do disco **e** a
     disciplina de verificação no prompt da Aliança. Não dá para atribuir 100% ao mecanismo de disco.

## Veredito da Fase 1

A tese se sustenta, com nuance honesta: o efeito de **retenção** é nítido exatamente quando o
artefato ultrapassa a janela (o caso real), e a **entrega** da Aliança se manteve íntegra em todos
os cenários enquanto a versão crua desmoronou. É o máximo que um teste de arquivo único
consegue mostrar — o cenário natural da tese (código >> janela, dependências entre arquivos) é a
Fase 2.

## Nota metodológica (transparência)

- N=1 por ponto (rodar 1 vez) → há ruído; a ordem não é perfeitamente monotônica.
- O modelo local é pequeno e comete erros de sintaxe por conta própria; parte dos "0" do baseline
  vem disso, não só da pressão de contexto — por isso separamos Retenção de Correção.
- Inferência com flash attention desligado (correção obrigatória de um bug do ollama nesta máquina)
  é mais lenta; por isso o escopo foi mantido enxuto.
