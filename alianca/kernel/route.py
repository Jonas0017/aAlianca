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

# klog: log do kernel (dmesg). Best-effort; se faltar, no-op (nunca quebra o hook).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from klog import klog
except Exception:
    def klog(event, detail):
        pass

# scope: resolucao do ESCOPO ATIVO (raiz vs microprojeto) — memoria federada.
# Modulo PURO (sem efeito colateral de import). Se faltar/quebrar, DEGRADA para
# a raiz sempre (fail-open): o roteamento nunca pode travar a sessao.
try:
    import scope as _scope
    resolve_scope = _scope.resolve_scope
    merge_indices = _scope.merge_indices
    _memory_dir_rel = _scope.memory_dir_rel
    _MICROPROJECTS_DIR = _scope.MICROPROJECTS_DIR
    _ALIANCA_DIR = _scope.ALIANCA_DIR
except Exception:
    def resolve_scope(cwd, prompt, registry=None):
        return None

    def merge_indices(root, local):
        return root

    def _memory_dir_rel(scope):
        return "memory"

    _ALIANCA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _MICROPROJECTS_DIR = os.path.join(_ALIANCA_DIR, "microprojects")

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


def _mem_display(scope):
    """Pasta de memoria do escopo, formatada 'alianca/.../' para exibicao."""
    try:
        return "alianca/" + _memory_dir_rel(scope) + "/"
    except Exception:
        return "alianca/memory/"


def loop_text(scope=None):
    """
    Linha do LOOP + fonte de memoria DO ESCOPO ATIVO (nao mais fixa na raiz).
    A raiz continua sendo o fallback COMPARTILHADO.
    """
    return ("Loop: CHECAR -> CARREGAR -> AGIR -> VERIFICAR -> PERSISTIR. "
            "Fonte de memoria deste escopo: {0}; fallback compartilhado: "
            "alianca/memory/.\n"
            "Papel: voce e o GERENTE — delegue TODA execucao a um subagente "
            "(Agent tool) e consuma so o resumo; inline apenas roteamento, "
            "decisao e dialogo (o pai nao poe a mao no codigo).").format(
                _mem_display(scope))

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


def base_reminder(scope=None):
    """Lembrete base: so o loop + fonte de memoria (do escopo ativo)."""
    return HEADER + "\n" + loop_text(scope)


def read_payload():
    """
    Le o stdin do hook UMA vez e devolve (prompt, cwd).

    Precisamos dos DOIS: o prompt (roteamento + pista [mp:x]) e o cwd (sinal
    bonus de escopo). Le o stdin uma unica vez (consumo unico) e cai para os
    fallbacks:
      - prompt: stdin JSON 'prompt' -> stdin cru -> sys.argv -> None;
      - cwd:    stdin JSON 'cwd'    -> None.
    Nunca lanca.
    """
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""

    prompt = None
    cwd = None
    if raw and raw.strip():
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                p = data.get("prompt")
                if isinstance(p, str) and p.strip():
                    prompt = p
                c = data.get("cwd")
                if isinstance(c, str) and c.strip():
                    cwd = c
            # JSON valido mas sem prompt -> cai pro fallback de argv
        except Exception:
            # stdin nao era JSON: trata o texto cru como prompt
            prompt = raw

    if prompt is None and len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:]).strip()
        if arg:
            prompt = arg

    return prompt, cwd


def _read_index_file(path):
    """Le um router.index.json valido de 'path', ou None (nunca lanca)."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("modules"), dict):
            return data
    except Exception:
        pass
    return None


def load_index(scope=None):
    """
    Carrega o indice da RAIZ (alianca/router.index.json). Se o escopo for um
    microprojeto com router.index.json LOCAL, sobrepoe por nome (local
    substitui; so-raiz continua como fallback). Sem scope -> raiz pura
    (back-compat exato). Retorna dict ou None (nunca lanca).
    """
    root = _read_index_file(os.path.join(_ALIANCA_DIR, "router.index.json"))
    if scope:
        try:
            local = _read_index_file(
                os.path.join(_MICROPROJECTS_DIR, scope, "router.index.json"))
            if local:
                merged = merge_indices(root, local)
                if isinstance(merged, dict) and isinstance(
                        merged.get("modules"), dict):
                    return merged
        except Exception:
            pass
    return root


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
    """
    Retorna [(nome, meta, forca)] dos modulos que casaram, ordenados por
    RELEVANCIA. 'forca' = quantas keywords distintas do modulo casaram — um
    match especifico (tasks casa 'tarefa'+'nova') vence um match generico
    (architecture casa so 'nova'), sem precisar curar keyword.

    CALIBRACAO ANTI-RUIDO: modulo cujas keywords foram DERIVADAS do trigger
    pelo compile.py (meta["keywordsDerived"] == true) exige forca minima 2 —
    keywords derivadas de prosa sao genericas ("revisao", "mas", "multi") e
    uma unica coincidencia nao e sinal. Keywords CURADAS mantem forca 1.

    Ordem: security sempre primeiro se casou (invariante de seguranca: nunca
    sacrificada); depois por forca desc; empate -> codigo antes de ciclo de
    vida, depois precedencia, depois nome.
    """
    modules = index.get("modules", {})
    scored = []
    for name, meta in modules.items():
        if not isinstance(meta, dict):
            continue
        keywords = meta.get("keywords") or []
        strength = sum(
            1 for kw in keywords if keyword_matches(kw, tokens, norm_prompt)
        )
        min_strength = 2 if meta.get("keywordsDerived") else 1
        if strength >= min_strength:
            scored.append((name, meta, strength))

    def sort_key(item):
        name, meta, strength = item
        pr = meta.get("priority")
        is_code = isinstance(pr, int)
        return (
            0 if name == "security" else 1,   # security colado no topo
            -strength,                          # match mais forte primeiro
            0 if is_code else 1,                # codigo antes de ciclo de vida
            pr if is_code else 999,             # precedencia entre os de codigo
            name,
        )

    scored.sort(key=sort_key)
    return scored


def is_execution_intent(tokens, matched):
    """
    True se o prompt tem cara de execucao pesada:
      (a) um verbo-radical de execucao (implementar, refatorar, migrar...), OU
      (b) 2+ modulos de CODIGO casaram (priority != null) — varias frentes
          tecnicas ao mesmo tempo sugere trabalho substancial.

    Le o meta em item[1]: funciona tanto com 2-tuplas (name, meta) quanto com
    3-tuplas (name, meta, pulled_by) — a saida de expand_pulls.
    """
    for tok in tokens:
        for stem in EXECUTION_STEMS:
            if tok.startswith(stem):
                return True
    code_hits = sum(
        1 for item in matched
        if isinstance(item[1].get("priority"), int)
    )
    return code_hits >= 2


def with_coordinator(block, tokens, matched):
    """Anexa o bloco do modo coordenador se a intencao for execucao pesada."""
    if is_execution_intent(tokens, matched):
        return block + "\n" + COORD_BLOCK
    return block


def cap_modules(scored, limit=3):
    """
    Teto do scheduler (nao despejar contexto): fica com os 'limit' modulos
    mais relevantes (scored ja vem ordenado por relevancia). Devolve a lista
    no formato (nome, meta) que o resto do modulo espera.
    """
    return [(name, meta) for (name, meta, _strength) in scored[:limit]]


def expand_pulls(selected, index, ceiling=5):
    """
    TRAVERSAL DE GRAFO (1 salto, adaptativo, limitado).

    'selected' = saida de cap_modules = [(name, meta)] (os diretos, por keyword).
    Retorna [(name, meta, pulled_by)]: pulled_by=None para diretos; pulled_by=
    <nome do puxador> para os trazidos pelo grafo via meta["pulls"].

    Regras:
      - 1 SALTO SO: expande apenas os pulls dos diretos, nunca pulls-de-pulls
        (seguranca a ciclo por construcao).
      - Dedup: pula alvo ja presente (direto ou ja puxado por outro).
      - Aresta quebrada: alvo ausente de index["modules"] e ignorado em silencio
        (quem reporta e o health-check/x9).
      - Ordem: todos os diretos primeiro (na ordem de relevancia recebida);
        depois os puxados por precedencia (codigo/priority asc; ciclo de vida
        por ultimo; empate por nome). Corta o excedente para len <= ceiling
        (os diretos, no maximo 3, sempre cabem).
      - ADAPTATIVO: se nenhum direto tem 'pulls', devolve exatamente os diretos
        convertidos p/ 3-tupla (pulled_by=None) — zero inflacao do caso simples.

    Blindagem: qualquer erro cai para os diretos sem pulls.
    """
    directs = [(name, meta, None) for (name, meta) in selected]
    try:
        modules = index.get("modules", {}) if isinstance(index, dict) else {}
        if not isinstance(modules, dict):
            return directs

        seen = set(name for (name, _meta) in selected)
        pulled = []  # (name, meta, pulled_by)
        for name, meta in selected:
            if not isinstance(meta, dict):
                continue
            targets = meta.get("pulls")
            if not isinstance(targets, (list, tuple)):
                continue
            for tgt in targets:
                if not isinstance(tgt, str) or tgt in seen:
                    continue
                tmeta = modules.get(tgt)
                if not isinstance(tmeta, dict):
                    # aresta quebrada -> ignora em silencio
                    continue
                seen.add(tgt)
                pulled.append((tgt, tmeta, name))

        if not pulled:
            return directs

        def pull_key(item):
            name, meta, _by = item
            pr = meta.get("priority")
            is_code = isinstance(pr, int)
            return (
                0 if is_code else 1,       # codigo antes de ciclo de vida
                pr if is_code else 999,    # priority asc entre os de codigo
                name,
            )

        pulled.sort(key=pull_key)
        expanded = directs + pulled
        if len(expanded) > ceiling:
            expanded = expanded[:ceiling]
        return expanded
    except Exception:
        # blindagem: em duvida, diretos sem pulls (nunca quebra o turno)
        return directs


def scope_label(scope):
    """Rotulo humano do escopo para o cabecalho/klog."""
    return scope if scope else "raiz"


def resolve_instruction_path(name, meta, scope):
    """
    Resolve o caminho da instrucao LOCAL-PRIMEIRO. Se o escopo tem o arquivo
    local (indice local ja traz o path 'microprojects/...', ou existe uma
    sobreposicao fisica em microprojects/<slug>/<rel>), aponta pra ele; senao,
    cai para o caminho da raiz (fallback compartilhado). Nunca lanca.
    """
    rel = str(meta.get("file") or ("instructions/" + name + ".md")).lstrip("/")
    if scope:
        try:
            if rel.startswith("microprojects/"):
                return "alianca/" + rel
            local_rel = "microprojects/{0}/{1}".format(scope, rel)
            local_abs = os.path.join(_ALIANCA_DIR, *local_rel.split("/"))
            if os.path.isfile(local_abs):
                return "alianca/" + local_rel
        except Exception:
            pass
    return "alianca/" + rel


def build_block(expanded, scope=None):
    """
    Monta o bloco compacto de roteamento.

    Aceita itens (name, meta, pulled_by) de expand_pulls (ou 2-tuplas legadas).
    Quando pulled_by, anexa a dica "(puxado por <pulled_by>)" na linha.
    Emite o cabecalho 'Escopo ativo: <slug|raiz>' e resolve cada caminho de
    instrucao local-primeiro.
    """
    if not expanded:
        return base_reminder(scope)

    lines = [HEADER,
             "Escopo ativo: {0}".format(scope_label(scope)),
             "Carregue ANTES de agir (ordem de precedencia):"]
    for item in expanded:
        name = item[0]
        meta = item[1]
        pulled_by = item[2] if len(item) > 2 else None
        path = resolve_instruction_path(name, meta, scope)
        hint = short_hint(meta.get("trigger"))
        prov = "  (puxado por {0})".format(pulled_by) if pulled_by else ""
        if hint:
            lines.append(
                "  * {0} -> {1}  ({2}){3}".format(name, path, hint, prov)
            )
        else:
            lines.append("  * {0} -> {1}{2}".format(name, path, prov))
    lines.append(loop_text(scope))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    prompt, cwd = read_payload()

    # Escopo ATIVO deste turno (fail-open p/ raiz). Resolve ANTES do early-exit
    # para que ate o lembrete base traga a memoria do escopo certo.
    try:
        scope = resolve_scope(cwd, prompt)
    except Exception:
        scope = None

    if not prompt:
        emit(base_reminder(scope))

    tokens = tokenize(prompt)
    norm_prompt = strip_accents(prompt)

    index = load_index(scope)
    if not index:
        # Sem indice ainda conseguimos avaliar o modo coordenador (nao
        # depende do roteamento de modulos).
        emit(with_coordinator(base_reminder(scope), tokens, []))

    matched = cap_modules(select_modules(index, tokens, norm_prompt))
    expanded = expand_pulls(matched, index)
    directs = [n for (n, _m, by) in expanded if by is None]
    pulls = [n for (n, _m, by) in expanded if by is not None]
    klog(
        "ROUTE",
        "scope={} mods=[{}] pulls=[{}]".format(
            scope_label(scope), ", ".join(directs), ", ".join(pulls)),
    )
    # O gate do coordenador avalia a intencao sobre os modulos DIRETOS
    # (matched), nao sobre os puxados pelo grafo: pulls de codigo (ex.:
    # security -> testing, bug-prevention) nao devem inflar o heuristico
    # "2+ modulos de codigo" e disparar o coordenador espuriamente. O grafo
    # (expanded) segue intacto no build_block.
    emit(with_coordinator(build_block(expanded, scope), tokens, matched))


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
