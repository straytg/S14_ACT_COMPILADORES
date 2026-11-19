"""Etapa 3 - Análisis semántico.

Valida lo que la gramática no puede expresar: tipos de datos, rangos de las
reglas de negocio de TechSolutions SAC, RUC con dígito verificador, nombres
declarados antes de usarse y variables permitidas dentro de las políticas.
"""

from .ast_nodos import (Solicitud, Politica, Evaluacion, Binaria, Numero, Variable)
from .errores import ErrorCompilacion

# nombre -> (tipo, mínimo, máximo, obligatorio, entero)
CAMPOS = {
    "cliente": ("cadena", None, None, True, False),
    "ruc": ("cadena", None, None, True, False),
    "monto": ("numero", 500, 500000, True, False),
    "plazo": ("numero", 6, 60, True, True),
    "ingreso": ("numero", 1, None, True, False),
    "score": ("numero", 0, 1000, True, True),
    "tasa": ("numero", 1, 100, True, False),
    "deuda": ("numero", 0, None, False, False),
}

# Variables que pueden usarse dentro de una regla (campos numéricos + derivadas)
VARIABLES_POLITICA = {"monto", "plazo", "ingreso", "score", "tasa", "deuda",
                      "cuota", "endeudamiento"}

PREFIJOS_RUC = ("10", "15", "16", "17", "20")


def ruc_valido(ruc):
    """RUC peruano: 11 dígitos, prefijo válido y dígito verificador (módulo 11)."""
    if len(ruc) != 11 or not ruc.isdigit() or ruc[:2] not in PREFIJOS_RUC:
        return False
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(d) * p for d, p in zip(ruc[:10], pesos))
    return int(ruc[10]) == (11 - suma % 11) % 10


def analizar_semantica(programa):
    errores = []
    solicitudes, politicas, usadas, evaluadas = {}, {}, set(), set()

    def err(cod, msg, linea=0, col=0, gravedad="error"):
        errores.append(ErrorCompilacion("semantico", cod, msg, linea, col, gravedad))

    for s in programa.sentencias:
        if isinstance(s, Solicitud):
            _solicitud(s, solicitudes, err)
        elif isinstance(s, Politica):
            _politica(s, politicas, err)
        elif isinstance(s, Evaluacion):
            if s.codigo not in solicitudes:
                err("E08", f"La solicitud {s.codigo} no fue declarada antes de evaluarla", s.linea, s.columna)
            else:
                evaluadas.add(s.codigo)
            if s.politica not in politicas:
                err("E09", f"La política '{s.politica}' no fue declarada antes de usarla", s.linea, s.columna)
            else:
                usadas.add(s.politica)

    for cod, sol in solicitudes.items():
        if cod not in evaluadas:
            err("W01", f"La solicitud {cod} se declara pero nunca se evalúa", sol.linea, 0, "advertencia")
    for nom, pol in politicas.items():
        if nom not in usadas:
            err("W02", f"La política '{nom}' se declara pero nunca se aplica", pol.linea, 0, "advertencia")
    return errores


def _solicitud(s, tabla, err):
    if s.codigo in tabla:
        err("E01", f"La solicitud {s.codigo} ya fue declarada (línea {tabla[s.codigo].linea})", s.linea)
    else:
        tabla[s.codigo] = s

    vistos = {}
    for c in s.campos:
        if c.nombre not in CAMPOS:
            err("E04", f"El campo '{c.nombre}' no existe en una solicitud. "
                       f"Campos válidos: {', '.join(CAMPOS)}", c.linea, c.columna)
            continue
        if c.nombre in vistos:
            err("E12", f"El campo '{c.nombre}' está repetido en {s.codigo}", c.linea, c.columna)
            continue
        vistos[c.nombre] = c

        tipo, minimo, maximo, _, entero = CAMPOS[c.nombre]
        if c.tipo != tipo:
            esperado = "un texto entre comillas" if tipo == "cadena" else "un número"
            err("E05", f"El campo '{c.nombre}' debe ser {esperado}", c.linea, c.columna)
            continue
        if tipo == "numero":
            if entero and c.valor != int(c.valor):
                err("E06", f"El campo '{c.nombre}' debe ser un número entero", c.linea, c.columna)
            if minimo is not None and c.valor < minimo or maximo is not None and c.valor > maximo:
                rango = f"entre {minimo:g} y {maximo:g}" if maximo is not None else f"mayor o igual a {minimo:g}"
                err("E06", f"'{c.nombre}' = {c.valor:g} fuera de rango: debe estar {rango}", c.linea, c.columna)
        elif c.nombre == "ruc" and not ruc_valido(c.valor):
            err("E07", f"El RUC \"{c.valor}\" no es válido (11 dígitos, prefijo 10/15/16/17/20 y dígito verificador)",
                c.linea, c.columna)

    faltan = [n for n, (_, _, _, obl, _) in CAMPOS.items() if obl and n not in vistos]
    if faltan:
        err("E03", f"A la solicitud {s.codigo} le faltan campos obligatorios: {', '.join(faltan)}", s.linea)


def _politica(p, tabla, err):
    if p.nombre in tabla:
        err("E02", f"La política '{p.nombre}' ya fue declarada (línea {tabla[p.nombre].linea})", p.linea)
    else:
        tabla[p.nombre] = p
    for r in p.reglas:
        _expr(r.condicion.izq, err)
        _expr(r.condicion.der, err)


def _expr(e, err):
    if isinstance(e, Variable):
        if e.nombre not in VARIABLES_POLITICA:
            err("E10", f"La variable '{e.nombre}' no existe. Disponibles: {', '.join(sorted(VARIABLES_POLITICA))}",
                e.linea, e.columna)
    elif isinstance(e, Binaria):
        _expr(e.izq, err)
        _expr(e.der, err)
        if e.op == "/" and isinstance(e.der, Numero) and e.der.valor == 0:
            err("E11", "División entre cero en una regla", e.linea, e.columna)
