# -*- coding: utf-8 -*-
"""Importa um arquivo gerado e roda o verificador da tarefa. Isolado por subprocesso.
Uso: python verify_one.py <task_id> <caminho_arquivo>
Imprime JSON: {"exec": bool, "symbol": bool, "core": float, "edge": float, "err": str}
"""
import sys, json, importlib.util, io, contextlib

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import tasks as T

task_id, path = sys.argv[1], sys.argv[2]
task = next(t for t in T.TASKS if t["id"] == task_id)
out = {"exec": False, "symbol": False, "core": 0.0, "edge": 0.0, "err": ""}

try:
    spec = importlib.util.spec_from_file_location("gen_mod", path)
    mod = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        spec.loader.exec_module(mod)   # roda o arquivo
    out["exec"] = True
    ns = {k: getattr(mod, k) for k in dir(mod)}
    if task["symbol"] in ns and callable(ns[task["symbol"]]):
        out["symbol"] = True
        try:
            core, edge = task["verify"](ns)
            out["core"], out["edge"] = float(core), float(edge)
        except Exception as e:
            out["err"] = "verify:" + repr(e)[:200]
    else:
        out["err"] = "symbol ausente: " + task["symbol"]
except Exception as e:
    out["err"] = "exec:" + repr(e)[:200]

print(json.dumps(out))
