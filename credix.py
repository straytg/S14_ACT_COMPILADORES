"""Línea de comandos:  python credix.py ejemplos/credito_pyme.crx"""
import sys
from metacompilador import compilar


def main():
    if len(sys.argv) < 2:
        print("Uso: python credix.py archivo.crx [--python]")
        return 2
    r = compilar(open(sys.argv[1], encoding="utf-8").read())
    for e in r["errores"] + r["advertencias"]:
        print(f"{e['gravedad'].upper():11} {e['codigo']} línea {e['linea']}:{e['columna']}  {e['mensaje']}")
    if "--python" in sys.argv:
        print(r["codigo_python"])
    for x in r["resultados"]:
        print(f"{x['solicitud']}  {x['decision']:10} cuota S/ {x['cuota']:,.2f}  "
              f"endeudamiento {x['endeudamiento']:.1%}")
        for m in x["motivos"]:
            print("     -", m)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
