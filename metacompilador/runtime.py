"""Funciones de apoyo que usa el código Python generado por el transpilador."""

import operator

OPERADORES = {">=": operator.ge, "<=": operator.le, "==": operator.eq,
              "!=": operator.ne, ">": operator.gt, "<": operator.lt}


def cuota_francesa(monto, plazo, tasa_anual):
    """Cuota fija mensual (sistema francés). La tasa llega como % efectivo anual."""
    i = (1 + tasa_anual / 100) ** (1 / 12) - 1
    if i == 0:
        return monto / plazo
    return monto * i / (1 - (1 + i) ** -plazo)


def cronograma(monto, plazo, tasa_anual):
    i = (1 + tasa_anual / 100) ** (1 / 12) - 1
    cuota = cuota_francesa(monto, plazo, tasa_anual)
    saldo, filas = monto, []
    for n in range(1, int(plazo) + 1):
        interes = saldo * i
        capital = cuota - interes
        saldo = max(saldo - capital, 0.0)
        filas.append({"n": n, "cuota": round(cuota, 2), "interes": round(interes, 2),
                      "capital": round(capital, 2), "saldo": round(saldo, 2)})
    return filas


def contexto(s):
    """Variables disponibles para las reglas de una solicitud."""
    c = dict(s)
    c.setdefault("deuda", 0.0)
    c["cuota"] = cuota_francesa(c["monto"], c["plazo"], c["tasa"])
    c["endeudamiento"] = (c["deuda"] + c["cuota"]) / c["ingreso"]
    return c


def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("división entre cero")
    return a / b


def evaluar(solicitud, politica):
    """Aplica una política y construye el resultado verificable."""
    ctx = contexto(solicitud)
    detalle, rechazos = [], []
    for texto, f_izq, op, f_der, mensaje in politica:
        try:
            izq, der = f_izq(ctx), f_der(ctx)
            ok = OPERADORES[op](izq, der)
            detalle.append({"regla": texto, "izquierda": round(izq, 4), "derecha": round(der, 4),
                            "cumple": bool(ok)})
            if not ok:
                rechazos.append(mensaje)
        except ZeroDivisionError:
            detalle.append({"regla": texto, "izquierda": None, "derecha": None, "cumple": False})
            rechazos.append(f"Regla no evaluable (división entre cero): {texto}")
    aprobado = not rechazos
    resultado = {
        "cliente": solicitud["cliente"], "monto": solicitud["monto"], "plazo": solicitud["plazo"],
        "tasa": solicitud["tasa"], "cuota": round(ctx["cuota"], 2),
        "endeudamiento": round(ctx["endeudamiento"], 4),
        "decision": "APROBADO" if aprobado else "RECHAZADO",
        "motivos": rechazos, "reglas": detalle, "cronograma": [],
    }
    if aprobado:
        filas = cronograma(solicitud["monto"], solicitud["plazo"], solicitud["tasa"])
        resultado["cronograma"] = filas
        resultado["total_intereses"] = round(sum(f["interes"] for f in filas), 2)
        resultado["total_a_pagar"] = round(sum(f["cuota"] for f in filas), 2)
    return resultado
