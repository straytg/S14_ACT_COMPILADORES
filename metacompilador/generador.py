"""Etapa 4 - Generación de código (transpilador CrediX -> Python).

Recorre el AST ya validado y emite un módulo Python. Ese módulo se ejecuta
(`ejecutar`) y produce los resultados verificables: decisión, cuota,
motivos de rechazo y cronograma de pagos.
"""

from .ast_nodos import (Programa, Solicitud, Politica, Evaluacion, Binaria,
                        Numero, Variable, expr_a_texto)

CABECERA = '''"""Código generado automáticamente por CrediX (TechSolutions SAC). No editar."""
from metacompilador.runtime import evaluar, dividir

SOLICITUDES = {}
POLITICAS = {}
RESULTADOS = []
'''


def _py(e):
    if isinstance(e, Numero):
        return repr(e.valor)
    if isinstance(e, Variable):
        return f"c[{e.nombre!r}]"
    if e.op == "/":
        return f"dividir({_py(e.izq)}, {_py(e.der)})"
    return f"({_py(e.izq)} {e.op} {_py(e.der)})"


def generar_python(programa: Programa) -> str:
    lineas = [CABECERA]
    for s in programa.sentencias:
        if isinstance(s, Solicitud):
            datos = {c.nombre: c.valor for c in s.campos}
            lineas.append(f"SOLICITUDES[{s.codigo!r}] = {datos!r}")
        elif isinstance(s, Politica):
            lineas.append(f"POLITICAS[{s.nombre!r}] = [")
            for r in s.reglas:
                cond = r.condicion
                texto = f"{expr_a_texto(cond.izq)} {cond.op} {expr_a_texto(cond.der)}"
                lineas.append(f"    ({texto!r}, lambda c: {_py(cond.izq)}, {cond.op!r}, "
                              f"lambda c: {_py(cond.der)}, {r.mensaje!r}),")
            lineas.append("]")
        elif isinstance(s, Evaluacion):
            lineas.append(f"RESULTADOS.append(dict(solicitud={s.codigo!r}, politica={s.politica!r}, "
                          f"**evaluar(SOLICITUDES[{s.codigo!r}], POLITICAS[{s.politica!r}])))")
    return "\n".join(lineas) + "\n"


def ejecutar(codigo_python: str):
    """Ejecuta el módulo generado y devuelve la lista de resultados."""
    espacio = {"__name__": "credix_generado"}
    exec(compile(codigo_python, "<credix_generado>", "exec"), espacio)
    return espacio["RESULTADOS"]
