"""Etapa 2 - Análisis sintáctico.

La gramática vive en gramatica/credix.lark. El metacompilador (Lark) genera a
partir de ella un analizador LALR(1); aquí solo lo cargamos, recuperamos los
errores sintácticos y convertimos el árbol de derivación en un AST.
"""

from pathlib import Path
from lark import Lark, Transformer, v_args, Token
from lark.exceptions import UnexpectedToken, UnexpectedInput

from .ast_nodos import (Programa, Solicitud, Campo, Politica, Regla, Condicion,
                        Evaluacion, Binaria, Numero, Variable)
from .errores import ErrorCompilacion, nombre_token
from .lexer import LexerAdaptado

RUTA_GRAMATICA = Path(__file__).parent / "gramatica" / "credix.lark"
MAX_ERRORES = 8

_parser = Lark(RUTA_GRAMATICA.read_text(encoding="utf-8"),
               parser="lalr", lexer=LexerAdaptado, start="start")


@v_args(inline=True)
class ConstructorAST(Transformer):
    def start(self, *sentencias):
        return Programa(list(sentencias))

    def solicitud(self, codigo, *campos):
        return Solicitud(str(codigo), list(campos), codigo.line)

    def campo(self, nombre, valor):
        if isinstance(valor, Numero):
            return Campo(str(nombre), valor.valor, "numero", f"{valor.valor:g}", nombre.line, nombre.column)
        return Campo(str(nombre), valor, "cadena", valor, nombre.line, nombre.column)

    def numero(self, tok):
        return Numero(float(tok), tok.line, tok.column)

    def cadena(self, tok):
        return str(tok)[1:-1]

    def variable(self, tok):
        return Variable(str(tok), tok.line, tok.column)

    def binaria(self, izq, op, der):
        return Binaria(str(op), izq, der, op.line, op.column)

    def condicion(self, izq, op, der):
        return Condicion(izq, str(op), der, op.line)

    def regla(self, condicion, mensaje):
        return Regla(condicion, str(mensaje)[1:-1], mensaje.line)

    def politica(self, nombre, *reglas):
        return Politica(str(nombre), list(reglas), nombre.line)

    def evaluacion(self, codigo, politica):
        return Evaluacion(str(codigo), str(politica), codigo.line, codigo.column)


def _describir(tok):
    if tok.type == "$END":
        return "el fin del archivo"
    return f"'{tok.value}'"


INICIOS = {"_SOLICITUD", "_POLITICA", "_EVALUAR"}


def _dividir_sentencias(tokens):
    """Recuperación por sentencia: cada 'solicitud', 'politica' o 'evaluar'
    inicia un bloque que se analiza por separado."""
    bloques = []
    for t in tokens:
        if t.type in INICIOS or not bloques:
            bloques.append([])
        bloques[-1].append(t)
    return bloques


def _error_de(e):
    tok = e.token
    try:
        esperados = sorted({nombre_token(t) for t in (e.accepts or e.expected)})
    except Exception:
        esperados = sorted({nombre_token(t) for t in e.expected})
    lista = ", ".join(esperados[:4]) + ("…" if len(esperados) > 4 else "")
    if tok.type == "$END":
        return ErrorCompilacion("sintactico", "S02",
                                f"La sentencia termina antes de tiempo. Se esperaba: {lista}",
                                tok.line or 0, tok.column or 0)
    return ErrorCompilacion("sintactico", "S01",
                            f"Se encontró {_describir(tok)} pero se esperaba: {lista}",
                            tok.line or 0, tok.column or 0)


def analizar_sintaxis(tokens):
    """Devuelve (ast | None, errores_sintacticos)."""
    if not tokens:
        return None, [ErrorCompilacion("sintactico", "S03",
                                       "El programa está vacío: se esperaba al menos una sentencia", 1, 1)]
    errores, sentencias = [], []
    for bloque in _dividir_sentencias(tokens):
        try:
            sentencias.extend(ConstructorAST().transform(_parser.parse(bloque)).sentencias)
        except UnexpectedToken as e:
            errores.append(_error_de(e))
        except UnexpectedInput as e:
            errores.append(ErrorCompilacion("sintactico", "S99", str(e)))
    if errores:
        return None, errores[:MAX_ERRORES]
    return Programa(sentencias), []
