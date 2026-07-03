# -*- coding: utf-8 -*-
"""FASE 2 — Projeto multi-arquivo com CONTRATOS CRUZADOS sob pressão de contexto.

3 arquivos que se importam. Escrever o 3º exige lembrar as assinaturas do 1º e 2º.
SEM Aliança: histórico cru numa janela; contratos antigos saem da janela -> chamada errada.
COM Aliança: contratos + arquivos vivem em disco e são recarregados a cada arquivo novo.
Métrica: o projeto montado importa e total(['caneta','caderno','mochila'],'PROMO10')==87.75 ?
"""
import os, re, sys, json, time, shutil, subprocess, requests

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work_p2"); os.makedirs(WORK, exist_ok=True)
MODEL = os.environ.get("BENCH_MODEL", "qwen2.5-coder:7b")
OLLAMA = "http://127.0.0.1:11434/api/generate"
N = int(os.environ.get("P2_N", "2"))
CTXS = [int(x) for x in os.environ.get("P2_CTXS", "1200,20000").split(",")]
NUMPREDICT = int(os.environ.get("P2_NUMPREDICT", "500"))

SYS_ALIANCA = open(os.path.join(BASE, "system_alianca.txt"), encoding="utf-8").read()
SYS_BASE = open(os.path.join(BASE, "system_baseline.txt"), encoding="utf-8").read()

CONTRATOS = """Sistema de pedidos em 3 arquivos Python que se importam. CONTRATOS FIXOS (nomes e regras exatos, não invente):
- catalogo.py: função buscar_valor(sku: str) -> float. Tabela: 'AX9'=2.5, 'KT3'=15.0, 'MZ7'=80.0; sku desconhecido -> -1.0.
- desconto.py: importa buscar_valor de catalogo. Funções:
    somar_itens(skus: list) -> float  (soma buscar_valor(sku) de cada sku, IGNORANDO os que derem -1.0)
    promo(valor: float, codigo: str) -> float  (codigo 'ZK88' -> 12% de desconto; 'HALF' -> 50% de desconto; outro codigo -> sem alteração)
- pedido.py: importa de desconto. Função:
    finalizar(skus: list, codigo: str) -> float = promo(somar_itens(skus), codigo)
Exemplo esperado: finalizar(['AX9','KT3','MZ7'], 'ZK88') == 85.8"""

NOISE = (" [conversa paralela: o usuário comenta sobre o clima, um jogo de ontem e uma receita — "
         "nada disso muda os contratos; ignore ao gerar o código, mas ocupa espaço no histórico.] ")

# (nome_do_arquivo, instrução do turno)
TURNS = [
    ("catalogo.py", "Escreva agora APENAS o arquivo catalogo.py. Só o código."),
    ("desconto.py", "Escreva agora APENAS o arquivo desconto.py, importando e usando corretamente o que catalogo.py oferece." + NOISE + " Só o código."),
    ("pedido.py",   "Escreva agora APENAS o arquivo pedido.py, importando e usando corretamente o que desconto.py oferece." + NOISE + " Só o código."),
    ("pedido.py",   "Revise pedido.py e garanta que total() devolve exatamente o valor esperado do exemplo." + NOISE + " Só o código."),
]

CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
def extract(text):
    b = CODE_RE.findall(text)
    if b: return max(b, key=len).strip()
    m = re.search(r"```(?:python|py)?\s*\n(.*)$", text, re.DOTALL | re.IGNORECASE)
    return (m.group(1).strip() if m else text.strip())

def gen(system, prompt, seed):
    p = {"model": MODEL, "system": system, "prompt": prompt, "stream": False,
         "options": {"temperature": 0.2, "seed": seed, "num_ctx": 8192, "top_p": 0.9,
                     "num_predict": NUMPREDICT}}
    r = requests.post(OLLAMA, json=p, timeout=300); r.raise_for_status()
    return r.json()["response"]

def save(d, fname, code):
    open(os.path.join(d, fname), "w", encoding="utf-8").write(code)

def verify(d):
    try:
        p = subprocess.run([sys.executable, os.path.join(BASE, "verify_proj.py"), d],
                           capture_output=True, text=True, timeout=25)
        line = (p.stdout or "").strip().splitlines()
        return json.loads(line[-1]) if line else {"err": "sem stdout", "total_ok": False,
                                                   "catalogo": False, "desconto": False, "pedido": False}
    except Exception as e:
        return {"err": "verify:" + repr(e)[:80], "total_ok": False,
                "catalogo": False, "desconto": False, "pedido": False}

def run_session(cond, ctx, rep):
    d = os.path.join(WORK, f"{ctx}_{cond}_{rep}");
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
    seed = 300 + rep
    if cond == "baseline":
        transcript = ""
        for t, (fname, instr) in enumerate(TURNS):
            if t == 0:
                prompt = CONTRATOS + "\n\n" + instr
                transcript += "USUARIO: " + prompt + "\n"
                send = prompt                       # turno 0 completo
            else:
                transcript += "USUARIO: " + instr + "\n"
                send = transcript[-ctx:]            # janela crua
            resp = gen(SYS_BASE, send, seed)
            transcript += "ASSISTENTE:\n" + resp + "\n"
            save(d, fname, extract(resp))
    else:  # alianca — recarrega contratos + arquivos do disco
        written = {}
        for t, (fname, instr) in enumerate(TURNS):
            ctx_files = "\n".join(f"--- {n} (em disco) ---\n{c}" for n, c in written.items())
            prompt = ("CONTRATOS (fonte da verdade, em disco):\n" + CONTRATOS +
                      ("\n\nARQUIVOS JÁ ESCRITOS:\n" + ctx_files if ctx_files else "") +
                      "\n\nTAREFA: " + instr)
            resp = gen(SYS_ALIANCA, prompt, seed)
            code = extract(resp)
            save(d, fname, code)
            written[fname] = code
    return verify(d)

def score(v):
    return (2*bool(v.get("catalogo")) + 2*bool(v.get("desconto")) +
            2*bool(v.get("pedido")) + 4*bool(v.get("total_ok")))

def main():
    out = []
    total = len(CTXS)*2*N; done = 0
    for ctx in CTXS:
        for cond in ("baseline", "alianca"):
            for rep in range(N):
                t0 = time.time()
                try:
                    v = run_session(cond, ctx, rep); err = v.get("err", "")
                except Exception as e:
                    v = {"total_ok": False, "catalogo": False, "desconto": False, "pedido": False}
                    err = "SESSION:" + repr(e)[:80]
                sc = score(v); done += 1
                rec = {"ctx": ctx, "cond": cond, "rep": rep, "score": sc, "verify": v,
                       "secs": round(time.time()-t0, 1), "err": err}
                out.append(rec)
                print(f"[{done}/{total}] ctx={ctx:6d} {cond:9s} rep{rep}  nota={sc:2d}/10  "
                      f"total={v.get('total_val')} ok={v.get('total_ok')} ({rec['secs']}s) {err[:40]}",
                      flush=True)
    json.dump(out, open(os.path.join(BASE, "results_p2.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n==== RESUMO FASE 2 (nota /10; integração total==87.75 vale 4) ====")
    print(f"{'janela':>8} | {'SEM Aliança':>12} | {'COM Aliança':>12} | {'Δ':>6}")
    for ctx in CTXS:
        b = [r["score"] for r in out if r["ctx"] == ctx and r["cond"] == "baseline"]
        a = [r["score"] for r in out if r["ctx"] == ctx and r["cond"] == "alianca"]
        ib = 100*sum(1 for r in out if r["ctx"]==ctx and r["cond"]=="baseline" and r["verify"].get("total_ok"))/max(len(b),1)
        ia = 100*sum(1 for r in out if r["ctx"]==ctx and r["cond"]=="alianca" and r["verify"].get("total_ok"))/max(len(a),1)
        mb = sum(b)/len(b) if b else 0; ma = sum(a)/len(a) if a else 0
        print(f"{ctx:>8} | {mb:>7.1f} (int {ib:3.0f}%) | {ma:>7.1f} (int {ia:3.0f}%) | {ma-mb:>+6.1f}")
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
