#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alianca / kernel / verify.py

Stop hook: o bloco VERIFICATION — "como sabemos que foi realmente feito?".
Impede declarar "pronto" sem CONSTATAR o fato.

E o terceiro e ultimo bloco do microkernel:
  route.py  (UserPromptSubmit) — decide o que carregar.
  gate.py   (PreToolUse)        — fecha o caminho barato-errado.
  verify.py (Stop)              — nao deixa "pronto" sem prova.

Principios inegociaveis:
  1. CONSTATA, NAO PERGUNTA. A verificacao observa o FATO: roda um comando
     e le o exit code real. Nunca confia na alegacao da LLM.
  2. NUNCA TRANCAR O USUARIO. Fail-open em qualquer erro (exit 0). E como um
     Stop hook pode entrar em LOOP (bloqueia -> agente continua -> Stop dispara
     de novo), respeitamos stop_hook_active para NUNCA repetir o bloqueio.
  3. VALVULA DE ESCAPE LOGADA (o "sudo"): override explicito PERMITE mas
     REGISTRA quem/por que. Enforcement sem override vira a nova friccao.
  4. MENOS E MAIS: Python 3 stdlib apenas. utf-8 explicito. Caminhos via
     __file__ (nunca cwd). Deterministico.

Contrato Stop (Claude Code):
  - stdin: JSON com transcript_path, stop_hook_active, cwd, ...
  - BLOQUEAR: stdout JSON {"decision":"block","reason":"..."} + exit 0.
  - PERMITIR: exit 0 sem output.
"""

import io
import os
import re
import sys
import json
import shutil
import subprocess

# --- klog: importa; se falhar, no-op local (um log nunca quebra o hook) ----
try:
    from klog import klog  # mesmo diretorio (alianca/kernel/)
except Exception:  # pragma: no cover
    def klog(event, detail):
        pass


HERE = os.path.dirname(os.path.abspath(__file__))
CMD_FILE = os.path.join(HERE, "verify.cmd")
CMD_TIMEOUT = 120  # segundos
TAIL_LINES = 15

# Sinais CONSERVADORES de alegacao de CONCLUSAO (baixo falso-positivo).
# Exige formas COMPLETAS (participio/adjetivo): "concluido/finalizado/
# implementado". O INFINITIVO e INTENCAO, nao conclusao — "concluir",
# "vou finalizar", "preciso implementar" NAO casam de proposito.
CLAIM_RE = re.compile(
    r"\b(pront[oa]s?|conclu[ií]d[oa]s?|finalizad[oa]s?|implementad[oa]s?|"
    r"tarefa validada|marcar validada|est[aá] funcionando|done)\b",
    re.IGNORECASE,
)
# "pronto/pronta PARA <algo>" e intencao ("pronto para comecar"), nao conclusao.
PRONTO_PARA_RE = re.compile(r"\bpront[oa]s?\s+(?:para|pra)\b", re.IGNORECASE)


def has_completion_claim(msg):
    """True se a mensagem afirma CONCLUSAO (nao intencao/futuro)."""
    if not msg:
        return False
    cleaned = PRONTO_PARA_RE.sub(" ", msg)  # "pronto para ..." nao conta
    return bool(CLAIM_RE.search(cleaned))

# Valvula de escape logada: [verify:skip <razao>]
OVERRIDE_RE = re.compile(r"\[verify:skip\s+([^\]]*)\]", re.IGNORECASE)


# --- Leitura do transcript ------------------------------------------------

def _text_from_message(message):
    """Extrai o texto (concatenado) de uma mensagem do transcript."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") in (None, "text") and isinstance(block.get("text"), str):
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return ""


def last_assistant_text(transcript_path):
    """
    Retorna o texto da ULTIMA mensagem do assistant no transcript .jsonl.
    "" se nao houver / ilegivel (o chamador trata como 'sem claim').
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return ""
    last = ""
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except Exception:
                continue
            if not isinstance(evt, dict):
                continue
            if evt.get("type") != "assistant":
                continue
            txt = _text_from_message(evt.get("message"))
            if txt:
                last = txt
    return last


# --- Constatacao (roda o comando de verificacao) --------------------------

def read_verify_cmd():
    """Primeira linha nao-vazia de verify.cmd, ou None se ausente/vazio."""
    if not os.path.isfile(CMD_FILE):
        return None
    try:
        with open(CMD_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    return s
    except Exception:
        return None
    return None


def _tail(text, n=TAIL_LINES):
    lines = (text or "").splitlines()
    return "\n".join(lines[-n:])


_SHELL_BUILTINS = {"exit", "cd", "set", "echo", "type", "dir", "rem", "call", "for", "if"}


def cmd_runnable(cmd):
    """
    True se da pra EXECUTAR o comando (binario existe / builtin / compound).
    Distingue 'verificador nao roda' (infra) de 'verificacao falhou' (trabalho
    errado). Com shell=True um binario inexistente devolve exit != 0 (nao
    excecao) — sem este pre-voo isso seria lido como FALHA e bloquearia o
    usuario indevidamente. which() None -> fail-open (lado seguro: permitir).
    """
    cmd = (cmd or "").strip()
    if not cmd:
        return False
    if any(op in cmd for op in ("&&", "||", "|", ">", "<", ";", "&")):
        return True  # compound: deixa o shell resolver
    first = re.split(r"\s+", cmd, 1)[0].strip('"').strip("'")
    if first.lower() in _SHELL_BUILTINS:
        return True
    return shutil.which(first) is not None


def run_verification(cmd, cwd):
    """
    CONSTATA: roda o comando e observa o exit code REAL.
    Retorna (exit_code, saida_combinada). Levanta em timeout/erro de spawn
    (o chamador trata como fail-open — nao trancar o usuario).
    """
    workdir = cwd if (cwd and os.path.isdir(cwd)) else HERE
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=CMD_TIMEOUT,
    )
    out = proc.stdout.decode("utf-8", errors="replace") if proc.stdout else ""
    return proc.returncode, out


# --- Saida do hook --------------------------------------------------------

def _block(reason):
    """Emite o veredito de bloqueio (JSON decision) e retorna exit 0."""
    payload = {"decision": "block", "reason": reason}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    return 0


# --- Main -----------------------------------------------------------------

def main():
    # 0) stdin -> JSON. Qualquer falha = fail-open.
    try:
        raw = sys.stdin.buffer.read()
        data = raw.decode("utf-8", errors="replace")
        payload = json.loads(data) if data.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
    except Exception as e:
        klog("VERIFY", "fail-open: stdin invalido ({})".format(type(e).__name__))
        return 0

    # 1) Anti-loop: se o Stop anterior ja bloqueou, PERMITIR sempre.
    if payload.get("stop_hook_active"):
        klog("VERIFY", "skip: stop_hook_active")
        return 0

    # 2) Ultima mensagem do assistant. Falha de leitura = fail-open.
    try:
        msg = last_assistant_text(payload.get("transcript_path"))
    except Exception as e:
        klog("VERIFY", "fail-open: transcript ilegivel ({})".format(type(e).__name__))
        return 0

    # Sem alegacao de conclusao -> nada a constatar. PERMITIR.
    if not has_completion_claim(msg):
        klog("VERIFY", "no-claim: allow")
        return 0

    # 3) Valvula de escape logada (o "sudo"): [verify:skip <razao>].
    m = OVERRIDE_RE.search(msg or "")
    if m:
        razao = (m.group(1) or "").strip() or "(sem razao)"
        klog("VERIFY", "OVERRIDE razao={}".format(razao))
        return 0

    # 4) CONSTATA: procurar comando de verificacao configurado.
    try:
        cmd = read_verify_cmd()
    except Exception as e:
        klog("VERIFY", "fail-open: verify.cmd ilegivel ({})".format(type(e).__name__))
        return 0

    # 5b) Sem comando -> NAO ha como constatar. O portao so BLOQUEIA quando
    #     CONSTATA uma falha (constata, nao pergunta). Sem verify.cmd o
    #     enforcement e opt-in por projeto: PERMITIR. (Ligue configurando
    #     alianca/kernel/verify.cmd com o comando de teste/lint do projeto.)
    if not cmd:
        klog("VERIFY", "sem verify.cmd: allow (enforcement opt-in)")
        return 0

    # 5c) Verificador nao executavel (infra quebrada) != trabalho errado.
    #     Nao da pra constatar -> PERMITIR (nunca trancar por infra).
    if not cmd_runnable(cmd):
        klog("VERIFY", "fail-open: verificador nao executavel cmd='{}'".format(cmd))
        return 0

    # 4/5a) Rodar o comando e observar o exit code REAL.
    try:
        code, out = run_verification(cmd, payload.get("cwd"))
    except subprocess.TimeoutExpired:
        # Nao conseguimos constatar em tempo habil -> nunca trancar.
        klog("VERIFY", "fail-open: timeout cmd='{}'".format(cmd))
        return 0
    except Exception as e:
        klog("VERIFY", "fail-open: erro ao rodar cmd='{}' ({})".format(cmd, type(e).__name__))
        return 0

    if code == 0:
        klog("VERIFY", "cmd='{}' PASS".format(cmd))
        return 0

    # 5a) Constatou FALHA. BLOQUEAR com a saida real (tail).
    klog("VERIFY", "cmd='{}' FAIL exit={}".format(cmd, code))
    reason = (
        "Verificacao falhou (constatado): {} exit={}. "
        "Corrija e rode de novo. Saida:\n{}\n"
        "(Override consciente: inclua [verify:skip motivo].)"
    ).format(cmd, code, _tail(out))
    return _block(reason)


if __name__ == "__main__":
    # stdout/stderr utf-8 mesmo em consoles legados (Windows).
    for _name in ("stdout", "stderr"):
        try:
            stream = getattr(sys, _name)
            setattr(sys, _name, io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace"))
        except Exception:
            pass
    try:
        sys.exit(main())
    except Exception as e:
        # Blindagem final: NUNCA trancar o usuario.
        klog("VERIFY", "fail-open: excecao nao tratada ({})".format(type(e).__name__))
        sys.exit(0)
