#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
klog.py — o log do kernel da Alianca (o "dmesg").

Uma unica coisa, bem feita: anexar UMA linha ao kernel.log toda vez que
algo relevante acontece no kernel (route/gate/verify). E o registro que o
health-check e o X9 leem para responder "o que o kernel andou fazendo?".

Formato de cada linha (utf-8, append):
    <ISO8601 local>\t<EVENT>\t<detail>\n
Ex.:
    2026-07-01T14:03:22\tVERIFY\tclaim=pronto cmd='pytest -q' FAIL exit=1

Principio inegociavel: um LOG NUNCA pode quebrar um hook. Por isso TUDO
aqui e best-effort — envolto em try/except que engole qualquer excecao.
Se nao da para logar, o kernel segue a vida (fail-open silencioso).

Caminho do log resolvido via __file__ (nunca cwd): funciona identico
importado de qualquer diretorio de trabalho.

Interface publica:
    from klog import klog
    klog(event, detail)  -> anexa uma linha (best-effort, nunca levanta)
    tail(n)              -> lista das ultimas n linhas (best-effort, [] em erro)

Menos e mais: Python 3 stdlib apenas. ZERO dependencia.
"""

import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Caminho do log: SEMPRE ao lado deste arquivo (alianca/kernel/kernel.log).
# Resolvido via __file__ para funcionar de qualquer cwd.
# ---------------------------------------------------------------------------
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernel.log")


def klog(event, detail):
    """Anexa UMA linha ao kernel.log. Best-effort: NUNCA levanta excecao.

    "<ISO8601 local>\t<EVENT>\t<detail>\n"  (utf-8, append; cria se ausente).
    """
    try:
        ts = datetime.now().isoformat(timespec="seconds")
        # EVENT em caixa alta, sem tabs/quebras que estraguem o formato TSV.
        ev = str(event).upper().replace("\t", " ").replace("\n", " ").replace("\r", " ")
        dt = str(detail).replace("\t", " ").replace("\n", " ").replace("\r", " ")
        line = ts + "\t" + ev + "\t" + dt + "\n"
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        # Um log jamais derruba um hook. Silencio proposital.
        pass


def tail(n=20):
    """Ultimas n linhas do kernel.log (sem o \n final). Best-effort: [] em erro."""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            linhas = f.read().splitlines()
        if n is None or n <= 0:
            return linhas
        return linhas[-n:]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Auto-teste: `python klog.py` loga 3 eventos e imprime tail(2).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    klog("BOOT", "klog auto-teste inicio")
    klog("VERIFY", "claim=pronto cmd='pytest -q' FAIL exit=1")
    klog("OVERRIDE", "who=jonas why='hotfix urgente' — PERMITIDO e registrado")
    for l in tail(2):
        print(l)
