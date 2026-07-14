#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session_start.py — hook SessionStart da Alianca (arranque de conversa NOVA).

So dispara em conversa NOVA (matcher "startup" no settings + checagem de
'source' aqui por defesa em profundidade). Faz duas coisas:
  1) STARTA o kernel: roda o selftest e reporta a saude (verde/FALHA) no
     contexto da sessao. O kernel "acorda" provado.
  2) Dispara o X9: injeta a diretriz OBRIGATORIA de rodar a auditoria de pontas
     soltas como PRIMEIRO ato, delegada a um subagente (Regra do gerente).

Filosofia (igual aos outros hooks): NUNCA quebrar a sessao. Fail-open: qualquer
erro -> exit 0. stdout utf-8. Deterministico. stdlib apenas.

TRAVA ANTI-RECURSAO: rodar o selftest a partir daqui e seguro porque o proprio
selftest, ao exercitar este hook, seta ALIANCA_SS_NO_SELFTEST=1 — e com essa
env presente NAO re-rodamos o selftest. Sem isso: session_start -> selftest ->
test_session_start -> session_start -> selftest ... (fork-bomb).

Contrato (Claude Code, SessionStart):
  stdin  -> JSON com "source" (startup|resume|clear|compact), ...
  stdout -> JSON {"hookSpecificOutput": {"hookEventName":"SessionStart",
                   "additionalContext": "..."}}
  exit   -> sempre 0.
"""

import io
import os
import re
import sys
import json
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from klog import klog
except Exception:
    def klog(event, detail):
        pass

# scope: escopo ATIVO (raiz vs microprojeto) — o X9/monitor roda no escopo certo
# e le/grava o x9-state.md DELE. Modulo puro; fail-open p/ raiz.
try:
    from scope import resolve_scope, memory_dir_rel
except Exception:
    def resolve_scope(cwd, prompt, registry=None):
        return None

    def memory_dir_rel(scope):
        return "memory"

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SELFTEST = os.path.join(HERE, "selftest.py")
SELFTEST_TIMEOUT = 90

def _x9_directive(scope):
    """Diretriz X9 do arranque, apontando para o x9-state.md do ESCOPO ATIVO."""
    try:
        state = "alianca/" + memory_dir_rel(scope) + "/x9-state.md"
    except Exception:
        state = "alianca/memory/x9-state.md"
    escopo = scope if scope else "raiz"
    return (
        "OBRIGATORIO, primeiro ato desta conversa: rode a auditoria X9 (pontas "
        "soltas do projeto) DELEGANDO a um subagente (ver alianca/instructions/"
        "x9.md); traga so o resumo das pontas soltas ANTES de qualquer outro "
        "trabalho. Escopo ativo: {0} (estado do monitor em {1}).".format(
            escopo, state)
    )


def _emit(additional_context):
    payload = {"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": additional_context,
    }}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


def _read_source():
    try:
        raw = sys.stdin.read()
        if raw and raw.strip():
            data = json.loads(raw)
            if isinstance(data, dict):
                return data.get("source")
    except Exception:
        pass
    return None


def _kernel_line():
    """Roda o selftest e resume a saude. Guard anti-recursao via env."""
    if os.environ.get("ALIANCA_SS_NO_SELFTEST"):
        return "Kernel: (selftest nao re-executado em auto-teste)."
    try:
        proc = subprocess.run(
            [sys.executable or "python", SELFTEST],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=os.path.dirname(HERE),
            timeout=SELFTEST_TIMEOUT,
        )
        out = proc.stdout.decode("utf-8", "replace") if proc.stdout else ""
        m = re.search(r"RESUMO:\s*(.+)", out)
        resumo = m.group(1).strip() if m else "sem resumo"
        if proc.returncode == 0:
            return "Kernel: {} (selftest verde no arranque).".format(resumo)
        return ("Kernel: FALHA no selftest do arranque ({}). Conserte o kernel "
                "antes de prosseguir.").format(resumo)
    except Exception as e:
        return "Kernel: selftest nao rodou no arranque ({}).".format(
            type(e).__name__)


def main():
    source = _read_source()
    # So conversa NOVA. resume/clear/compact -> nao repete o arranque (nem o x9).
    if source not in (None, "startup"):
        klog("SESSION", "skip source={}".format(source))
        return 0
    kernel_line = _kernel_line()
    try:
        scope = resolve_scope(None, None)
    except Exception:
        scope = None
    klog("SESSION", "startup: scope={} {}".format(
        scope or "raiz", kernel_line[:60]))
    ctx = ("== Alianca — arranque de conversa ==\n"
           + kernel_line + "\n" + _x9_directive(scope))
    _emit(ctx)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        klog("SESSION", "fail-open: {}".format(type(e).__name__))
        sys.exit(0)
