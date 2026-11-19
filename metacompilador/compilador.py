"""Orquestador del metacompilador: encadena las 4 etapas y devuelve un
resultado serializable. Es el ÚNICO punto de entrada que usan el backend
(Flask), la línea de comandos y las pruebas."""

from .lexer import tokenizar
from .parser import analizar_sintaxis
from .semantico import analizar_semantica
from .generador import generar_python, ejecutar
from .ast_nodos import a_arbol


def compilar(fuente: str) -> dict:
    etapas = {"lexico": "pendiente", "sintactico": "pendiente",
              "semantico": "pendiente", "generacion": "pendiente"}
    salida = {"ok": False, "etapas": etapas, "tokens": [], "errores": [], "advertencias": [],
              "arbol": None, "codigo_python": "", "resultados": []}

    # 1. léxico
    tokens, errores = tokenizar(fuente)
    salida["tokens"] = [{"tipo": t.type.lstrip("_"), "valor": str(t), "linea": t.line, "columna": t.column}
                        for t in tokens]
    if errores:
        etapas["lexico"] = "error"
        salida["errores"] = [e.to_dict() for e in errores]
        return salida
    etapas["lexico"] = "ok"

    # 2. sintáctico
    programa, errores = analizar_sintaxis(tokens)
    if errores or programa is None:
        etapas["sintactico"] = "error"
        salida["errores"] = [e.to_dict() for e in errores]
        return salida
    etapas["sintactico"] = "ok"
    salida["arbol"] = a_arbol(programa)

    # 3. semántico
    problemas = analizar_semantica(programa)
    errores = [e for e in problemas if e.gravedad == "error"]
    salida["advertencias"] = [e.to_dict() for e in problemas if e.gravedad == "advertencia"]
    if errores:
        etapas["semantico"] = "error"
        salida["errores"] = [e.to_dict() for e in errores]
        return salida
    etapas["semantico"] = "ok"

    # 4. generación y ejecución
    codigo = generar_python(programa)
    salida["codigo_python"] = codigo
    salida["resultados"] = ejecutar(codigo)
    etapas["generacion"] = "ok"
    salida["ok"] = True
    return salida
