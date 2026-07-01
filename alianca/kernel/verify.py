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


# --- PERSISTIR (5o passo do loop): trabalho substancial exige memoria -----
#
# O loop e CHECAR -> CARREGAR -> AGIR -> VERIFICAR -> PERSISTIR. Os passos
# 1-4 ja tem enforcement; este bloco fecha o 5o: se o turno fez trabalho
# substancial de ESCRITA no projeto (Edit/Write/NotebookEdit no transcript,
# ignorando escritas em alianca/memory/) e alianca/memory/active-context.md
# NAO foi tocado durante a sessao (mtime < timestamp do 1o evento do
# transcript), o Stop bloqueia 1x mandando persistir. Anti-loop garantido
# pelo stop_hook_active (checado antes, no main). Fail-open em tudo.

MEMORY_ACTIVE = os.path.join(os.path.dirname(HERE), "memory", "active-context.md")
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# "Substancial" = pelo menos N usos de ferramenta de escrita no projeto.
# 1 edit trivial nao obriga a persistir; 2+ ja e trabalho que merece memoria.
PERSIST_MIN_WRITES = 2
# Folga p/ granularidade de mtime do filesystem (FAT arredonda a 2s).
MTIME_SLACK_S = 2.0


def _iso_to_epoch(ts):
    """ISO8601 (com ou sem 'Z'/offset) -> epoch. None se nao parsear."""
    try:
        from datetime import datetime
        s = str(ts).strip()
        if not s:
            return None
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        # Naive -> assume hora local (mesmo relogio do mtime). Aware -> exato.
        return dt.timestamp()
    except Exception:
        return None


def _is_project_write(path, cwd):
    """
    True se o caminho escrito conta como 'arquivo do projeto':
      - escritas em alianca/memory/ NAO contam (persistir memoria e o remedio,
        nao o sintoma);
      - caminho absoluto FORA do cwd do projeto nao conta (temp/scratch).
    """
    if not path:
        return False
    low = str(path).replace("\\", "/").lower()
    if "alianca/memory/" in low:
        return False
    try:
        if cwd and os.path.isabs(path):
            c = os.path.normcase(os.path.abspath(cwd))
            p = os.path.normcase(os.path.abspath(path))
            if p != c and not p.startswith(c.rstrip("\\/") + os.sep):
                return False
    except Exception:
        pass  # em duvida, conta como do projeto (o gate ainda e fail-open)
    return True


def _scan_transcript_writes(transcript_path, cwd):
    """
    Varre o transcript .jsonl uma vez e devolve (writes, session_start):
      writes        -> quantos tool_use de escrita em arquivos do projeto;
      session_start -> epoch do PRIMEIRO evento com timestamp parseavel
                       (inicio da sessao), ou None.
    """
    writes = 0
    session_start = None
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
            if session_start is None:
                session_start = _iso_to_epoch(evt.get("timestamp"))
            message = evt.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_use":
                    continue
                if block.get("name") not in WRITE_TOOLS:
                    continue
                tin = block.get("input")
                tin = tin if isinstance(tin, dict) else {}
                path = tin.get("file_path") or tin.get("notebook_path") or ""
                if _is_project_write(path, cwd):
                    writes += 1
    return writes, session_start


def persist_reason(payload):
    """
    Portao PERSISTIR. Retorna a razao de bloqueio (str) ou None (permitir).
    So constata: nunca levanta para o chamador alem do try do main.
    """
    transcript_path = payload.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        return None  # sem transcript nao ha como constatar -> fail-open

    # (c) Sem memoria inicializada -> nada a exigir. ALLOW logado.
    if not os.path.isfile(MEMORY_ACTIVE):
        klog("VERIFY", "persist: allow sem active-context.md (memoria nao inicializada)")
        return None

    writes, session_start = _scan_transcript_writes(
        transcript_path, payload.get("cwd"))

    if writes < PERSIST_MIN_WRITES:
        klog("VERIFY", "persist: allow writes={} (< {}: sem trabalho substancial)".format(
            writes, PERSIST_MIN_WRITES))
        return None

    if session_start is None:
        klog("VERIFY", "persist: allow fail-open (transcript sem timestamp)")
        return None

    try:
        mtime = os.path.getmtime(MEMORY_ACTIVE)
    except Exception:
        klog("VERIFY", "persist: allow fail-open (mtime ilegivel)")
        return None

    if mtime >= session_start - MTIME_SLACK_S:
        klog("VERIFY", "persist: allow active-context.md atualizado na sessao (writes={})".format(writes))
        return None

    klog("VERIFY", "persist: block writes={} sem atualizar active-context.md".format(writes))
    return (
        "PERSISTIR pendente: este turno editou {} arquivo(s) do projeto mas "
        "alianca/memory/active-context.md nao foi atualizado nesta sessao. "
        "Atualize o active-context.md (o que mudou / proximo passo) antes de "
        "encerrar."
    ).format(writes)


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
    first = re.split(r"\s+", cmd, maxsplit=1)[0].strip('"').strip("'")
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

    # 3) Valvula de escape logada (o "sudo"): [verify:skip <razao>].
    #    Vale para os DOIS portoes deste hook (claim e PERSISTIR).
    m = OVERRIDE_RE.search(msg or "")
    if m:
        razao = (m.group(1) or "").strip() or "(sem razao)"
        klog("VERIFY", "OVERRIDE razao={}".format(razao))
        return 0

    # 4/5) Portao 1 — CLAIM: alegou "pronto"? Entao constata com verify.cmd.
    #      Todo caminho de PERMITIR cai para o portao PERSISTIR abaixo
    #      (checagem ADICIONAL); so o BLOCK encerra aqui.
    reason = _claim_reason(msg, payload)
    if reason:
        return _block(reason)

    # 6) Portao 2 — PERSISTIR (5o passo do loop). Fail-open em qualquer erro.
    try:
        reason = persist_reason(payload)
    except Exception as e:
        klog("VERIFY", "persist: allow fail-open ({})".format(type(e).__name__))
        reason = None
    if reason:
        return _block(reason)
    return 0


def _claim_reason(msg, payload):
    """
    Portao do CLAIM (logica original, intacta): se a ultima mensagem alega
    conclusao, roda o verify.cmd e devolve a razao de bloqueio quando a
    verificacao FALHA. Devolve None em todo caminho de permitir (fail-open).
    """
    # Sem alegacao de conclusao -> nada a constatar. PERMITIR.
    if not has_completion_claim(msg):
        klog("VERIFY", "no-claim: allow")
        return None

    # CONSTATA: procurar comando de verificacao configurado.
    try:
        cmd = read_verify_cmd()
    except Exception as e:
        klog("VERIFY", "fail-open: verify.cmd ilegivel ({})".format(type(e).__name__))
        return None

    # Sem comando -> NAO ha como constatar. O portao so BLOQUEIA quando
    # CONSTATA uma falha (constata, nao pergunta). Sem verify.cmd o
    # enforcement e opt-in por projeto: PERMITIR. (Ligue configurando
    # alianca/kernel/verify.cmd com o comando de teste/lint do projeto.)
    if not cmd:
        klog("VERIFY", "sem verify.cmd: allow (enforcement opt-in)")
        return None

    # Verificador nao executavel (infra quebrada) != trabalho errado.
    # Nao da pra constatar -> PERMITIR (nunca trancar por infra).
    if not cmd_runnable(cmd):
        klog("VERIFY", "fail-open: verificador nao executavel cmd='{}'".format(cmd))
        return None

    # Rodar o comando e observar o exit code REAL.
    try:
        code, out = run_verification(cmd, payload.get("cwd"))
    except subprocess.TimeoutExpired:
        # Nao conseguimos constatar em tempo habil -> nunca trancar.
        klog("VERIFY", "fail-open: timeout cmd='{}'".format(cmd))
        return None
    except Exception as e:
        klog("VERIFY", "fail-open: erro ao rodar cmd='{}' ({})".format(cmd, type(e).__name__))
        return None

    if code == 0:
        klog("VERIFY", "cmd='{}' PASS".format(cmd))
        return None

    # Constatou FALHA. BLOQUEAR com a saida real (tail).
    klog("VERIFY", "cmd='{}' FAIL exit={}".format(cmd, code))
    return (
        "Verificacao falhou (constatado): {} exit={}. "
        "Corrija e rode de novo. Saida:\n{}\n"
        "(Override consciente: inclua [verify:skip motivo].)"
    ).format(cmd, code, _tail(out))


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
