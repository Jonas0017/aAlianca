#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest.py — o teste-de-constatacao do kernel da Alianca.

O terceiro portao (verify.py) estava INERTE: sem verify.cmd nada rodava, e o
kernel nao tinha teste proprio. Este arquivo fecha as duas pontas de uma vez:

  1. E o comando que o verify.cmd DESTE repo executa. Assim o Stop hook do
     proprio harness passa a rodar este self-test: o kernel se verifica com o
     proprio terceiro portao.
  2. CONSTATA (nao mocka): roda os hooks REAIS (route/gate/verify) como
     subprocesso com stdin controlado e le a saida/exit REAL; ou importa e
     chama as funcoes puras quando isso for mais limpo (expand_pulls) e
     mais barato (compile).

Principios:
  - DETERMINISTICO: nenhuma dependencia de Date.now()/random. Entradas fixas.
  - RAPIDO: poucos spawns, < ~2s no total.
  - FAIL-FAST: imprime PASS por caso; no PRIMEIRO fracasso imprime FAIL com o
    detalhe e sai com exit != 0 (esse exit code e o que verify.py vai ler).
  - SEM RECURSAO: os fixtures de verify.py rodam em diretorio TEMPORARIO
    isolado, com COPIA de verify.py e verify.cmd proprio de fixture — NUNCA o
    verify.cmd real deste repo (que re-dispararia este self-test -> loop).

Uso:
    python selftest.py        # exit 0 se tudo passa; != 0 no primeiro fracasso
"""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

# stdout utf-8 (Windows costuma vir cp1252; os textos tem acento).
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python"

ROUTE = os.path.join(HERE, "route.py")
GATE = os.path.join(HERE, "gate.py")
VERIFY = os.path.join(HERE, "verify.py")
KLOG = os.path.join(HERE, "klog.py")
COMPILE = os.path.join(HERE, "compile.py")
INDEX = os.path.abspath(os.path.join(HERE, os.pardir, "router.index.json"))

_PASSES = 0


def _fail(name, detail):
    """Imprime o FAIL e ABORTA com exit != 0 (fail-fast: primeiro fracasso)."""
    print("FAIL  {0}".format(name))
    print("      -> {0}".format(detail))
    print("")
    print("RESUMO: FALHOU em '{0}' (apos {1} PASS).".format(name, _PASSES))
    sys.exit(1)


def check(name, cond, detail=""):
    """Constata uma expectativa. PASS segue; FAIL aborta."""
    global _PASSES
    if cond:
        _PASSES += 1
        print("PASS  {0}".format(name))
    else:
        _fail(name, detail or "condicao falsa")


# ---------------------------------------------------------------------------
# Runners dos hooks reais (subprocesso, stdin controlado)
# ---------------------------------------------------------------------------
def run_hook(script, payload, cwd=None):
    """Roda um hook como subprocesso; devolve (exit, stdout, stderr)."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    proc = subprocess.run(
        [PY, script],
        input=data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", "replace"),
        proc.stderr.decode("utf-8", "replace"),
    )


def route_context(prompt):
    """Roda route.py e devolve o additionalContext injetado (str)."""
    code, out, _err = run_hook(ROUTE, {"prompt": prompt})
    if code != 0:
        _fail("route[{0}]".format(prompt), "route.py saiu != 0 (exit={0})".format(code))
    try:
        obj = json.loads(out)
        return obj["hookSpecificOutput"]["additionalContext"]
    except Exception as e:
        _fail("route[{0}]".format(prompt), "stdout nao-JSON: {0} :: {1!r}".format(e, out[:200]))


# ===========================================================================
# 1) route.py — roteamento determinista, grafo de pulls, gate do coordenador
# ===========================================================================
def test_route():
    COORD = "== Modo coordenador =="
    PUXADO_SEC = "(puxado por security)"

    # (a) "integrar pagamento com cartao": security no topo + bug-prevention e
    #     testing PUXADOS por security + bloco coordenador presente.
    ctx = route_context("integrar pagamento com cartao")
    i_sec = ctx.find("security -> ")
    i_bug = ctx.find("bug-prevention -> ")
    i_test = ctx.find("testing -> ")
    check("route/pagamento: security presente e no topo",
          i_sec >= 0 and i_bug > i_sec and i_test > i_sec,
          "sec={0} bug={1} test={2}\n{3}".format(i_sec, i_bug, i_test, ctx))
    check("route/pagamento: bug-prevention e testing puxados por security",
          ctx.count(PUXADO_SEC) >= 2,
          "esperava 2x '(puxado por security)':\n{0}".format(ctx))
    check("route/pagamento: bloco coordenador presente (execucao pesada)",
          COORD in ctx, ctx)

    # (b) "senha" (uma palavra): security + pulls, mas SEM coordenador.
    #     REGRESSAO CORRIGIDA HOJE: o gate do coordenador avalia SO os diretos
    #     (matched=security, 1 modulo de codigo) e NAO os puxados. Se voltar a
    #     avaliar os puxados (security+bug-prevention+testing = 3 de codigo),
    #     o coordenador dispararia espuriamente e este caso TEM que travar.
    ctx = route_context("senha")
    check("route/senha: security presente",
          "security -> " in ctx, ctx)
    check("route/senha: pulls presentes (grafo intacto)",
          PUXADO_SEC in ctx, ctx)
    check("route/senha: SEM coordenador (gate avalia so os diretos) [regressao]",
          COORD not in ctx,
          "coordenador vazou avaliando os PUXADOS:\n{0}".format(ctx))

    # (c) "escreve um teste de cobertura": testing SO, sem pulls, sem inflacao.
    ctx = route_context("escreve um teste de cobertura")
    check("route/teste: testing presente",
          "testing -> " in ctx, ctx)
    check("route/teste: sem security",
          "security -> " not in ctx, ctx)
    check("route/teste: sem pulls (testing nao tem 'pulls') e sem coordenador",
          "(puxado por" not in ctx and COORD not in ctx, ctx)

    # (d) "ola tudo bem": BASE (sem modulos, sem coordenador).
    ctx = route_context("ola tudo bem")
    # Base = so HEADER + LOOP. Sem cabecalho de lista e sem bullets de modulo.
    # (O LOOP em si contem setas '->', entao checamos os marcadores da lista.)
    check("route/base: sem lista de modulos",
          "Carregue ANTES de agir" not in ctx and "  * " not in ctx, ctx)
    check("route/base: sem coordenador",
          COORD not in ctx, ctx)


# ===========================================================================
# 1b) route.py — CALIBRACAO (prompts REAIS que geraram falso positivo)
# ===========================================================================
def test_route_calibration():
    # Os 3 prompts ruidosos vieram de uma sessao real (kernel.log). Cada um
    # roteava modulos errados por keyword DERIVADA generica ('revisao', 'mas',
    # 'multi', 'tarefa') ou keyword curada frouxa ('estrutura', 'todo').

    # (1) "revisao completa do projeto" -> SO x9 (auditoria). Antes puxava
    #     agents ('revisao' derivada do trigger de agents) e outros.
    ctx = route_context("faz uma revisão completa desse projeto")
    check("calib/revisao-completa: x9 roteado", "x9 -> " in ctx, ctx)
    for spurio in ("agents", "adopt", "security", "bug-prevention",
                   "testing", "snapshot"):
        check("calib/revisao-completa: sem {0} (falso positivo)".format(spurio),
              spurio + " -> " not in ctx, ctx)

    # (2) pedido de parecer/analise -> nada ou x9. Antes: architecture
    #     ('estrutura'), adopt ('mas'!), agents ('revisao').
    ctx = route_context(
        "ok, vc tá fazendo uma revisão seguindo a estrutura atual do projeto "
        "seguindo as regras, mas eu quero uma análise mais completa e um "
        "parecer seu, pontos de melhoria, ajustes, coisas que podemos "
        "melhorar nesse projeto")
    for spurio in ("architecture", "adopt", "agents"):
        check("calib/parecer: sem {0} (falso positivo)".format(spurio),
              spurio + " -> " not in ctx, ctx)

    # (3) "multiplos agentes" -> agents (x9 aceitavel). Antes: snapshot
    #     ('multi' derivada) e x9 via 'todo' casando 'todos'.
    ctx = route_context(
        "pode atacar todos juntos, corrija tudo de uma vez com multiplos agentes")
    check("calib/multiplos-agentes: agents roteado", "agents -> " in ctx, ctx)
    check("calib/multiplos-agentes: sem snapshot (falso positivo 'multi')",
          "snapshot -> " not in ctx, ctx)

    # Matches LEGITIMOS que a calibracao NAO pode quebrar.
    ctx = route_context("tem senha hardcoded aqui?")
    check("calib/senha-hardcoded: security roteado", "security -> " in ctx, ctx)

    ctx = route_context("escreve testes pra essa função")
    check("calib/escreve-testes: testing roteado", "testing -> " in ctx, ctx)

    ctx = route_context("cria uma tarefa pra isso")
    check("calib/cria-tarefa: tasks roteado", "tasks -> " in ctx, ctx)
    check("calib/cria-tarefa: sem agents/snapshot (falso positivo 'tarefa')",
          "agents -> " not in ctx and "snapshot -> " not in ctx, ctx)

    ctx = route_context("audita as pontas soltas")
    check("calib/audita-pontas: x9 roteado", "x9 -> " in ctx, ctx)

    ctx = route_context("divide esse trabalho entre agentes")
    check("calib/divide-agentes: agents roteado", "agents -> " in ctx, ctx)


# ===========================================================================
# 1c) select_modules — forca minima 2 para keywords DERIVADAS (anti-ruido)
# ===========================================================================
_DERIVED_MIN2_SRC = r'''
import json, os, sys
sys.path.insert(0, os.environ["ALIANCA_KERNEL_DIR"])
import route
idx = {"modules": {
    "derivado": {"file": "instructions/derivado.md", "trigger": "t",
                 "keywords": ["alpha", "beta"], "keywordsDerived": True,
                 "priority": None},
    "curado": {"file": "instructions/curado.md", "trigger": "t",
               "keywords": ["alpha"], "priority": None},
}}
out = {}
for prompt in ("quero alpha", "quero alpha e beta"):
    tokens = route.tokenize(prompt)
    norm = route.strip_accents(prompt)
    sel = route.select_modules(idx, tokens, norm)
    out[prompt] = sorted(n for (n, _m, _s) in sel)
sys.stdout.write(json.dumps(out))
'''


def test_derived_min_strength():
    env = dict(os.environ)
    env["ALIANCA_KERNEL_DIR"] = HERE
    proc = subprocess.run([PY, "-c", _DERIVED_MIN2_SRC],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if proc.returncode != 0:
        _fail("route/derivado-min2",
              "exit!=0: {0}".format(proc.stderr.decode("utf-8", "replace")[:300]))
    out = json.loads(proc.stdout.decode("utf-8", "replace"))
    check("route/derivado-min2: 1 keyword derivada NAO seleciona (curada sim)",
          out["quero alpha"] == ["curado"], "sel={0}".format(out))
    check("route/derivado-min2: 2 keywords derivadas selecionam",
          out["quero alpha e beta"] == ["curado", "derivado"],
          "sel={0}".format(out))


# ===========================================================================
# 2) expand_pulls — aresta quebrada ignorada + teto respeitado (funcao pura)
# ===========================================================================
# Sub-script isolado: importa route e exercita expand_pulls sobre um indice
# sintetico. Roda em subprocesso PROPRIO porque route.py, ao ser importado,
# reembrulha sys.stdout (efeito colateral de modulo) — o que fecharia o stdout
# deste selftest se importassemos in-process. Constata na mesma, isolado.
_BROKEN_EDGE_SRC = r'''
import json, os, sys
sys.path.insert(0, os.environ["ALIANCA_KERNEL_DIR"])
import route
idx = {"modules": {
    "alpha": {"file": "instructions/alpha.md", "trigger": "t",
              "keywords": ["alpha"], "priority": 0,
              "pulls": ["ghost", "p1", "p2", "p3", "p4", "p5", "p6"]},
    "p1": {"trigger": "", "keywords": [], "priority": 1},
    "p2": {"trigger": "", "keywords": [], "priority": 2},
    "p3": {"trigger": "", "keywords": [], "priority": 3},
    "p4": {"trigger": "", "keywords": [], "priority": 4},
    "p5": {"trigger": "", "keywords": [], "priority": 5},
    "p6": {"trigger": "", "keywords": [], "priority": 6},
}}
sel = route.cap_modules(route.select_modules(idx, ["alpha"], "alpha"))
exp = route.expand_pulls(sel, idx)
sys.stdout.write(json.dumps([item[0] for item in exp]))
'''


def test_broken_edge():
    # Indice sintetico: 'alpha' PUXA um alvo INEXISTENTE ('ghost') + 6 reais.
    # Espera: ghost ignorado sem excecao; teto de 5 respeitado.
    env = dict(os.environ)
    env["ALIANCA_KERNEL_DIR"] = HERE
    proc = subprocess.run([PY, "-c", _BROKEN_EDGE_SRC],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if proc.returncode != 0:
        _fail("expand_pulls/aresta-quebrada",
              "lancou excecao/exit!=0: {0}".format(
                  proc.stderr.decode("utf-8", "replace")[:300]))
    try:
        names = json.loads(proc.stdout.decode("utf-8", "replace"))
    except Exception as e:
        _fail("expand_pulls/aresta-quebrada",
              "stdout nao-JSON: {0} :: {1!r}".format(e, proc.stdout[:160]))
    check("expand_pulls: aresta quebrada ('ghost' inexistente) ignorada em silencio",
          "ghost" not in names, "names={0}".format(names))
    check("expand_pulls: teto de pulls respeitado (<=5)",
          len(names) <= 5, "len={0} names={1}".format(len(names), names))


# ===========================================================================
# 3) gate.py — segredo hardcoded bloqueia; placeholder/normal permite
# ===========================================================================
def test_gate():
    def gate_exit(tool, tool_input):
        code, _out, _err = run_hook(GATE, {"tool_name": tool, "tool_input": tool_input})
        return code

    # Segredo real (AWS access key) numa escritura -> BLOQUEIA (exit 2).
    check("gate/segredo-aws: BLOQUEIA (exit 2)",
          gate_exit("Write", {"file_path": "config.py",
                              "content": 'api_key = "AKIAIOSFODNN7EXAMPLE"'}) == 2,
          "esperava exit 2")

    # Credencial em atribuicao (alta entropia) -> BLOQUEIA (exit 2).
    check("gate/segredo-atribuicao: BLOQUEIA (exit 2)",
          gate_exit("Edit", {"file_path": "auth.py",
                             "new_string": 'password = "P@ssw0rd12345"'}) == 2,
          "esperava exit 2")

    # Valor placeholder -> PERMITE (exit 0).
    check("gate/placeholder: PERMITE (exit 0)",
          gate_exit("Write", {"file_path": "config.py",
                              "content": 'api_key = "your_api_key_here"'}) == 0,
          "esperava exit 0")

    # Codigo normal -> PERMITE (exit 0).
    check("gate/codigo-normal: PERMITE (exit 0)",
          gate_exit("Edit", {"file_path": "main.py",
                             "new_string": "def soma(a, b):\n    return a + b"}) == 0,
          "esperava exit 0")


# ===========================================================================
# 4) verify.py — em diretorio TEMPORARIO ISOLADO (sem tocar o verify.cmd real)
# ===========================================================================
def _write_transcript(dirp, assistant_text):
    tp = os.path.join(dirp, "transcript.jsonl")
    evt = {"type": "assistant",
           "message": {"content": [{"type": "text", "text": assistant_text}]}}
    with open(tp, "w", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")
    return tp


def _run_verify_isolated(assistant_text, verify_cmd_line=None):
    """
    Roda verify.py numa COPIA isolada em temp. O CMD_FILE de verify.py resolve
    por __file__ (o dir da copia), entao damos a ele um verify.cmd de FIXTURE
    (ou nenhum) — jamais o verify.cmd real deste repo. Zero risco de recursao.

    Devolve (exit_code, stdout).
    """
    tdir = tempfile.mkdtemp(prefix="alianca_verify_")
    try:
        shutil.copy(VERIFY, os.path.join(tdir, "verify.py"))
        shutil.copy(KLOG, os.path.join(tdir, "klog.py"))
        if verify_cmd_line is not None:
            with open(os.path.join(tdir, "verify.cmd"), "w", encoding="utf-8") as f:
                f.write("# fixture verify.cmd (isolado) — nao e o do repo\n")
                f.write(verify_cmd_line + "\n")
        transcript = _write_transcript(tdir, assistant_text)
        payload = {"transcript_path": transcript, "cwd": tdir,
                   "stop_hook_active": False}
        proc = subprocess.run(
            [PY, os.path.join(tdir, "verify.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    finally:
        shutil.rmtree(tdir, ignore_errors=True)


def _is_block(stdout):
    try:
        obj = json.loads(stdout)
        return isinstance(obj, dict) and obj.get("decision") == "block"
    except Exception:
        return False


def test_verify():
    # Comando de fixture que FALHA (exit 1) de forma portavel (nao amarra a
    # suite ao cmd.exe): 'python' ja passa no preflight do verify.py e existe
    # em qualquer host onde o kernel roda.
    FAIL_CMD = 'python -c "import sys; sys.exit(1)"'

    # (a) Alegacao de conclusao + verify.cmd que FALHA -> BLOCK.
    code, out = _run_verify_isolated("Tudo pronto e implementado.", FAIL_CMD)
    check("verify/claim+cmd-falha: BLOCK (constatou falha)",
          code == 0 and _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:160]))

    # (b) Alegacao de conclusao + SEM verify.cmd -> ALLOW (enforcement opt-in).
    code, out = _run_verify_isolated("Tudo pronto e implementado.", None)
    check("verify/claim+sem-cmd: ALLOW (opt-in)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:160]))

    # (c) Alegacao + valvula [verify:skip razao] (mesmo com cmd que falha) -> ALLOW.
    code, out = _run_verify_isolated(
        "Pronto. [verify:skip hotfix urgente]", FAIL_CMD)
    check("verify/override [verify:skip razao]: ALLOW (logado)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:160]))

    # (d) Intencao/futuro ("vou concluir") NAO e conclusao -> ALLOW mesmo com
    #     cmd que falha (nada a constatar sem alegacao de pronto).
    code, out = _run_verify_isolated(
        "Vou concluir e finalizar isso na proxima etapa.", FAIL_CMD)
    check("verify/intencao ('vou concluir'): ALLOW (intencao != conclusao)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:160]))


# ===========================================================================
# 4b) verify.py — portao PERSISTIR (5o passo do loop, em layout isolado)
# ===========================================================================
def _iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z")


def _write_persist_transcript(dirp, project_writes, memory_writes=1):
    """Transcript sintetico: user + assistant com tool_use de escrita."""
    blocks = [{"type": "text", "text": "Editando os arquivos do projeto."}]
    for i in range(project_writes):
        blocks.append({"type": "tool_use", "name": "Edit" if i % 2 == 0 else "Write",
                       "input": {"file_path": os.path.join(dirp, "src", "mod{0}.py".format(i))}})
    for i in range(memory_writes):
        # Escrita em alianca/memory/ NAO conta como trabalho a persistir.
        blocks.append({"type": "tool_use", "name": "Edit",
                       "input": {"file_path": os.path.join(
                           dirp, "alianca", "memory", "nota{0}.md".format(i))}})
    ts = _iso_now()
    eventos = [
        {"type": "user", "timestamp": ts, "message": {"content": "faz ai"}},
        {"type": "assistant", "timestamp": ts, "message": {"content": blocks}},
    ]
    tp = os.path.join(dirp, "transcript.jsonl")
    with open(tp, "w", encoding="utf-8") as f:
        for evt in eventos:
            f.write(json.dumps(evt, ensure_ascii=False) + "\n")
    return tp


def _run_persist_case(project_writes, active_context, active_age_s,
                      stop_hook_active=False):
    """
    Monta um layout isolado tdir/kernel/verify.py + tdir/memory/ e roda o
    Stop hook. active_context=False -> memoria nao inicializada.
    active_age_s -> idade do mtime do active-context.md (segundos atras).
    Devolve (exit_code, stdout).
    """
    tdir = tempfile.mkdtemp(prefix="alianca_persist_")
    try:
        kdir = os.path.join(tdir, "kernel")
        os.makedirs(kdir)
        shutil.copy(VERIFY, os.path.join(kdir, "verify.py"))
        shutil.copy(KLOG, os.path.join(kdir, "klog.py"))
        # NUNCA copiar o verify.cmd real (recursao). Sem claim no texto,
        # o portao do claim permite e cai no PERSISTIR.
        if active_context:
            mdir = os.path.join(tdir, "memory")
            os.makedirs(mdir)
            ac = os.path.join(mdir, "active-context.md")
            with open(ac, "w", encoding="utf-8") as f:
                f.write("# contexto\n")
            old = time.time() - active_age_s
            os.utime(ac, (old, old))
        transcript = _write_persist_transcript(tdir, project_writes)
        payload = {"transcript_path": transcript, "cwd": tdir,
                   "stop_hook_active": stop_hook_active}
        proc = subprocess.run(
            [PY, os.path.join(kdir, "verify.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    finally:
        shutil.rmtree(tdir, ignore_errors=True)


def test_persist():
    # (a) Trabalho substancial (2 escritas no projeto) + active-context.md
    #     VELHO (nao tocado na sessao) -> BLOCK mandando persistir.
    code, out = _run_persist_case(2, active_context=True, active_age_s=3600)
    check("persist/escritas+memoria-velha: BLOCK (PERSISTIR pendente)",
          code == 0 and _is_block(out) and "active-context" in out,
          "exit={0} stdout={1!r}".format(code, out[:200]))

    # (b) Mesmo cenario com stop_hook_active -> ALLOW (anti-loop SEMPRE).
    code, out = _run_persist_case(2, active_context=True, active_age_s=3600,
                                  stop_hook_active=True)
    check("persist/stop_hook_active: ALLOW (anti-loop)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:200]))

    # (c) Sem active-context.md (memoria nao inicializada) -> ALLOW.
    code, out = _run_persist_case(2, active_context=False, active_age_s=0)
    check("persist/sem-active-context: ALLOW (memoria nao inicializada)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:200]))

    # (d) active-context.md atualizado DURANTE a sessao (mtime fresco) -> ALLOW.
    code, out = _run_persist_case(2, active_context=True, active_age_s=0)
    check("persist/memoria-atualizada: ALLOW (persistiu na sessao)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:200]))

    # (e) 1 escrita so (< minimo) -> ALLOW (nao e trabalho substancial;
    #     as escritas em alianca/memory/ do fixture nao contam).
    code, out = _run_persist_case(1, active_context=True, active_age_s=3600)
    check("persist/1-escrita: ALLOW (abaixo do minimo de substancial)",
          code == 0 and not _is_block(out),
          "exit={0} stdout={1!r}".format(code, out[:200]))


# ===========================================================================
# 4c) klog.py — append + tail + _summary (num log SINTETICO, nunca o real)
# ===========================================================================
def test_klog():
    spec = importlib.util.spec_from_file_location("alianca_klog_test", KLOG)
    kmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kmod)

    tdir = tempfile.mkdtemp(prefix="alianca_klog_")
    try:
        kmod.LOG_PATH = os.path.join(tdir, "kernel.log")  # log sintetico
        kmod.klog("route", "mods=[x9] pulls=[]")
        kmod.klog("VERIFY", "persist: block\tcom tab e\nquebra")
        linhas = kmod.tail(10)
        check("klog: append gravou 2 linhas", len(linhas) == 2,
              "linhas={0!r}".format(linhas))
        check("klog: EVENT normalizado em caixa alta",
              linhas[0].split("\t")[1] == "ROUTE", linhas[0])
        check("klog: tab/quebra sanitizados no detail (TSV integro)",
              len(linhas[1].split("\t")) == 3 and "\n" not in linhas[1],
              linhas[1])
        check("klog: tail(1) devolve so a ultima",
              kmod.tail(1) == linhas[-1:], "tail(1)={0!r}".format(kmod.tail(1)))
        resumo = "\n".join(kmod._summary(10))
        check("klog: _summary conta os 2 registros e destaca o block",
              "2 registros" in resumo and "VERIFY block: 1" in resumo, resumo)
        # Log ausente -> 'sem registros ainda' (fail-open do dmesg).
        kmod.LOG_PATH = os.path.join(tdir, "inexistente.log")
        check("klog: _summary com log ausente -> 'sem registros ainda'",
              kmod._summary(5) == ["sem registros ainda"],
              "{0!r}".format(kmod._summary(5)))
    finally:
        shutil.rmtree(tdir, ignore_errors=True)


# ===========================================================================
# 4d) compile.py — frontmatter: continuacao multi-linha com "Palavra:" no meio
# ===========================================================================
def test_frontmatter_multiline():
    spec = importlib.util.spec_from_file_location("alianca_compile_test", COMPILE)
    cmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cmod)

    texto = (
        "---\n"
        "trigger: auditar o projeto em busca de pontas soltas.\n"
        "Nota: esta linha e CONTINUACAO do trigger, nao chave nova\n"
        "keywords: alpha, beta\n"
        "---\n"
        "corpo do modulo\n"
    )
    fm = cmod.parse_frontmatter(texto)
    check("frontmatter: parse ok", isinstance(fm, dict), repr(fm))
    check("frontmatter: 'Nota:' anexada ao trigger (nao vira chave)",
          "Nota" not in fm and "CONTINUACAO do trigger" in fm.get("trigger", ""),
          repr(fm))
    check("frontmatter: chave conhecida depois da continuacao segue valendo",
          fm.get("keywords") == "alpha, beta", repr(fm))


# ===========================================================================
# 5) compile.py — idempotente + emite 'pulls' p/ security e refactor
# ===========================================================================
def test_compile():
    def compile_once():
        proc = subprocess.run([PY, COMPILE], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        if proc.returncode != 0:
            _fail("compile", "compile.py saiu != 0 (exit={0}) :: {1}".format(
                proc.returncode, proc.stderr.decode("utf-8", "replace")[:200]))
        with open(INDEX, "rb") as f:
            return f.read()

    # Roda 2x; o router.index.json deve ficar BYTE-A-BYTE identico (idempotente).
    first = compile_once()
    second = compile_once()
    check("compile: idempotente (index identico apos 2 execucoes)",
          first == second, "bytes divergiram entre a 1a e a 2a compilacao")

    # 'pulls' emitido para security (-> testing, bug-prevention) e refactor.
    idx = json.loads(second.decode("utf-8"))
    mods = idx.get("modules", {})
    check("compile: 'pulls' emitido p/ security",
          isinstance(mods.get("security", {}).get("pulls"), list)
          and mods["security"]["pulls"],
          "security.pulls ausente/vazio: {0}".format(mods.get("security")))
    check("compile: 'pulls' emitido p/ refactor",
          isinstance(mods.get("refactor", {}).get("pulls"), list)
          and mods["refactor"]["pulls"],
          "refactor.pulls ausente/vazio: {0}".format(mods.get("refactor")))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print("== Alianca kernel — selftest (constata, nao mocka) ==")
    print("")
    test_route()
    test_route_calibration()
    test_derived_min_strength()
    test_broken_edge()
    test_gate()
    test_verify()
    test_persist()
    test_klog()
    test_frontmatter_multiline()
    test_compile()
    print("")
    print("RESUMO: {0} PASS — kernel verificado.".format(_PASSES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
