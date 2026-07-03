# -*- coding: utf-8 -*-
"""Lê results.json e imprime o relatório comparativo + notas 0-10."""
import json, os, statistics as st

BASE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(BASE, "results.json"), encoding="utf-8"))

TASKS = ["palindrome", "cpf", "fizzbuzz", "rpn", "roman"]
CONDS = ["baseline", "alianca"]
NAME = {"baseline": "SEM Aliança", "alianca": "COM Aliança"}

def sel(cond, task=None):
    return [r for r in R if r["cond"] == cond and (task is None or r["task"] == task)]

def avg(rows, key):
    xs = [r[key] for r in rows]
    return sum(xs) / len(xs) if xs else 0.0

print("=" * 68)
print("  BENCHMARK ALIANÇA — entregabilidade (modelo local via ollama)")
print("=" * 68)
n_per = len(sel("baseline", TASKS[0]))
print(f"  Modelo: qwen2.5-coder:7b | repetições por célula: {n_per} | tarefas: {len(TASKS)}")
print(f"  Nota/geração = extraível(2) + executa(2) + correto(4) + robusto(2)")
print()

# --- tabela por tarefa ---
hdr = f"  {'tarefa':<12} | {'SEM':>6} | {'COM':>6} | {'Δ':>6} | detalhe (SEM→COM)"
print(hdr); print("  " + "-" * 64)
for t in TASKS:
    b, a = sel("baseline", t), sel("alianca", t)
    nb, na = avg(b, "total"), avg(a, "total")
    det = (f"exec {avg(b,'executa'):.1f}/{avg(a,'executa'):.1f} "
           f"corr {avg(b,'correto'):.1f}/{avg(a,'correto'):.1f} "
           f"rob {avg(b,'robusto'):.1f}/{avg(a,'robusto'):.1f}")
    print(f"  {t:<12} | {nb:6.2f} | {na:6.2f} | {na-nb:+6.2f} | {det}")

print("  " + "-" * 64)
gb, ga = avg(sel("baseline"), "total"), avg(sel("alianca"), "total")
print(f"  {'NOTA GERAL':<12} | {gb:6.2f} | {ga:6.2f} | {ga-gb:+6.2f} |")
print()

# --- sub-métricas agregadas ---
def sub(cond):
    rows = sel(cond)
    return {
        "extraível": avg(rows, "extraivel"),
        "executa":   avg(rows, "executa"),
        "correto":   avg(rows, "correto"),
        "robusto":   avg(rows, "robusto"),
        "%exec_ok":  100 * sum(1 for r in rows if r["executa"] == 2) / len(rows),
        "%correto100": 100 * sum(1 for r in rows if r["correto"] >= 3.99) / len(rows),
        "seg_médio": avg(rows, "secs"),
    }
sb, sa = sub("baseline"), sub("alianca")
print("  Sub-métricas (média por geração):")
print(f"    {'métrica':<14} {'SEM':>8} {'COM':>8}")
for k in sb:
    print(f"    {k:<14} {sb[k]:8.2f} {sa[k]:8.2f}")
print()

# --- notas finais 0-10 ---
print("=" * 68)
print(f"  NOTA FINAL  →  SEM Aliança: {gb:.1f}/10     COM Aliança: {ga:.1f}/10")
print("=" * 68)

# erros mais comuns
print("\n  Falhas registradas (amostra):")
for cond in CONDS:
    errs = [r["err"] for r in sel(cond) if r["err"] and r["executa"] < 2]
    print(f"   {NAME[cond]}: {len(errs)} gerações com falha de execução/símbolo")
