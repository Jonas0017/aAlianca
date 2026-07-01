#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alianca / kernel / gate.py

PreToolUse hook: FECHA o caminho barato-errado.
Bloqueia deterministicamente uma escrita (Write/Edit/MultiEdit) que
introduz um segredo/credencial hardcoded no codigo.

Materializa a invariante do START-HERE §5: "nunca commitar credencial".

Contrato (Claude Code hooks):
  - Recebe JSON no stdin com: tool_name, tool_input, ...
  - Para BLOQUEAR: exit 2 + mensagem no stderr (meio mais confiavel).
  - Para PERMITIR: exit 0 sem output.

Principios:
  - Fail-open: qualquer erro de parsing/execucao -> exit 0 (nunca travar
    todas as ferramentas por um bug do proprio portao).
  - Determinismo: mesmas entradas -> mesma decisao.
  - Baixo falso-positivo: regex conservador + lista de placeholders.
"""

import sys
import io
import re

ALLOWED_TOOLS = ("Write", "Edit", "MultiEdit")

# Extensoes de arquivo que sao, por convencao, exemplos/placeholders.
EXAMPLE_SUFFIXES = (".example", ".sample", ".env.example", ".env.sample", ".dist", ".template")

# Referencias a variavel de ambiente: nunca sao segredo hardcoded.
ENV_REF_TOKENS = (
    "os.environ", "process.env", "getenv", "env[", "env.get",
)

# Placeholder estrutural COMPLETO: <...> ou ${...}.
PLACEHOLDER_STRUCT_RE = re.compile(r"<[^>]{0,60}>|\$\{[^}]+\}")

# Palavras-placeholder. So contam se DOMINAREM o valor (ver
# _is_placeholder_value) — nunca por mera substring, senao "todoSecret12345"
# ou "xxxxREAL9999" escapariam do portao.
PLACEHOLDER_WORD_RE = re.compile(
    r"your[_-]?|yourkey|change[_-]?me|changeit|x{3,}|example|dummy|"
    r"placeholder|redacted|todo|fixme|here",
    re.IGNORECASE,
)

# --- Deteccao de segredo (conservadora) ---------------------------------

RE_AWS_KEY = re.compile(r"AKIA[0-9A-Z]{16}")

RE_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |)PRIVATE KEY-----"
)

# api_key / secret / token / password / client_secret = "valor com >=8 chars"
RE_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|passwd|password|client[_-]?secret)\b"
    r"\s*[:=]\s*"
    r"(['\"])([^'\"]{8,})\2"
)

# Tokens de provedores comuns (formato fixo, alto sinal).
RE_SLACK = re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")
RE_GITHUB = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")
RE_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{20,}")


def _is_placeholder_value(value):
    """
    True se o valor for claramente placeholder/exemplo.

    NAO usa substring: uma palavra-placeholder so "vence" se dominar o valor
    (o residuo alfanumerico, fora ela, for curto). Assim um segredo real de
    alta entropia colado a 'todo'/'xxxx'/'<' NAO escapa do portao.
    """
    v = value.strip()
    if not v:
        return True

    low = v.lower()
    for tok in ENV_REF_TOKENS:
        if tok in low:
            return True

    # Placeholder estrutural completo (<...>, ${...}) em qualquer posicao,
    # ou valor que comeca com '<' / '${'.
    if v.startswith("<") or v.startswith("${") or PLACEHOLDER_STRUCT_RE.search(v):
        return True

    # Palavra-placeholder: so vale se o que sobra (fora ela) for <= 6 chars.
    if PLACEHOLDER_WORD_RE.search(v):
        residue = re.sub(r"[^A-Za-z0-9]", "", PLACEHOLDER_WORD_RE.sub("", v))
        if len(residue) <= 6:
            return True

    return False


def _char_classes(s):
    """Numero de classes de caractere presentes (minuscula/MAIUSCULA/digito/simbolo)."""
    classes = 0
    if re.search(r"[a-z]", s):
        classes += 1
    if re.search(r"[A-Z]", s):
        classes += 1
    if re.search(r"[0-9]", s):
        classes += 1
    if re.search(r"[^A-Za-z0-9]", s):
        classes += 1
    return classes


def _looks_like_example_path(file_path):
    if not file_path:
        return False
    fp = file_path.lower().replace("\\", "/")
    for suf in EXAMPLE_SUFFIXES:
        if fp.endswith(suf):
            return True
    return False


def find_secret(text, file_path):
    """
    Retorna uma string curta descrevendo o segredo encontrado,
    ou None se nada suspeito (ou tudo for placeholder).
    """
    if not text:
        return None

    if _looks_like_example_path(file_path):
        # Arquivo de exemplo: por contrato, nao bloqueamos.
        return None

    # 1) AWS access key
    m = RE_AWS_KEY.search(text)
    if m and not _is_placeholder_value(m.group(0)):
        return "AWS access key (AKIA...)"

    # 2) Chave privada
    if RE_PRIVATE_KEY.search(text):
        return "chave privada (PRIVATE KEY block)"

    # 3) Atribuicoes api_key/secret/token/password/...
    for m in RE_ASSIGNMENT.finditer(text):
        name = m.group(1)
        value = m.group(3)
        if _is_placeholder_value(value):
            continue
        # Regra generica (nome de var + string): exige "cara de segredo" —
        # >= 2 classes de caractere. Sem isso, prosa/exemplo de doc como
        # `# token = "abcdefghijklmnop"` (so minusculas) gera falso-positivo.
        # Padroes de alto sinal (AWS/GitHub/Slack/chave privada) nao passam
        # por aqui e continuam bloqueando em qualquer contexto.
        if _char_classes(value) < 2:
            continue
        return "credencial hardcoded em atribuicao ({}=...)".format(name)

    # 4) Tokens de provedores
    for rx, label in (
        (RE_SLACK, "Slack token (xox...)"),
        (RE_GITHUB, "GitHub token (gh?_...)"),
        (RE_BEARER, "Bearer token"),
    ):
        m = rx.search(text)
        if m and not _is_placeholder_value(m.group(0)):
            return label

    return None


# --- Extracao do texto novo por tipo de ferramenta ----------------------

def extract_new_text_and_path(tool_name, tool_input):
    """
    Retorna (texto_novo, file_path). Tolerante a variacoes de chave
    conforme o contrato (Write: content/content_to_write; Edit:
    new_string/new_contents; MultiEdit: updates[].newContents/new_string).
    """
    if not isinstance(tool_input, dict):
        return "", ""

    file_path = (
        tool_input.get("file_path")
        or tool_input.get("original_file_path")
        or tool_input.get("targetFile")
        or ""
    )

    if tool_name == "Write":
        text = (
            tool_input.get("content")
            or tool_input.get("content_to_write")
            or ""
        )
        return _as_text(text), file_path

    if tool_name == "Edit":
        text = (
            tool_input.get("new_string")
            or tool_input.get("new_contents")
            or ""
        )
        return _as_text(text), file_path

    if tool_name == "MultiEdit":
        parts = []
        # Variante 1: edits[] com new_string
        for key in ("edits", "updates"):
            seq = tool_input.get(key)
            if isinstance(seq, list):
                for item in seq:
                    if not isinstance(item, dict):
                        continue
                    v = (
                        item.get("new_string")
                        or item.get("newContents")
                        or item.get("new_contents")
                        or ""
                    )
                    if v:
                        parts.append(_as_text(v))
                    if not file_path:
                        file_path = item.get("targetFile") or file_path
        # Variante 2: MultiEdit tambem pode trazer new_string direto
        if not parts:
            v = tool_input.get("new_string") or tool_input.get("new_contents")
            if v:
                parts.append(_as_text(v))
        return "\n".join(parts), file_path

    return "", file_path


def _as_text(v):
    if isinstance(v, str):
        return v
    if v is None:
        return ""
    try:
        return str(v)
    except Exception:
        return ""


# --- Main ---------------------------------------------------------------

def main():
    # Leitura defensiva do stdin como utf-8.
    try:
        raw = sys.stdin.buffer.read()
        data = raw.decode("utf-8", errors="replace")
    except Exception:
        # stdin ilegivel -> fail-open
        return 0

    if not data.strip():
        return 0

    try:
        import json
        payload = json.loads(data)
    except Exception:
        # JSON invalido -> fail-open (nunca travar por bug de parsing)
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in ALLOWED_TOOLS:
        # Nao e uma escrita -> ignorar/permitir
        return 0

    tool_input = payload.get("tool_input") or {}

    try:
        new_text, file_path = extract_new_text_and_path(tool_name, tool_input)
        finding = find_secret(new_text, file_path)
    except Exception:
        # Qualquer erro na deteccao -> fail-open
        return 0

    if finding:
        where = file_path or "(arquivo sem caminho)"
        msg = (
            "[Alianca/portao] BLOQUEADO: possivel segredo hardcoded em '{}': {}.\n"
            "START-HERE §5: nunca commitar credencial -- use variavel de ambiente / "
            ".env (gitignored) / secret manager."
        ).format(where, finding)
        sys.stderr.write(msg + "\n")
        return 2

    return 0


if __name__ == "__main__":
    # Garantir stderr utf-8 mesmo em consoles legados.
    try:
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass
    sys.exit(main())
