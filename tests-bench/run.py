# -*- coding: utf-8 -*-
"""Runner do benchmark: com vs sem Aliança, mesmo modelo ollama.

Nota por geração (0-10):
  extraivel (bloco de código presente) .... 2
  executa  (roda sem erro + símbolo def) .. 2
  correto  (fração dos casos core) ........ 4
  robusto  (fração dos casos de borda) .... 2
"""
import os, re, sys, json, time, subprocess, requests

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work")
MODEL = os.environ.get("BENCH_MODEL", "qwen2.5-coder:7b")
N = int(os.environ.get("BENCH_N", "3"))
OLLAMA = "http://127.0.0.1:11434/api/generate"

sys.path.insert(0, BASE)
import tasks as T

SYS = {
    "baseline": open(os.path.join(BASE, "system_baseline.txt"), encoding="utf-8").read(),
    "alianca":  open(os.path.join(BASE, "system_alianca.txt"),  encoding="utf-8").read(),
}

CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)

def extract_code(text):
    blocks = CODE_RE.findall(text)
    if blocks:
        # pega o maior bloco (o entregável costuma ser o mais completo)
        return max(blocks, key=len), True
    return text, False  # sem cerca: tenta o texto cru

def gen(system, prompt, seed):
    payload = {
        "model": MODEL, "system": system, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.2, "seed": seed, "num_ctx": 8192, "top_p": 0.9},
    }
    r = requests.post(OLLAMA, json=payload, timeout=600)
    r.raise_for_status()
    return r.json()["response"]

def score_gen(task, text, tag):
    code, fenced = extract_code(text)
    fpath = os.path.join(WORK, tag + ".py")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(code)
    extraivel = 2 if (fenced and code.strip()) else (1 if code.strip() else 0)
    v = {"exec": False, "symbol": False, "core": 0.0, "edge": 0.0, "err": "no-run"}
    try:
        p = subprocess.run([sys.executable, os.path.join(BASE, "verify_one.py"), task["id"], fpath],
                           capture_output=True, text=True, timeout=20)
        line = (p.stdout or "").strip().splitlines()
        if line:
            v = json.loads(line[-1])
        else:
            v["err"] = "sem stdout; " + (p.stderr or "")[:150]
    except subprocess.TimeoutExpired:
        v["err"] = "timeout (loop infinito?)"
    executa = 2 if (v["exec"] and v["symbol"]) else (1 if v["exec"] else 0)
    correto = 4 * v["core"]
    robusto = 2 * v["edge"]
    total = extraivel + executa + correto + robusto
    return {
        "total": round(total, 2), "extraivel": extraivel, "executa": executa,
        "correto": round(correto, 2), "robusto": round(robusto, 2),
        "fenced": fenced, "err": v["err"], "chars": len(text),
    }

def main():
    results = []
    conditions = ["baseline", "alianca"]
    total_runs = len(T.TASKS) * len(conditions) * N
    done = 0
    for task in T.TASKS:
        for cond in conditions:
            for i in range(N):
                seed = 100 + i  # mesma semente entre condições -> justo
                tag = f"{task['id']}__{cond}__{i}"
                t0 = time.time()
                try:
                    text = gen(SYS[cond], task["prompt"], seed)
                    err = ""
                except Exception as e:
                    text, err = "", "GEN_ERR:" + repr(e)[:150]
                with open(os.path.join(WORK, tag + ".out.txt"), "w", encoding="utf-8") as f:
                    f.write(text)
                sc = score_gen(task, text, tag) if text else {
                    "total": 0, "extraivel": 0, "executa": 0, "correto": 0,
                    "robusto": 0, "fenced": False, "err": err, "chars": 0}
                sc.update({"task": task["id"], "cond": cond, "run": i,
                           "secs": round(time.time() - t0, 1)})
                results.append(sc)
                done += 1
                print(f"[{done}/{total_runs}] {tag:34s} nota={sc['total']:5.2f} "
                      f"({sc['secs']}s) err={sc['err'][:40]}", flush=True)
    with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
