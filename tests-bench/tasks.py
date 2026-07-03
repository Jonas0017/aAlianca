# -*- coding: utf-8 -*-
"""Tarefas com entregável objetivo + verificadores.

Cada tarefa: id, prompt (idêntico nas duas condições), symbol (nome exigido),
e verify(ns) -> (core_frac, edge_frac) onde ns é o namespace do módulo gerado.
core_frac/edge_frac em [0,1]. Levantar exceção conta como 0 no bloco.
"""

def _frac(results):
    return sum(1 for r in results if r) / len(results) if results else 0.0


# ---------------- 1. palindrome ----------------
PALINDROME_PROMPT = (
    "Escreva uma função Python `is_palindrome(s: str) -> bool` que retorna True se a "
    "string for um palíndromo considerando APENAS caracteres alfanuméricos e IGNORANDO "
    "maiúsculas/minúsculas. String vazia deve retornar True. "
    "Entregue o arquivo completo em um único bloco de código Python."
)

def verify_palindrome(ns):
    f = ns["is_palindrome"]
    core = [
        f("A man, a plan, a canal: Panama") is True,
        f("race a car") is False,
        f("Was it a car or a cat I saw?") is True,
        f("hello") is False,
        f("RaceCar") is True,
    ]
    edge = [
        f("") is True,
        f(".,") is True,          # só não-alfanumérico -> vazio -> True
        f("a") is True,
    ]
    return _frac(core), _frac(edge)


# ---------------- 2. CPF ----------------
CPF_PROMPT = (
    "Escreva uma função Python `valida_cpf(cpf: str) -> bool` que valida um CPF brasileiro "
    "pelos dois dígitos verificadores. Deve aceitar o CPF com ou sem máscara (pontos e traço). "
    "CPFs com todos os dígitos iguais (ex.: 00000000000, 11111111111) são INVÁLIDOS. "
    "Qualquer entrada que não tenha exatamente 11 dígitos é inválida. "
    "Entregue o arquivo completo em um único bloco de código Python."
)

def verify_cpf(ns):
    f = ns["valida_cpf"]
    core = [
        f("529.982.247-25") is True,      # válido conhecido
        f("52998224725") is True,          # mesmo, sem máscara
        f("111.444.777-35") is True,       # válido conhecido
        f("529.982.247-24") is False,      # dígito errado
        f("123.456.789-00") is False,      # inválido
    ]
    edge = [
        f("00000000000") is False,         # todos iguais
        f("11111111111") is False,
        f("") is False,
        f("123") is False,                 # curto demais
        f("5299822472") is False,          # 10 dígitos
    ]
    return _frac(core), _frac(edge)


# ---------------- 3. FizzBuzz ----------------
FIZZBUZZ_PROMPT = (
    "Escreva uma função Python `fizzbuzz(n: int) -> list` que retorna uma LISTA com os "
    "resultados de 1 até n (inclusive): múltiplos de 3 viram 'Fizz', de 5 viram 'Buzz', "
    "de 3 e 5 viram 'FizzBuzz', e os demais viram o próprio número como int. "
    "Entregue o arquivo completo em um único bloco de código Python."
)

def verify_fizzbuzz(ns):
    f = ns["fizzbuzz"]
    r15 = f(15)
    core = [
        isinstance(r15, list),
        len(r15) == 15,
        r15[0] == 1,
        r15[2] == "Fizz",
        r15[4] == "Buzz",
        r15[14] == "FizzBuzz",
        r15[13] == 14,
    ]
    edge = [
        f(1) == [1],
        f(0) == [],
        f(3) == [1, 2, "Fizz"],
    ]
    return _frac(core), _frac(edge)


# ---------------- 4. RPN (harder) ----------------
RPN_PROMPT = (
    "Escreva uma função Python `eval_rpn(tokens: list) -> float` que avalia uma expressão em "
    "notação polonesa reversa (RPN). tokens é uma lista de strings, cada uma sendo um número "
    "ou um dos operadores '+', '-', '*', '/'. Ex.: ['2','1','+','3','*'] resulta em 9. "
    "Divisão é divisão real (float). "
    "Entregue o arquivo completo em um único bloco de código Python."
)

def verify_rpn(ns):
    f = ns["eval_rpn"]
    core = [
        abs(f(["2", "1", "+", "3", "*"]) - 9) < 1e-6,
        abs(f(["4", "13", "5", "/", "+"]) - 6.6) < 1e-6,
        abs(f(["5"]) - 5) < 1e-6,
        abs(f(["10", "6", "-"]) - 4) < 1e-6,
        abs(f(["2", "3", "*", "4", "+"]) - 10) < 1e-6,
    ]
    edge = [
        abs(f(["7", "2", "/"]) - 3.5) < 1e-6,   # divisão real
        abs(f(["3", "4", "5", "*", "-"]) - (-17)) < 1e-6,
        abs(f(["-3", "4", "+"]) - 1) < 1e-6,     # número negativo
    ]
    return _frac(core), _frac(edge)


# ---------------- 5. int_to_roman ----------------
ROMAN_PROMPT = (
    "Escreva uma função Python `int_to_roman(n: int) -> str` que converte um inteiro entre "
    "1 e 3999 (inclusive) para numeral romano em maiúsculas. "
    "Entregue o arquivo completo em um único bloco de código Python."
)

def verify_roman(ns):
    f = ns["int_to_roman"]
    core = [
        f(1) == "I",
        f(4) == "IV",
        f(9) == "IX",
        f(58) == "LVIII",
        f(1994) == "MCMXCIV",
    ]
    edge = [
        f(3999) == "MMMCMXCIX",
        f(40) == "XL",
        f(90) == "XC",
        f(400) == "CD",
    ]
    return _frac(core), _frac(edge)


TASKS = [
    {"id": "palindrome", "symbol": "is_palindrome", "prompt": PALINDROME_PROMPT, "verify": verify_palindrome},
    {"id": "cpf",        "symbol": "valida_cpf",    "prompt": CPF_PROMPT,        "verify": verify_cpf},
    {"id": "fizzbuzz",   "symbol": "fizzbuzz",      "prompt": FIZZBUZZ_PROMPT,   "verify": verify_fizzbuzz},
    {"id": "rpn",        "symbol": "eval_rpn",      "prompt": RPN_PROMPT,         "verify": verify_rpn},
    {"id": "roman",      "symbol": "int_to_roman",  "prompt": ROMAN_PROMPT,       "verify": verify_roman},
]
