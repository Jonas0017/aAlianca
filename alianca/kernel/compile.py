#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile.py — o "compilador" da Aliança.

Lê todos os módulos em alianca/instructions/*.md, parseia o frontmatter (à mão,
sem PyYAML) e produz o índice compilado alianca/router.index.json (schema fixo,
sort_keys, ensure_ascii=False) que o route.py consome.

Rodar duas vezes produz exatamente o mesmo resultado (idempotente).
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes de contrato
# ---------------------------------------------------------------------------

VERSION = "3.0"
GENERATED_FROM = "alianca/instructions/*.md"

# Ordem de precedência dos módulos de CÓDIGO. O índice nesta lista é a
# "priority" do módulo. Módulos fora desta lista (ciclo de vida / bootstrap)
# recebem priority = null.
PRECEDENCE = [
    "security",
    "bug-prevention",
    "testing",
    "architecture",
    "refactor",
    "interface",
    "code-quality",
]

# Stopwords PT descartadas ao derivar keywords do trigger. Inclui palavras
# CONVERSACIONAIS genericas (foi, como, algo, qual, problema, produto...) que,
# vindas de triggers em prosa, viram roteadores fracos e casam prompts
# benignos. Mantida em sincronia com a STOPWORDS de route.py.
# Para sinal de alta precisao num modulo especifico, prefira 'keywords:'
# curado no frontmatter (o compilador respeita e sobrepoe a derivacao).
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

# Caminhos (relativos à raiz alianca/, resolvidos a partir deste arquivo:
#   alianca/kernel/compile.py -> alianca/ é o parent do parent).
ALIANCA_DIR = Path(__file__).resolve().parent.parent
INSTRUCTIONS_DIR = ALIANCA_DIR / "instructions"
INDEX_PATH = ALIANCA_DIR / "router.index.json"


# ---------------------------------------------------------------------------
# Parsing de frontmatter (à mão, sem PyYAML)
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """
    Extrai o bloco de frontmatter delimitado por '---' no topo do arquivo.

    Retorna um dict {chave: valor} (valores como strings), ou None se o
    arquivo não tiver um frontmatter válido.
    """
    lines = text.splitlines()
    # Pular linhas em branco / BOM no topo.
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx >= len(lines) or lines[idx].strip() != "---":
        return None

    fm = {}
    idx += 1
    closed = False
    current_key = None
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == "---":
            closed = True
            break
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            current_key = m.group(1).strip()
            fm[current_key] = m.group(2).strip()
        elif current_key is not None and line.strip() != "":
            # Continuação de um valor multi-linha: anexa.
            fm[current_key] = (fm[current_key] + " " + line.strip()).strip()
        idx += 1

    if not closed:
        return None
    return fm


# ---------------------------------------------------------------------------
# Derivação de keywords
# ---------------------------------------------------------------------------

def strip_accents(s):
    """Remove acentos (NFKD + descarte de marcas combinantes)."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def derive_keywords(trigger):
    """
    Deriva keywords do texto do trigger:
      - minúsculas
      - sem acento
      - tokenizar por não-letra
      - descartar stopwords PT e tokens com < 3 letras
      - deduplicar e ordenar
    """
    normalized = strip_accents(trigger.lower())
    tokens = re.split(r"[^a-z]+", normalized)
    kept = set()
    for tok in tokens:
        if len(tok) < 3:
            continue
        if tok in STOPWORDS:
            continue
        kept.add(tok)
    return sorted(kept)


def parse_explicit_keywords(raw):
    """
    Se o frontmatter tiver 'keywords:' explícito, usa-o. Aceita formatos:
      keywords: a, b, c
      keywords: [a, b, c]
    Normaliza (minúsculas, sem acento, dedup, ordena).
    """
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    parts = re.split(r"[,;]", raw)
    kept = set()
    for p in parts:
        p = strip_accents(p.strip().strip("'\"").lower())
        if p:
            kept.add(p)
    return sorted(kept)


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

def compute_priority(name):
    """Índice na lista de precedência, ou None (módulos de ciclo de vida)."""
    if name in PRECEDENCE:
        return PRECEDENCE.index(name)
    return None


# ---------------------------------------------------------------------------
# I/O determinístico (LF, utf-8, sem reescrever se idêntico)
# ---------------------------------------------------------------------------

def write_text(path, content):
    path = Path(path)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            return
    path.write_text(content, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not INSTRUCTIONS_DIR.is_dir():
        print(f"ERRO: nao encontrei {INSTRUCTIONS_DIR}", file=sys.stderr)
        return 1

    md_files = sorted(INSTRUCTIONS_DIR.glob("*.md"), key=lambda p: p.name)

    modules = {}
    skipped = []

    for path in md_files:
        name = path.stem
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        if fm is None or "trigger" not in fm or not fm["trigger"].strip():
            skipped.append(name)
            continue

        trigger = fm["trigger"].strip()

        if "keywords" in fm and fm["keywords"].strip():
            keywords = parse_explicit_keywords(fm["keywords"])
        else:
            keywords = derive_keywords(trigger)

        load_when = fm.get("load-when", "").strip()

        modules[name] = {
            "file": f"instructions/{name}.md",
            "trigger": trigger,
            "keywords": keywords,
            "loadWhen": load_when,
            "priority": compute_priority(name),
        }

    index = {
        "version": VERSION,
        "generatedFrom": GENERATED_FROM,
        "precedence": PRECEDENCE,
        "modules": modules,
    }

    index_text = json.dumps(
        index, sort_keys=True, indent=2, ensure_ascii=False
    ) + "\n"
    write_text(INDEX_PATH, index_text)

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------
    print(f"Alianca compile — {INDEX_PATH.name} gerado.")
    print(f"  Modulos indexados: {len(modules)}")
    if skipped:
        print(f"  AVISO: {len(skipped)} arquivo(s) sem frontmatter valido "
              f"(pulados): {', '.join(skipped)}")
    else:
        print("  Sem avisos: todos os modulos tinham frontmatter valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
