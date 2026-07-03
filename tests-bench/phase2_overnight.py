# -*- coding: utf-8 -*-
"""FASE 2 — versão NOTURNA (mais reps, medição de tokens, isolamento de fatores).

Projeto de 3 arquivos que se importam, contratos ARBITRÁRIOS. Métrica: o projeto montado
importa e finalizar(['AX9','KT3','MZ7'],'ZK88')==85.8 ?

4 condições (2x2) para separar MECANISMO (recarga de disco) de DISCIPLINA (prompt da Aliança):
  baseline          : prompt neutro   + janela crua (sem recarga)   <- controle
  alianca           : prompt Aliança  + recarga de disco            <- produto completo
  alianca_noreload  : prompt Aliança  + janela crua                 <- só a disciplina
  base_reload       : prompt neutro   + recarga de disco            <- só o mecanismo

Além da nota, registra tokens (prompt+geração) por sessão -> permite calcular o CUSTO (ROI).

Rodar (exemplo noturno):
  P2_N=6 P2_CTXS=1200,3000,20000 python phase2_overnight.py > phase2_overnight.log 2>&1
"""
import os, re, sys, json, time, shutil, subprocess, requests

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work_p2_night"); os.makedirs(WORK, exist_ok=True)
MODEL = os.environ.get("BENCH_MODEL", "qwen2.5-coder:7b")
OLLAMA = "http://127.0.0.1:11434/api/generate"
N = int(os.environ.get("P2_N", "6"))
CTXS = [int(x) for x in os.environ.get("P2_CTXS", "1200,3000,20000").split(",")]
NUMPREDICT = int(os.environ.get("P2_NUMPREDICT", "500"))
CONDS = os.environ.get("P2_CONDS", "baseline,alianca,alianca_noreload,base_reload").split(",")

SYS_ALIANCA = open(os.path.join(BASE, "system_alianca.txt"), encoding="utf-8").read()
SYS_BASE = open(os.path.join(BASE, "system_baseline.txt"), encoding="utf-8").read()

# system prompt e uso-de-recarga por condição
COND_CFG = {
    "baseline":         (SYS_BASE,    False),
    "alianca":          (SYS_ALIANCA, True),
    "alianca_noreload": (SYS_ALIANCA, False),
    "base_reload":      (SYS_BASE,    True),
}

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

_TOK = {"prompt": 0, "gen": 0}
def gen(system, prompt, seed):
    p = {"model": MODEL, "system": system, "prompt": prompt, "stream": False,
         "options": {"temperature": 0.2, "seed": seed, "num_ctx": 8192, "top_p": 0.9,
                     "num_predict": NUMPREDICT}}
    r = requests.post(OLLAMA, json=p, timeout=300); r.raise_for_status()
    j = r.json()
    _TOK["prompt"] += j.get("prompt_eval_count", 0)
    _TOK["gen"] += j.get("eval_count", 0)
    return j["response"]

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
    system, use_reload = COND_CFG[cond]
    d = os.path.join(WORK, f"{ctx}_{cond}_{rep}")
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
    seed = 300 + rep
    _TOK["prompt"] = 0; _TOK["gen"] = 0
    if not use_reload:                       # janela crua acumulando
        transcript = ""
        for t, (fname, instr) in enumerate(TURNS):
            if t == 0:
                prompt = CONTRATOS + "\n\n" + instr
                transcript += "USUARIO: " + prompt + "\n"
                send = prompt
            else:
                transcript += "USUARIO: " + instr + "\n"
                send = transcript[-ctx:]
            resp = gen(system, send, seed)
            transcript += "ASSISTENTE:\n" + resp + "\n"
            save(d, fname, extract(resp))
    else:                                    # recarrega contratos + arquivos do disco
        written = {}
        for t, (fname, instr) in enumerate(TURNS):
            ctx_files = "\n".join(f"--- {n} (em disco) ---\n{c}" for n, c in written.items())
            prompt = ("CONTRATOS (fonte da verdade, em disco):\n" + CONTRATOS +
                      ("\n\nARQUIVOS JÁ ESCRITOS:\n" + ctx_files if ctx_files else "") +
                      "\n\nTAREFA: " + instr)
            resp = gen(system, prompt, seed)
            code = extract(resp)
            save(d, fname, code)
            written[fname] = code
    v = verify(d)
    v["tok_prompt"] = _TOK["prompt"]; v["tok_gen"] = _TOK["gen"]
    return v

def score(v):
    return (2*bool(v.get("catalogo")) + 2*bool(v.get("desconto")) +
            2*bool(v.get("pedido")) + 4*bool(v.get("total_ok")))

def main():
    out = []
    total = len(CTXS)*len(CONDS)*N; done = 0
    for ctx in CTXS:
        for cond in CONDS:
            for rep in range(N):
                t0 = time.time()
                try:
                    v = run_session(cond, ctx, rep); err = v.get("err", "")
                except Exception as e:
                    v = {"total_ok": False, "catalogo": False, "desconto": False,
                         "pedido": False, "tok_prompt": 0, "tok_gen": 0}
                    err = "SESSION:" + repr(e)[:80]
                sc = score(v); done += 1
                rec = {"ctx": ctx, "cond": cond, "rep": rep, "score": sc, "verify": v,
                       "tok_prompt": v.get("tok_prompt", 0), "tok_gen": v.get("tok_gen", 0),
                       "secs": round(time.time()-t0, 1), "err": err}
                out.append(rec)
                print(f"[{done}/{total}] ctx={ctx:6d} {cond:17s} rep{rep}  nota={sc:2d}/10  "
                      f"ok={str(v.get('total_ok')):5s} tok(p/g)={v.get('tok_prompt')}/{v.get('tok_gen')} "
                      f"({rec['secs']}s) {err[:30]}", flush=True)
    json.dump(out, open(os.path.join(BASE, "results_p2_night.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n==== RESUMO NOTURNO (nota media /10 · integração% · tokens medios) ====")
    print(f"{'janela':>7} | {'condição':<17} | {'nota':>5} | {'int%':>4} | {'tok tot':>8}")
    for ctx in CTXS:
        for cond in CONDS:
            rows = [r for r in out if r["ctx"] == ctx and r["cond"] == cond]
            if not rows: continue
            nota = sum(r["score"] for r in rows)/len(rows)
            integ = 100*sum(1 for r in rows if r["verify"].get("total_ok"))/len(rows)
            tok = sum(r["tok_prompt"]+r["tok_gen"] for r in rows)/len(rows)
            print(f"{ctx:>7} | {cond:<17} | {nota:>5.1f} | {integ:>3.0f}% | {tok:>8.0f}")
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
