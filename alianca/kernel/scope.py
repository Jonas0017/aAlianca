#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scope.py — resolucao do ESCOPO ATIVO (raiz vs microprojeto) da Alianca.

A Alianca deixou de ter UMA memoria plana: agora a memoria e FEDERADA por
microprojetos (bounded context). Cada turno opera num escopo — a raiz
(`alianca/memory/`) ou um microprojeto (`alianca/microprojects/<slug>/memory/`).
Este modulo e a fonte unica dessa resolucao, compartilhada por:

  - route.py    (UserPromptSubmit): injecao scope-aware (indice + linha de mem).
  - verify.py   (Stop):             cobra a memoria do escopo certo.
  - session_start.py (SessionStart): X9/monitor do escopo ativo.
  - selftest.py:                    testes de integridade do grafo.

PRINCIPIO: modulo PURO. Importar scope.py NAO tem efeito colateral (nao mexe em
stdout, nao roda nada) — por isso os hooks podem importa-lo sem risco. E
FAIL-OPEN TOTAL: qualquer erro na resolucao degrada para a RAIZ (None). O hook
route.py roda em TODO turno; um erro aqui jamais pode travar a sessao.

Sinal primario de escopo (precedencia em resolve_scope):
  1. pista `[mp:<slug>]` no prompt        (o mais explicito; o humano mandou)
  2. match do `cwd` em registry.codeDirs  (bonus; no Claude Code o cwd costuma
                                           ser a raiz e NAO discrimina)
  3. marcador `ACTIVE` em disco           (1 linha; vazio = raiz)
  4. raiz (None)                          (default e fail-open)

Invariante "uma so memoria" reinterpretada: uma por ESCOPO ATIVO (hierarquica,
nunca duas em paralelo). A raiz e o fallback COMPARTILHADO.
"""

import json
import os
import re

# Caminhos resolvidos via __file__ (nunca cwd):
#   alianca/kernel/scope.py -> alianca/kernel -> alianca -> alianca/microprojects
KERNEL_DIR = os.path.dirname(os.path.abspath(__file__))
ALIANCA_DIR = os.path.dirname(KERNEL_DIR)
MICROPROJECTS_DIR = os.path.join(ALIANCA_DIR, "microprojects")
REGISTRY_PATH = os.path.join(MICROPROJECTS_DIR, "registry.json")
ACTIVE_PATH = os.path.join(MICROPROJECTS_DIR, "ACTIVE")

# Pista explicita de escopo no prompt: [mp:<slug>].
MP_HINT_RE = re.compile(r"\[mp:([A-Za-z0-9._-]+)\]")

# Um fato hoisted deve deixar no local um STUB (ponteiro), nao o conteudo. O
# stub e reconhecido pelo marcador 'hoisted' + ser curto (ponteiro, nao dado).
_STUB_MARKER_RE = re.compile(r"hoisted", re.IGNORECASE)
_STUB_MAX_CHARS = 400


# ---------------------------------------------------------------------------
# Leitura do grafo (registry + ACTIVE). Tudo fail-open.
# ---------------------------------------------------------------------------
def load_registry():
    """registry.json como dict, ou {} se ausente/corrompido (nunca lanca)."""
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def read_active():
    """Primeira linha nao-vazia de ACTIVE (o slug ativo), ou None (=raiz)."""
    try:
        with open(ACTIVE_PATH, "r", encoding="utf-8") as fh:
            first = fh.readline().strip()
        return first or None
    except Exception:
        return None


def _is_registered(projects, slug):
    """True se o slug e um microprojeto conhecido do registry."""
    return isinstance(projects, dict) and isinstance(projects.get(slug), dict)


def _match_cwd(projects, cwd):
    """Devolve o slug cujo codeDirs contem (ou e prefixo de) o cwd, ou None."""
    try:
        cnorm = os.path.normcase(os.path.abspath(cwd))
    except Exception:
        return None
    for slug, meta in projects.items():
        if not isinstance(meta, dict):
            continue
        for d in meta.get("codeDirs") or []:
            try:
                dn = os.path.normcase(os.path.abspath(d))
            except Exception:
                continue
            if cnorm == dn or cnorm.startswith(dn.rstrip("\\/") + os.sep):
                return slug
    return None


def resolve_scope(cwd, prompt, registry=None):
    """
    Resolve o escopo ATIVO: devolve o slug do microprojeto ou None (=raiz).

    Precedencia: pista [mp:x] no prompt > match cwd em registry.codeDirs >
    marcador ACTIVE > raiz. So devolve um slug REGISTRADO (evita escopo
    fantasma por typo). FAIL-OPEN: qualquer erro -> None (raiz).
    """
    try:
        projects = registry if isinstance(registry, dict) else load_registry()
        if not isinstance(projects, dict) or not projects:
            return None
        # 1) pista explicita no prompt (o humano mandou)
        if prompt:
            m = MP_HINT_RE.search(prompt)
            if m and _is_registered(projects, m.group(1)):
                return m.group(1)
        # 2) match por cwd nos codeDirs (bonus)
        if cwd:
            slug = _match_cwd(projects, cwd)
            if slug:
                return slug
        # 3) marcador ACTIVE em disco
        active = read_active()
        if active and _is_registered(projects, active):
            return active
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Caminhos de memoria por escopo
# ---------------------------------------------------------------------------
def memory_dir_rel(scope):
    """Pasta de memoria do escopo, RELATIVA a alianca/ (sem barra final)."""
    if scope:
        return "microprojects/{0}/memory".format(scope)
    return "memory"


def memory_active_path(scope, base_dir=None):
    """Caminho ABSOLUTO do active-context.md do escopo (via __file__)."""
    base = base_dir or ALIANCA_DIR
    rel = memory_dir_rel(scope)
    return os.path.join(base, *rel.split("/"), "active-context.md")


# ---------------------------------------------------------------------------
# Merge de indices (raiz <- local): o local SOBREPOE por nome; so-raiz e o
# fallback. Funcao PURA (o route.py a chama; o selftest a testa direto).
# ---------------------------------------------------------------------------
def merge_indices(root, local):
    """
    Sobrepoe o indice LOCAL do microprojeto sobre o da RAIZ, por nome de
    modulo: modulo local substitui o homonimo da raiz; modulo so-raiz continua
    visivel (fallback compartilhado). Robusto a None/tipos errados.
    """
    if not isinstance(root, dict):
        return local if isinstance(local, dict) else None
    if not isinstance(local, dict):
        return root
    merged = dict(root)
    modules = dict(root.get("modules") or {})
    for name, meta in (local.get("modules") or {}).items():
        modules[name] = meta  # local sobrepoe
    merged["modules"] = modules
    return merged


# ---------------------------------------------------------------------------
# Integridade do grafo (usada pelo selftest e disponivel p/ health-check/x9)
# ---------------------------------------------------------------------------
def _is_stub_file(path):
    """
    True se o arquivo e um STUB de hoisting (ponteiro), nao conteudo real.
    Regra: marcado com 'hoisted' E curto. Ilegivel -> True (nao acusa dup).
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except Exception:
        return True
    stripped = text.strip()
    return bool(_STUB_MARKER_RE.search(stripped)) and len(stripped) <= _STUB_MAX_CHARS


def validate_graph(base_dir=None):
    """
    Valida a integridade do grafo de microprojetos. Devolve uma LISTA de
    problemas (strings); vazia = grafo integro. NUNCA lanca.

    Constata:
      - cada microprojeto do registry tem pasta memory/ (senao: falha);
      - cada aresta de hoisting aponta p/ um destino raiz EXISTENTE (senao:
        aresta quebrada) e deixa no local um STUB, nunca conteudo (anti-
        duplicacao: a invariante "uma so memoria por escopo");
      - ACTIVE nao aponta p/ microprojeto nao registrado (ACTIVE orfao).
    """
    base = base_dir or ALIANCA_DIR
    problems = []
    reg_path = os.path.join(base, "microprojects", "registry.json")
    active_path = os.path.join(base, "microprojects", "ACTIVE")

    registry = {}
    if os.path.isfile(reg_path):
        try:
            with open(reg_path, "r", encoding="utf-8") as fh:
                registry = json.load(fh)
            if not isinstance(registry, dict):
                problems.append("registry.json nao e um objeto JSON")
                registry = {}
        except Exception as e:
            problems.append("registry.json ilegivel: {0}".format(type(e).__name__))
            registry = {}

    for slug, meta in registry.items():
        if not isinstance(meta, dict):
            problems.append("registro '{0}' nao e um objeto".format(slug))
            continue
        mem = os.path.join(base, "microprojects", slug, "memory")
        if not os.path.isdir(mem):
            problems.append("microprojeto '{0}' sem pasta memory/".format(slug))
        for h in meta.get("hoisted") or []:
            if not isinstance(h, dict):
                problems.append("aresta de hoisting invalida em '{0}'".format(slug))
                continue
            to = h.get("to")
            if not to or not os.path.isfile(os.path.join(base, *str(to).split("/"))):
                problems.append(
                    "hoisting '{0}': destino raiz ausente ({1})".format(slug, to))
            stub = h.get("stub")
            if stub:
                sp = os.path.join(base, *str(stub).split("/"))
                if os.path.isfile(sp) and not _is_stub_file(sp):
                    problems.append(
                        "hoisting '{0}': local nao e stub, ha conteudo "
                        "duplicado ({1})".format(slug, stub))

    active = None
    if os.path.isfile(active_path):
        try:
            with open(active_path, "r", encoding="utf-8") as fh:
                active = fh.readline().strip() or None
        except Exception:
            active = None
    if active and active not in registry:
        problems.append(
            "ACTIVE aponta p/ microprojeto nao registrado (orfao): {0}".format(active))

    return problems
