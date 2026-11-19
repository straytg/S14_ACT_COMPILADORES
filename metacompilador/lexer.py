"""Etapa 1 - Análisis léxico.

Convierte el texto fuente en una lista de tokens. Cada patrón es la
expresión regular que se documenta en la formalización (ER -> AFND -> AFD).
Los caracteres que no pertenecen al alfabeto del lenguaje se reportan como
errores léxicos y el analizador continúa para informar todos los problemas.
"""

import re
from lark import Token
from lark.lexer import Lexer

from .errores import ErrorCompilacion

PALABRAS_RESERVADAS = {
    "solicitud": "_SOLICITUD",
    "politica": "_POLITICA",
    "regla": "_REGLA",
    "sino": "_SINO",
    "evaluar": "_EVALUAR",
    "con": "_CON",
}

# (nombre, expresión regular). El orden importa: gana la primera que coincide.
ESPECIFICACION = [
    ("COMENTARIO", r"//[^\n]*"),
    ("CADENA", r'"[^"\n]*"'),
    ("CADENA_ABIERTA", r'"[^"\n]*'),
    ("CODIGO", r"[A-Z]{3}-[0-9]{4}(?![A-Za-z0-9_])"),
    ("NUMERO", r"[0-9]+(\.[0-9]+)?"),
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OPREL", r">=|<=|==|!=|>|<"),
    ("OPSUM", r"[+\-]"),
    ("OPMUL", r"[*/]"),
    ("_LLAVE_A", r"\{"),
    ("_LLAVE_C", r"\}"),
    ("_PAR_A", r"\("),
    ("_PAR_C", r"\)"),
    ("_PUNTO_COMA", r";"),
    ("ESPACIO", r"[ \t\r\n]+"),
]

_PATRON = re.compile("|".join(f"(?P<{n}>{p})" for n, p in ESPECIFICACION))


def tokenizar(texto):
    """Devuelve (tokens, errores_lexicos)."""
    tokens, errores = [], []
    linea, inicio_linea, pos = 1, 0, 0
    n = len(texto)

    while pos < n:
        m = _PATRON.match(texto, pos)
        col = pos - inicio_linea + 1
        if not m:
            errores.append(ErrorCompilacion(
                "lexico", "L01",
                f"Carácter no válido {texto[pos]!r}: no pertenece al alfabeto del lenguaje",
                linea, col))
            pos += 1
            continue

        tipo, lexema = m.lastgroup, m.group()

        if tipo == "CADENA_ABIERTA":
            errores.append(ErrorCompilacion(
                "lexico", "L02", "Cadena sin cerrar: falta la comilla de cierre", linea, col))
        elif tipo == "NUMERO" and re.match(r"[A-Za-z_]", texto[m.end():m.end() + 1] or " "):
            # 12abc, 5000soles ... un número pegado a letras no es un token válido
            extra = re.match(r"[A-Za-z0-9_]+", texto[m.end():]).group()
            errores.append(ErrorCompilacion(
                "lexico", "L03",
                f"Número mal formado '{lexema}{extra}': no puede llevar letras pegadas",
                linea, col))
            pos = m.end() + len(extra)
            continue
        elif tipo == "NUMERO" and texto[m.end():m.end() + 1] == "." :
            errores.append(ErrorCompilacion(
                "lexico", "L04", f"Número mal formado '{lexema}.': punto decimal sin dígitos",
                linea, col))
            pos = m.end() + 1
            continue
        elif tipo == "ID":
            if lexema in PALABRAS_RESERVADAS:
                tokens.append(Token(PALABRAS_RESERVADAS[lexema], lexema, pos, linea, col))
            else:
                tokens.append(Token("ID", lexema, pos, linea, col))
        elif tipo not in ("COMENTARIO", "ESPACIO", "CADENA_ABIERTA"):
            tokens.append(Token(tipo, lexema, pos, linea, col))

        # actualizar contador de líneas
        saltos = lexema.count("\n")
        if saltos:
            linea += saltos
            inicio_linea = pos + lexema.rfind("\n") + 1
        pos = m.end()

    return tokens, errores


class LexerAdaptado(Lexer):
    """Entrega a Lark la lista de tokens ya generada por `tokenizar`."""

    def __init__(self, lexer_conf):
        pass

    def lex(self, datos):
        yield from datos
