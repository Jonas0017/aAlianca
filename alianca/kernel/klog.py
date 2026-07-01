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
# dmesg: `python klog.py [N]` imprime um RESUMO legivel do kernel.log.
#
# NAO escreve nada (o contrato de escrita — klog/tail — fica intacto).
# So LE: contagem por evento, destaques (GATE/VERIFY block/skip) e as
# ultimas N decisoes via tail(). Deterministico. Fail-open: log ausente
# ou vazio -> "sem registros ainda", exit 0, sem excecao. Linhas
# malformadas sao contadas sem quebrar.
# ---------------------------------------------------------------------------

# Eventos "de primeira classe" que sempre aparecem no cabecalho, em ordem
# fixa (deterministico). Qualquer outro evento cai em "outros".
_KNOWN_EVENTS = ("ROUTE", "GATE", "VERIFY")


def _parse_line(linha):
    """(EVENT, detail) de uma linha TSV. Tolera linhas malformadas.

    Formato esperado: "<ts>\t<EVENT>\t<detail>". Sem os 3 campos, o
    EVENT vira "?" (contabilizado em 'malformadas'), nunca levanta.
    """
    partes = linha.split("\t")
    if len(partes) >= 3:
        return partes[1].strip().upper(), partes[2]
    return "?", linha


def _summary(n=20):
    """Monta as linhas do resumo do kernel.log. Best-effort, sem escrita."""
    # Le linhas cruas (mesma fonte que tail, mas sem recorte).
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except Exception:
        linhas = []

    # Log inexistente ou so linhas em branco -> sem registros.
    if not any(ln.strip() for ln in linhas):
        return ["sem registros ainda"]

    counts = {}          # EVENT -> total
    malformadas = 0
    gate_block = 0
    verify_block = 0
    verify_skip = 0

    for linha in linhas:
        if not linha.strip():
            continue
        ev, detail = _parse_line(linha)
        counts[ev] = counts.get(ev, 0) + 1
        low = detail.lower()
        if ev == "?":
            malformadas += 1
        elif ev == "GATE" and "block" in low:
            gate_block += 1
        elif ev == "VERIFY":
            if "block" in low:
                verify_block += 1
            if "skip" in low:
                verify_skip += 1

    total = sum(counts.values())
    out = []
    out.append("=== kernel dmesg — resumo de %d registros ===" % total)

    # Contagem por evento: conhecidos em ordem fixa, depois os demais
    # em ordem alfabetica (deterministico), '?' rotulado como malformadas.
    out.append("por evento:")
    for ev in _KNOWN_EVENTS:
        out.append("  %-8s %d" % (ev, counts.get(ev, 0)))
    outros = sorted(k for k in counts if k not in _KNOWN_EVENTS and k != "?")
    for ev in outros:
        out.append("  %-8s %d" % (ev, counts[ev]))
    if "?" in counts:
        out.append("  %-8s %d" % ("malform.", counts["?"]))

    # Destaques — o que sinaliza atrito.
    out.append("destaques:")
    out.append("  GATE   block: %d" % gate_block)
    out.append("  VERIFY block: %d  skip: %d" % (verify_block, verify_skip))
    if malformadas:
        out.append("  linhas malformadas: %d" % malformadas)

    # Ultimas N decisoes via a funcao tail existente (contrato intacto).
    # Filtra linhas em branco SO na exibicao, para o rotulo bater com a
    # contagem por evento (que ja ignora vazios) — tail() segue intacto.
    ult = [ln for ln in tail(n) if ln.strip()]
    out.append("ultimas %d decisoes:" % len(ult))
    for ln in ult:
        out.append("  " + ln)

    return out


if __name__ == "__main__":
    import sys

    # N opcional via argv; default ~20. Entrada invalida -> default (nunca quebra).
    n = 20
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except (ValueError, TypeError):
            n = 20

    for linha in _summary(n):
        print(linha)
    sys.exit(0)
