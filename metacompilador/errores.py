"""Errores que puede reportar cada etapa del compilador CrediX."""

from dataclasses import dataclass, asdict


@dataclass
class ErrorCompilacion:
    etapa: str          # lexico | sintactico | semantico
    codigo: str         # ej. L01, S01, E03
    mensaje: str
    linea: int = 0
    columna: int = 0
    gravedad: str = "error"   # error | advertencia

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        pos = f"[{self.linea}:{self.columna}] " if self.linea else ""
        return f"{self.gravedad.upper()} {self.etapa} {self.codigo} {pos}{self.mensaje}"


# Nombres "humanos" de los tokens para los mensajes de error
NOMBRES_TOKEN = {
    "_SOLICITUD": "'solicitud'",
    "_POLITICA": "'politica'",
    "_REGLA": "'regla'",
    "_SINO": "'sino'",
    "_EVALUAR": "'evaluar'",
    "_CON": "'con'",
    "CODIGO": "código de solicitud (ej. SOL-0001)",
    "ID": "identificador",
    "NUMERO": "número",
    "CADENA": "texto entre comillas",
    "OPREL": "operador relacional",
    "OPSUM": "'+' o '-'",
    "OPMUL": "'*' o '/'",
    "_LLAVE_A": "'{'",
    "_LLAVE_C": "'}'",
    "_PAR_A": "'('",
    "_PAR_C": "')'",
    "_PUNTO_COMA": "';'",
    "$END": "fin del archivo",
}


def nombre_token(tipo):
    return NOMBRES_TOKEN.get(tipo, tipo)
