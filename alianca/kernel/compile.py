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

# Versao do FORMATO do indice (schema do router.index.json), nao do produto.
# A versao do produto (Alianca) e lida do alianca/router.md (alianca-version)
# e emitida como "aliancaVersion".
INDEX_FORMAT_VERSION = "3.0"
GENERATED_FROM = "alianca/instructions/*.md"

# Chaves reconhecidas de frontmatter. Uma linha "palavra:" que NAO esteja
# nesta lista e tratada como CONTINUACAO do valor anterior (ex.: um trigger
# multi-linha contendo "Nota: ..."), nao como chave nova.
KNOWN_KEYS = {"trigger", "keywords", "load-when", "applies-to", "priority", "pulls"}

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
# Memoria FEDERADA: cada microprojeto pode ter instructions/ locais, compiladas
# para um router.index.json local (o merge no route.py sobrepoe a raiz por nome).
MICROPROJECTS_DIR = ALIANCA_DIR / "microprojects"


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
        # Chave nova SO se a linha nao esta indentada (o ^ do regex ja exige
        # comeco em coluna 0) E a chave e CONHECIDA. Senao, uma continuacao
        # de valor multi-linha que comece com "Palavra:" (ex.: "Nota: ...")
        # viraria uma chave espuria e truncaria o valor anterior.
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m and m.group(1).strip().lower() in KNOWN_KEYS:
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
# Versão do produto (lida do alianca/router.md)
# ---------------------------------------------------------------------------

ROUTER_MD_PATH = ALIANCA_DIR / "router.md"


def read_alianca_version():
    """
    Versão do produto declarada no alianca/router.md, na linha
    'alianca-version: X.Y' (dentro de um bloco de código). Parse tolerante:
    qualquer falha (arquivo ausente, linha ausente) devolve None e o campo
    é simplesmente omitido do índice.
    """
    try:
        text = ROUTER_MD_PATH.read_text(encoding="utf-8")
        m = re.search(r"^\s*alianca-version\s*:\s*([0-9][\w.\-]*)\s*$",
                      text, re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass
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

def build_modules(instructions_dir, file_prefix):
    """
    Compila todos os *.md de 'instructions_dir' em {nome: entry}, com o campo
    'file' prefixado por 'file_prefix' (RELATIVO a alianca/). Devolve
    (modules, skipped). Mesma logica p/ a raiz e p/ cada microprojeto — a unica
    diferenca e o prefixo do caminho.
    """
    modules = {}
    skipped = []
    md_files = sorted(instructions_dir.glob("*.md"), key=lambda p: p.name)
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
            keywords_derived = False
        else:
            keywords = derive_keywords(trigger)
            keywords_derived = True

        load_when = fm.get("load-when", "").strip()

        # Grafo operacional (opcional, adaptativo): 'pulls' = arestas de
        # contexto necessario nao-dito (ex.: security pulls testing). Modulo
        # sem 'pulls' nao entra no grafo. Nomes de modulo preservados (com
        # hifen), na ordem declarada.
        pulls = [p.strip() for p in re.split(r"[,;]", fm.get("pulls", "")) if p.strip()]

        entry = {
            "file": f"{file_prefix}{name}.md",
            "trigger": trigger,
            "keywords": keywords,
            "loadWhen": load_when,
            "priority": compute_priority(name),
        }
        if keywords_derived:
            # Keywords DERIVADAS do trigger sao ruidosas por natureza (prosa
            # vira roteador). O route.py exige forca minima 2 para modulos
            # marcados assim; keywords curadas mantem forca 1.
            entry["keywordsDerived"] = True
        if pulls:
            entry["pulls"] = pulls
        modules[name] = entry
    return modules, skipped


def _compile_microprojects():
    """
    Compila as instructions/ locais de cada microprojeto para um
    router.index.json local (idempotente). Devolve a lista de slugs compilados.
    Ausencia de microprojects/ ou de instructions/ locais e o caso comum
    (silencioso). Robusto: um microprojeto quebrado nao derruba o compile.
    """
    compiled = []
    if not MICROPROJECTS_DIR.is_dir():
        return compiled
    for sub in sorted(MICROPROJECTS_DIR.iterdir()):
        if not sub.is_dir():
            continue
        local_instr = sub / "instructions"
        if not local_instr.is_dir():
            continue
        prefix = f"microprojects/{sub.name}/instructions/"
        local_mods, _sk = build_modules(local_instr, prefix)
        local_index = {
            "indexFormatVersion": INDEX_FORMAT_VERSION,
            "generatedFrom": f"microprojects/{sub.name}/instructions/*.md",
            "precedence": PRECEDENCE,
            "modules": local_mods,
        }
        local_text = json.dumps(
            local_index, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        write_text(sub / "router.index.json", local_text)
        compiled.append(sub.name)
    return compiled


def main():
    if not INSTRUCTIONS_DIR.is_dir():
        print(f"ERRO: nao encontrei {INSTRUCTIONS_DIR}", file=sys.stderr)
        return 1

    modules, skipped = build_modules(INSTRUCTIONS_DIR, "instructions/")

    index = {
        "indexFormatVersion": INDEX_FORMAT_VERSION,
        "generatedFrom": GENERATED_FROM,
        "precedence": PRECEDENCE,
        "modules": modules,
    }
    alianca_version = read_alianca_version()
    if alianca_version:
        index["aliancaVersion"] = alianca_version

    index_text = json.dumps(
        index, sort_keys=True, indent=2, ensure_ascii=False
    ) + "\n"
    write_text(INDEX_PATH, index_text)

    compiled_mps = _compile_microprojects()

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------
    print(f"Alianca compile — {INDEX_PATH.name} gerado.")
    print(f"  Modulos indexados: {len(modules)}")
    if compiled_mps:
        print(f"  Microprojetos compilados: {', '.join(compiled_mps)}")
    if skipped:
        print(f"  AVISO: {len(skipped)} arquivo(s) sem frontmatter valido "
              f"(pulados): {', '.join(skipped)}")
    else:
        print("  Sem avisos: todos os modulos tinham frontmatter valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
