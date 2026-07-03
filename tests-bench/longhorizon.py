# -*- coding: utf-8 -*-
"""FASE 1 — Fidelidade de requisitos no LONGO PRAZO sob pressão de contexto.

Mesma IA, mesma tarefa (10 requisitos checáveis), mesma sequência de turnos.
Única diferença = COMO o contexto é gerido:
  BASELINE : histórico cru acumulando numa janela de CTX_CHARS (dropa o mais antigo -> a spec).
  ALIANÇA  : spec + arquivo vivem em disco e são recarregados a cada turno (janela nunca perde o essencial).

Roda em vários CTX_CHARS. Com janela grande os dois DEVEM empatar (controle anti-viés);
a diferença só pode aparecer sob pressão. Nota = requisitos corretos no fim / 10.
"""
import os, re, sys, json, time, importlib.util, io, contextlib, requests

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work_lh"); os.makedirs(WORK, exist_ok=True)
MODEL = os.environ.get("BENCH_MODEL", "qwen2.5-coder:7b")
OLLAMA = "http://127.0.0.1:11434/api/generate"
N = int(os.environ.get("LH_N", "2"))
CTXS = [int(x) for x in os.environ.get("LH_CTXS", "3000,6000,20000").split(",")]
TURNS = int(os.environ.get("LH_TURNS", "6"))

SYS_ALIANCA = open(os.path.join(BASE, "system_alianca.txt"), encoding="utf-8").read()
SYS_BASE = open(os.path.join(BASE, "system_baseline.txt"), encoding="utf-8").read()

SPEC = """Crie o arquivo `validador.py` com EXATAMENTE estas 10 funções (cada uma retorna bool):
1. valida_email(s): True se s tem um '@' e um '.' depois do '@'.
2. valida_senha(s): True se len>=8 e tem ao menos 1 maiúscula, 1 minúscula e 1 dígito.
3. valida_cep(s): True se, removidos traços/espaços, sobra exatamente 8 dígitos.
4. valida_telefone(s): True se, mantendo só dígitos, sobra 10 ou 11 dígitos.
5. valida_url(s): True se s começa com 'http://' ou 'https://'.
6. valida_data(s): True se s está no formato DD/MM/AAAA com dia 1-31 e mes 1-12.
7. valida_idade(n): True se n é int entre 0 e 150 inclusive.
8. so_letras(s): True se s não é vazio e tem apenas letras (a-z A-Z).
9. valida_hex(s): True se s é cor hex: '#' seguido de 6 dígitos hexadecimais.
10. valida_cartao(s): True se, mantendo só dígitos, sobra exatamente 16 dígitos."""

# tweaks NEUTROS de tamanho: NÃO devem remover nem inchar o arquivo se a IA lembra dos requisitos
TWEAKS = [
    "Faça as funções que recebem string retornarem False se receberem None.",
    "Remova imports que não estejam sendo usados.",
    "Padronize a indentação em 4 espaços.",
    "Troque aspas duplas por aspas simples onde possível.",
    "Garanta que não haja espaços em branco no fim das linhas.",
    "Deixe os nomes de variáveis internas mais claros.",
]
NOISE = (" [contexto paralelo: o usuário tambem conversa sobre outro assunto — "
         "planejamento de uma viagem, receitas de bolo, e detalhes de futebol — "
         "nada disso altera o arquivo, mas ocupa espaço na conversa. Ignore ao gerar o codigo.] ")

CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)

def extract(text):
    b = CODE_RE.findall(text)
    if b:
        return max(b, key=len).strip()
    # bloco cortado no fim (num_predict): pega do último ```python até o fim
    m = re.search(r"```(?:python|py)?\s*\n(.*)$", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text.strip()

NUMPREDICT = int(os.environ.get("LH_NUMPREDICT", "1300"))  # limita saída p/ tempo previsível

def gen(system, prompt, seed, num_ctx=8192):
    p = {"model": MODEL, "system": system, "prompt": prompt, "stream": False,
         "options": {"temperature": 0.2, "seed": seed, "num_ctx": num_ctx, "top_p": 0.9,
                     "num_predict": NUMPREDICT}}
    r = requests.post(OLLAMA, json=p, timeout=300); r.raise_for_status()
    return r.json()["response"]

# ---------- verificador dos 10 requisitos ----------
def verify(code):
    fpath = os.path.join(WORK, "_tmp_verify.py")
    open(fpath, "w", encoding="utf-8").write(code)
    checks = {
        "valida_email":    [("a@b.com", True), ("ab.com", False), ("a@bcom", False)],
        "valida_senha":    [("Abcdef12", True), ("abcdef12", False), ("Abc1", False)],
        "valida_cep":      [("12345-678", True), ("1234567", False)],
        "valida_telefone": [("(11) 91234-5678", True), ("1234", False)],
        "valida_url":      [("https://x.com", True), ("ftp://x", False)],
        "valida_data":     [("25/12/2020", True), ("32/01/2020", False), ("2020-12-25", False)],
        "valida_idade":    [(30, True), (200, False), (-1, False)],
        "so_letras":       [("abcDEF", True), ("abc1", False), ("", False)],
        "valida_hex":      [("#a1b2c3", True), ("a1b2c3", False), ("#12345", False)],
        "valida_cartao":   [("1234 5678 9012 3456", True), ("1234", False)],
    }
    results = {k: False for k in checks}
    try:
        spec = importlib.util.spec_from_file_location("val_mod", fpath)
        mod = importlib.util.module_from_spec(spec)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            spec.loader.exec_module(mod)
    except Exception:
        return results, 0  # arquivo nem roda -> 0 requisitos
    present = 0
    for name, cases in checks.items():
        fn = getattr(mod, name, None)
        if not callable(fn):
            continue
        present += 1
        ok = True
        for arg, exp in cases:
            try:
                if bool(fn(arg)) != exp:
                    ok = False; break
            except Exception:
                ok = False; break
        results[name] = ok
    return results, present

# ---------- uma sessão completa ----------
def run_baseline(seed, ctx_chars):
    """Histórico cru acumulando; janela = últimos ctx_chars caracteres."""
    transcript = ""
    def window():
        return transcript[-ctx_chars:]
    # turno 0: spec cabe (sessão começa com a spec no contexto; a pressão vem depois)
    u0 = SPEC + "\n\nImplemente o arquivo completo agora, código enxuto. Só o código."
    transcript += "USUARIO: " + u0 + "\n"
    resp = gen(SYS_BASE, u0, seed)          # turno 0 SEM janela (spec inteira)
    transcript += "ASSISTENTE:\n" + resp + "\n"
    last = extract(resp)
    for t in range(TURNS):
        u = TWEAKS[t % len(TWEAKS)] + NOISE + " Devolva o ARQUIVO COMPLETO, só o código."
        transcript += "USUARIO: " + u + "\n"
        resp = gen(SYS_BASE, window(), seed)
        transcript += "ASSISTENTE:\n" + resp + "\n"
        last = extract(resp)
    return last

def run_alianca(seed, ctx_chars):
    """spec + arquivo em 'disco'; recarrega só o essencial a cada turno."""
    reqs = SPEC                      # fonte da verdade, sempre recarregada
    u0 = reqs + "\n\nImplemente o arquivo completo agora. Só o código."
    resp = gen(SYS_ALIANCA, u0, seed)
    latest = extract(resp)
    for t in range(TURNS):
        prompt = ("REQUISITOS (fonte da verdade em disco — o arquivo DEVE conter as 10 funções):\n"
                  + reqs + "\n\nARQUIVO ATUAL (em disco):\n```python\n" + latest + "\n```\n\n"
                  + "TAREFA: " + TWEAKS[t % len(TWEAKS)] + NOISE
                  + "\nDevolva o ARQUIVO COMPLETO com as 10 funções, só o código.")
        resp = gen(SYS_ALIANCA, prompt, seed)
        latest = extract(resp)
    return latest

def main():
    out = []
    total = len(CTXS) * 2 * N
    done = 0
    for ctx in CTXS:
        for cond, fn in [("baseline", run_baseline), ("alianca", run_alianca)]:
            for i in range(N):
                seed = 200 + i
                t0 = time.time()
                try:
                    code = fn(seed, ctx)
                    res, present = verify(code)
                    met = sum(res.values())
                    err = ""
                except Exception as e:
                    res, present, met, code = {}, 0, 0, ""
                    err = repr(e)[:150]
                open(os.path.join(WORK, f"{ctx}_{cond}_{i}.py"), "w", encoding="utf-8").write(code)
                rec = {"ctx": ctx, "cond": cond, "rep": i, "met": met, "present": present,
                       "detail": res, "secs": round(time.time()-t0, 1), "err": err}
                out.append(rec); done += 1
                print(f"[{done}/{total}] ctx={ctx:6d} {cond:9s} rep{i}  "
                      f"requisitos={met}/10 (presentes={present}) {rec['secs']}s {err[:30]}", flush=True)
    json.dump(out, open(os.path.join(BASE, "results_lh.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    # resumo
    print("\n==== RESUMO FASE 1 (requisitos corretos / 10) ====")
    print(f"{'janela(chars)':>14} | {'SEM Aliança':>12} | {'COM Aliança':>12} | {'Δ':>6}")
    for ctx in CTXS:
        b = [r["met"] for r in out if r["ctx"] == ctx and r["cond"] == "baseline"]
        a = [r["met"] for r in out if r["ctx"] == ctx and r["cond"] == "alianca"]
        mb = sum(b)/len(b) if b else 0; ma = sum(a)/len(a) if a else 0
        print(f"{ctx:>14} | {mb:>12.1f} | {ma:>12.1f} | {ma-mb:>+6.1f}")
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
