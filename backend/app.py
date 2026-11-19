"""Backend Flask de CrediX. Solo expone HTTP: toda la lógica de compilación
vive en el paquete `metacompilador` (no hay reglas de negocio aquí)."""

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from flask import Flask, jsonify, request, send_from_directory, abort  # noqa: E402
from metacompilador import compilar  # noqa: E402
from metacompilador.parser import RUTA_GRAMATICA  # noqa: E402

app = Flask(__name__, static_folder=None)
EJEMPLOS = RAIZ / "ejemplos"
FRONTEND = RAIZ / "frontend"
LIMITE = 20_000  # caracteres


@app.post("/api/compilar")
def api_compilar():
    datos = request.get_json(silent=True) or {}
    fuente = datos.get("fuente", "")
    if not isinstance(fuente, str) or len(fuente) > LIMITE:
        return jsonify(error="Fuente inválida o demasiado larga"), 400
    return jsonify(compilar(fuente))


@app.get("/api/ejemplos")
def api_ejemplos():
    return jsonify([p.stem for p in sorted(EJEMPLOS.glob("*.crx"))])


@app.get("/api/ejemplos/<nombre>")
def api_ejemplo(nombre):
    ruta = EJEMPLOS / f"{nombre}.crx"
    if not ruta.is_file() or ruta.parent != EJEMPLOS:
        abort(404)
    return jsonify(nombre=nombre, fuente=ruta.read_text(encoding="utf-8"))


@app.get("/api/gramatica")
def api_gramatica():
    return jsonify(gramatica=RUTA_GRAMATICA.read_text(encoding="utf-8"))


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/<path:ruta>")
def estaticos(ruta):
    return send_from_directory(FRONTEND, ruta)


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=False)
