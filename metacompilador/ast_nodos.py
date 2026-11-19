"""Nodos del árbol de sintaxis abstracta (AST) de CrediX."""

from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class Numero:
    valor: float
    linea: int = 0
    columna: int = 0


@dataclass
class Variable:
    nombre: str
    linea: int = 0
    columna: int = 0


@dataclass
class Binaria:
    op: str
    izq: "Expr"
    der: "Expr"
    linea: int = 0
    columna: int = 0


Expr = Union[Numero, Variable, Binaria]


@dataclass
class Campo:
    nombre: str
    valor: Union[float, str]
    tipo: str            # numero | cadena
    texto: str           # lexema original (sirve para validar el RUC)
    linea: int = 0
    columna: int = 0


@dataclass
class Solicitud:
    codigo: str
    campos: List[Campo] = field(default_factory=list)
    linea: int = 0


@dataclass
class Condicion:
    izq: Expr
    op: str
    der: Expr
    linea: int = 0


@dataclass
class Regla:
    condicion: Condicion
    mensaje: str
    linea: int = 0


@dataclass
class Politica:
    nombre: str
    reglas: List[Regla] = field(default_factory=list)
    linea: int = 0


@dataclass
class Evaluacion:
    codigo: str
    politica: str
    linea: int = 0
    columna: int = 0


@dataclass
class Programa:
    sentencias: list


# ---------------------------------------------------------------
# Utilidades: texto de una expresión y conversión a árbol (para UI)
# ---------------------------------------------------------------
def expr_a_texto(e):
    if isinstance(e, Numero):
        return f"{e.valor:g}"
    if isinstance(e, Variable):
        return e.nombre
    return f"({expr_a_texto(e.izq)} {e.op} {expr_a_texto(e.der)})"


def a_arbol(nodo):
    """Devuelve {etiqueta, hijos} para dibujar el árbol sintáctico."""
    if isinstance(nodo, Programa):
        return {"etiqueta": "programa", "hijos": [a_arbol(s) for s in nodo.sentencias]}
    if isinstance(nodo, Solicitud):
        return {"etiqueta": f"solicitud {nodo.codigo}",
                "hijos": [a_arbol(c) for c in nodo.campos]}
    if isinstance(nodo, Campo):
        v = f'"{nodo.valor}"' if nodo.tipo == "cadena" else nodo.texto
        return {"etiqueta": "campo", "hijos": [{"etiqueta": nodo.nombre, "hijos": []},
                                               {"etiqueta": v, "hijos": []}]}
    if isinstance(nodo, Politica):
        return {"etiqueta": f"politica {nodo.nombre}",
                "hijos": [a_arbol(r) for r in nodo.reglas]}
    if isinstance(nodo, Regla):
        return {"etiqueta": "regla", "hijos": [a_arbol(nodo.condicion),
                                               {"etiqueta": f'sino "{nodo.mensaje}"', "hijos": []}]}
    if isinstance(nodo, Condicion):
        return {"etiqueta": nodo.op, "hijos": [a_arbol(nodo.izq), a_arbol(nodo.der)]}
    if isinstance(nodo, Binaria):
        return {"etiqueta": nodo.op, "hijos": [a_arbol(nodo.izq), a_arbol(nodo.der)]}
    if isinstance(nodo, Numero):
        return {"etiqueta": f"{nodo.valor:g}", "hijos": []}
    if isinstance(nodo, Variable):
        return {"etiqueta": nodo.nombre, "hijos": []}
    if isinstance(nodo, Evaluacion):
        return {"etiqueta": "evaluar", "hijos": [{"etiqueta": nodo.codigo, "hijos": []},
                                                 {"etiqueta": nodo.politica, "hijos": []}]}
    return {"etiqueta": str(nodo), "hijos": []}
