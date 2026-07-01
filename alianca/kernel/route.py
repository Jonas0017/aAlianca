#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route.py — hook UserPromptSubmit da Alianca (roteamento DETERMINISTICO).

Em vez de torcer para o LLM ler o router.md e decidir quais modulos carregar,
este hook casa a intencao do prompt do usuario contra o indice compilado
(alianca/router.index.json) e injeta no contexto exatamente quais modulos
carregar, na ordem de precedencia correta.

Contrato (Claude Code, UserPromptSubmit):
  stdin  -> JSON com campo "prompt" (entre outros).
  stdout -> JSON: {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                    "additionalContext": "<bloco de roteamento>"}}
  exit   -> sempre 0 (este hook injeta contexto; nunca bloqueia o turno).

Filosofia: nunca quebrar o turno do usuario. Qualquer falha (stdin vazio,
JSON invalido, indice ausente/corrompido) degrada para o "lembrete base".
"""

import io
import json
import os
import sys
import unicodedata

# ---------------------------------------------------------------------------
# stdout em utf-8 (Windows costuma vir em cp1252)
# ---------------------------------------------------------------------------
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Textos fixos
# ---------------------------------------------------------------------------
HEADER = "== Alianca — roteamento deste turno =="
LOOP = ("Loop: CHECAR -> CARREGAR -> AGIR -> VERIFICAR -> PERSISTIR. "
        "Fonte unica de memoria: alianca/memory/.")

# Bloco do MODO COORDENADOR (3o pilar: nao esgotar a janela desta sessao).
# Injetado so quando o prompt tem cara de EXECUCAO PESADA. Nudge CONDICIONAL:
# manda delegar o pesado/autocontido, mas deixa o trivial inline (senao
# delegar uma correcao de uma linha custaria mais que fazer).
COORD_BLOCK = (
    "== Modo coordenador ==\n"
    "Se esta execucao for autocontida (implementacao inteira, mudanca "
    "multi-arquivo, varredura, pesquisa, verificacao que roda coisas), "
    "DELEGUE a um subagente (Agent tool) e consuma so o resumo — descarrega "
    "a janela desta sessao. Se for ajuste trivial ou decisao, faca inline."
)

# Radicais de verbos que sinalizam execucao substancial. Casa por prefixo de
# token (implementar/implementacao, refatorar/refatoracao...). NAO inclui
# 'criar/cria' (generico demais: "cria uma tarefa" nao e execucao pesada).
EXECUTION_STEMS = (
    "implement", "constr", "desenvolv", "refator", "migr", "integr",
    "audit", "otimiz", "investig", "pesquis", "refaz", "corrig", "resolv",
    "program", "reescrev", "portar", "orquestr",
)

# stopwords PT para tokenizar o prompt. DEVE espelhar a STOPWORDS de
# compile.py: se um lado dropa uma palavra generica e o outro nao, o
# casamento fica assimetrico. Mantenha os dois conjuntos identicos.
STOPWORDS = {
    # artigos, preposicoes, conjuncoes, pronomes
    "de", "da", "do", "dos", "das", "ou", "e", "a", "o", "um", "uma", "em",
    "ao", "aos", "que", "com", "por", "pelo", "pela", "para", "os", "as",
    "no", "na", "nos", "nas", "se", "ja", "sobre", "pra", "essa", "esse",
    "esta", "este", "isso", "isto", "meu", "minha", "seu", "sua", "so",
    "uns", "umas", "vou", "aqui", "cada",
    # verbos/adverbios/interrogativos conversacionais genericos
    "foi", "foram", "como", "algo", "vai", "voce", "qual", "nao", "sao",
    "era", "ser", "tem", "ter", "quero", "preciso", "pode", "quer", "fazer",
    "agora", "entao", "tambem", "porque", "quando", "onde", "quem", "mais",
    "menos", "muito", "tudo", "nada", "alterar", "criar",
    # substantivos genericos de baixo sinal
    "problema", "produto", "coisa", "parte", "causa", "jeito", "forma",
    "projeto",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def strip_accents(text):
    """minusculo, sem acento."""
    text = text.lower()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def tokenize(text):
    """Tokeniza por nao-letra; descarta stopwords e tokens < 3 letras."""
    norm = strip_accents(text)
    out = []
    cur = []
    for ch in norm:
        if ch.isalpha():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return [t for t in out if len(t) >= 3 and t not in STOPWORDS]


def emit(additional_context):
    """Imprime o envelope JSON esperado pelo Claude Code e sai 0."""
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()
    sys.exit(0)


def base_reminder():
    """Lembrete base: so o loop + fonte de memoria."""
    return HEADER + "\n" + LOOP


def read_prompt():
    """
    Extrai o texto do prompt do usuario.
    1) stdin (JSON do hook, campo 'prompt').
    2) fallback: sys.argv juntos.
    3) None se nada disponivel.
    """
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""

    if raw and raw.strip():
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                p = data.get("prompt")
                if isinstance(p, str) and p.strip():
                    return p
            # JSON valido mas sem prompt utilizavel -> cai pro fallback
        except Exception:
            # stdin nao era JSON: trata o texto cru como prompt
            return raw

    if len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:]).strip()
        if arg:
            return arg

    return None


def load_index():
    """
    Carrega alianca/router.index.json resolvido via __file__:
    kernel/route.py -> sobe pra alianca/ -> router.index.json.
    Retorna dict ou None (nunca lanca).
    """
    try:
        kernel_dir = os.path.dirname(os.path.abspath(__file__))
        alianca_dir = os.path.dirname(kernel_dir)
        index_path = os.path.join(alianca_dir, "router.index.json")
        with open(index_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("modules"), dict):
            return data
    except Exception:
        pass
    return None


def short_hint(trigger):
    """Encurta o trigger para uma dica compacta entre parenteses."""
    if not trigger:
        return ""
    t = " ".join(str(trigger).split())
    # corta na primeira pontuacao forte, senao trunca
    for sep in ("(", " — ", " - ", ";", ":"):
        idx = t.find(sep)
        if idx > 0:
            t = t[:idx].strip()
            break
    if len(t) > 64:
        t = t[:61].rstrip() + "..."
    return t


def keyword_matches(keyword, tokens, norm_prompt):
    """
    Casa uma keyword. Keyword multi-palavra -> substring no prompt inteiro.
    Keyword simples -> igual a um token OU substring de um token.
    """
    kw = strip_accents(str(keyword)).strip()
    if len(kw) < 3:
        return False
    if " " in kw:
        return kw in norm_prompt
    for tok in tokens:
        # A keyword casa se for igual a um token OU for PREFIXO dele
        # (login -> "logins", teste -> "testes"): pega variacao morfologica
        # sem o falso-positivo do substring arbitrario ("usa" dentro de
        # "causa", "auth" dentro de "cauthela"). Prefixo, nao substring.
        if kw == tok or tok.startswith(kw):
            return True
    return False


def select_modules(index, tokens, norm_prompt):
    """Retorna lista ordenada de (nome, meta) dos modulos que casaram."""
    modules = index.get("modules", {})
    matched = []
    for name, meta in modules.items():
        if not isinstance(meta, dict):
            continue
        keywords = meta.get("keywords") or []
        for kw in keywords:
            if keyword_matches(kw, tokens, norm_prompt):
                matched.append((name, meta))
                break

    def sort_key(item):
        name, meta = item
        pr = meta.get("priority")
        if isinstance(pr, int):
            # modulos com precedencia primeiro (security=0 no topo)
            return (0, pr, name)
        # modulos de ciclo de vida: depois, alfabetico
        return (1, 0, name)

    matched.sort(key=sort_key)
    return matched


def is_execution_intent(tokens, matched):
    """
    True se o prompt tem cara de execucao pesada:
      (a) um verbo-radical de execucao (implementar, refatorar, migrar...), OU
      (b) 2+ modulos de CODIGO casaram (priority != null) — varias frentes
          tecnicas ao mesmo tempo sugere trabalho substancial.
    """
    for tok in tokens:
        for stem in EXECUTION_STEMS:
            if tok.startswith(stem):
                return True
    code_hits = sum(
        1 for _name, meta in matched
        if isinstance(meta.get("priority"), int)
    )
    return code_hits >= 2


def with_coordinator(block, tokens, matched):
    """Anexa o bloco do modo coordenador se a intencao for execucao pesada."""
    if is_execution_intent(tokens, matched):
        return block + "\n" + COORD_BLOCK
    return block


def build_block(matched):
    """Monta o bloco compacto de roteamento."""
    if not matched:
        return base_reminder()

    lines = [HEADER, "Carregue ANTES de agir (ordem de precedencia):"]
    for name, meta in matched:
        rel = meta.get("file") or ("instructions/" + name + ".md")
        path = "alianca/" + str(rel).lstrip("/")
        hint = short_hint(meta.get("trigger"))
        if hint:
            lines.append("  * {0} -> {1}  ({2})".format(name, path, hint))
        else:
            lines.append("  * {0} -> {1}".format(name, path))
    lines.append(LOOP)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    prompt = read_prompt()
    if not prompt:
        emit(base_reminder())

    tokens = tokenize(prompt)
    norm_prompt = strip_accents(prompt)

    index = load_index()
    if not index:
        # Sem indice ainda conseguimos avaliar o modo coordenador (nao
        # depende do roteamento de modulos).
        emit(with_coordinator(base_reminder(), tokens, []))

    matched = select_modules(index, tokens, norm_prompt)
    emit(with_coordinator(build_block(matched), tokens, matched))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # rede de seguranca final: nunca quebrar o turno
        try:
            emit(base_reminder())
        except Exception:
            sys.exit(0)
