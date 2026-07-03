# -*- coding: utf-8 -*-
"""Verifica o projeto de 3 arquivos gerado. Uso: python verify_proj.py <dir>
Imprime JSON com o que importou e se a integração (total==87.75) passou."""
import sys, json, importlib
d = sys.argv[1]
sys.path.insert(0, d)
out = {"catalogo": False, "desconto": False, "pedido": False,
       "total_ok": False, "total_val": None, "err": ""}
for m in ("catalogo", "desconto", "pedido"):
    sys.modules.pop(m, None)
try:
    import catalogo
    out["catalogo"] = callable(getattr(catalogo, "buscar_valor", None))
except Exception as e:
    out["err"] += "cat:" + repr(e)[:70]
try:
    import desconto
    out["desconto"] = callable(getattr(desconto, "somar_itens", None)) and \
                       callable(getattr(desconto, "promo", None))
except Exception as e:
    out["err"] += "|desc:" + repr(e)[:70]
try:
    import pedido
    out["pedido"] = callable(getattr(pedido, "finalizar", None))
    v = pedido.finalizar(["AX9", "KT3", "MZ7"], "ZK88")
    out["total_val"] = v
    out["total_ok"] = abs(float(v) - 85.8) < 1e-6
except Exception as e:
    out["err"] += "|ped:" + repr(e)[:70]
print(json.dumps(out))
