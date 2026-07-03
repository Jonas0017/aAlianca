#!/usr/bin/env bash
# Bateria noturna de testes da Aliança. Roda sozinha; deixa logs com carimbo de hora.
# Uso: bash run_overnight.sh   (ou no chat do Claude Code:  ! bash "tests-bench/run_overnight.sh")
set -u
cd "$(dirname "$0")"

# 1) Garante o ollama são (flash attention DESLIGADO — senão corrompe a saída nesta máquina)
export OLLAMA_FLASH_ATTENTION=0
if ! python -c "import requests; requests.get('http://127.0.0.1:11434/',timeout=5)" >/dev/null 2>&1; then
  echo "iniciando ollama serve..."
  ollama serve >/dev/null 2>&1 &
  sleep 6
fi

echo "==================================================================="
echo "=== INICIO bateria noturna: $(date) ==="
echo "==================================================================="

# 2) TESTE PRINCIPAL — projeto multi-arquivo: isola MECANISMO vs DISCIPLINA + mede TOKENS (ROI)
#    4 condições x 2 janelas x 4 reps x 4 turnos = 128 gerações (~2-3h nesta máquina)
echo ">>> [1/2] phase2_overnight (isolamento de fatores + custo de tokens) — $(date)"
P2_N=4 P2_CTXS=1200,20000 python phase2_overnight.py > phase2_overnight.log 2>&1
echo ">>> phase2_overnight FIM — $(date)"

# 3) TESTE SECUNDÁRIO — arquivo único, curva de janela mais fina e mais repetições
#    2 reps x 4 janelas x 5 turnos = 80 gerações (~1-2h)
echo ">>> [2/2] longhorizon (curva de retenção, mais fina) — $(date)"
LH_N=2 LH_CTXS=800,1500,3000,20000 LH_TURNS=4 LH_NUMPREDICT=750 python longhorizon.py > longhorizon_night.log 2>&1
echo ">>> longhorizon FIM — $(date)"

echo "==================================================================="
echo "=== FIM bateria noturna: $(date) ==="
echo "Resultados: phase2_overnight.log / longhorizon_night.log"
echo "JSON: results_p2_night.json / results_lh.json"
echo "==================================================================="
