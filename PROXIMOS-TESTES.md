# Próximos testes da Aliança — plano para rodar depois (modo noturno)

> Escrito em 2026-07-02. Objetivo: fechar o que os primeiros testes deixaram em aberto, sem
> estressar a máquina durante o dia. Rodar **enquanto o usuário dorme**.

## O que já está PROVADO (não repetir)

- Sob pressão de contexto (código > janela), a IA crua **alucina contrato / perde requisito** e a
  entrega quebra; a Aliança (estado em disco + recarga) **segura**. No controle sem pressão, empatam.
- Ver `RELATORIO-FINAL-alianca.md`, `RELATORIO-fase1-longo-prazo.md`, `RELATORIO-teste-alianca.md`.

## O que FALTA provar (estes testes)

### ✅ Teste B+C — Isolamento de fatores + Custo em tokens (ROI)  [AUTOMÁTICO / NOTURNO]
**Pergunta:** a vantagem da Aliança vem do *mecanismo* (recarregar do disco) ou da *disciplina* (o
prompt que manda verificar)? E quanto isso custa em tokens?
**Como:** o projeto de 3 arquivos roda em **4 condições** (desenho 2×2):

| Condição | Prompt | Recarga de disco | Isola |
|---|---|---|---|
| `baseline` | neutro | não | controle |
| `alianca` | Aliança | sim | produto completo |
| `alianca_noreload` | Aliança | não | só a disciplina do prompt |
| `base_reload` | neutro | sim | só o mecanismo de disco |

Se `base_reload` já sobe muito perto de `alianca`, o valor está no **mecanismo**. Se `alianca_noreload`
também ajuda, parte é **disciplina**. Cada sessão registra tokens (prompt+geração) → custo por
condição.
**Script:** `tests-bench/phase2_overnight.py` (já pronto). ~128 gerações, ~2-3h.

### ✅ Teste A' — Curva de retenção mais fina  [AUTOMÁTICO / NOTURNO]
**Pergunta:** confirmar a curva "quanto menor a janela, mais a IA crua perde" com mais repetições e
mais tamanhos, reduzindo o ruído do N=1.
**Script:** `tests-bench/longhorizon.py` (já pronto, parametrizado por env). ~80 gerações, ~1-2h.

### ⏳ Teste D — Harness REAL ponta a ponta  [PRECISA DE SUPERVISÃO — não é noturno]
**Pergunta:** o kernel de verdade (hooks `route/gate/verify` + router + subagentes) dirigindo um
agente capaz (Claude Code) numa tarefa longa entrega a fidelidade que o *princípio* mostrou?
**Por que não é noturno:** exige um agente em loop real, não um script ollama. Requer sessão
supervisionada com o Claude Code. **Fica para uma sessão dedicada.** Desenho sugerido: uma tarefa
multi-arquivo de verdade, comparando uma sessão COM o kernel ligado vs. uma sessão SEM, medindo
requisitos entregues, contradições e retrabalho.

---

## Como rodar a bateria noturna (um comando)

No chat do Claude Code, antes de dormir:

```
! bash "tests-bench/run_overnight.sh"
```

Ou num terminal (Git Bash):

```
bash "tests-bench/run_overnight.sh"
```

Isso: garante o ollama são (flash attention desligado), roda o Teste B+C e depois o Teste A', e
deixa os logs com carimbo de hora.

### Onde olhar o resultado de manhã
- `tests-bench/phase2_overnight.log`  → tabela final (nota · integração% · tokens por condição)
- `tests-bench/longhorizon_night.log` → curva de retenção
- `tests-bench/results_p2_night.json` e `results_lh.json` → dados brutos

### Ajustar o tamanho (se quiser mais/menos)
Editar as variáveis no topo de `run_overnight.sh`: `P2_N` (repetições), `P2_CTXS` (janelas),
`LH_N`, `LH_CTXS`, `LH_TURNS`. Mais repetições = números mais firmes, porém mais horas.

## Pré-requisitos (já atendidos nesta máquina)
- ollama com modelo `qwen2.5-coder:7b`.
- `OLLAMA_FLASH_ATTENTION=0` já gravado como variável de usuário permanente (o script reforça).
- Python 3.12 com `requests`.
