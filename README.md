# CrediX · Metacompilador de préstamos y créditos

Actividad de Compiladores (S14). **Empresa:** TechSolutions SAC · **Proceso:** Préstamos y créditos
(venta de equipos a crédito para pymes). CrediX es un DSL cuyo metacompilador (Lark) genera el analizador
LALR(1) a partir de una gramática libre de contexto, valida reglas de negocio y transpila a Python.

## Estructura (lógica separada de front y back)

```
metacompilador/        <- LÓGICA (no depende de Flask ni del navegador)
  gramatica/credix.lark   GLC: entrada del metacompilador
  lexer.py                etapa 1: análisis léxico (ER) + errores L0x
  parser.py               etapa 2: análisis sintáctico LALR(1) + AST + errores S0x
  semantico.py            etapa 3: tipos, rangos, RUC, declaración previa + errores E/W
  generador.py            etapa 4: transpilador a Python y ejecución
  runtime.py              cuota francesa, cronograma, evaluación de políticas
  compilador.py           orquestador: compilar(texto) -> dict
backend/app.py         <- BACK: API Flask (solo HTTP)
frontend/              <- FRONT: HTML + CSS + JS (consume /api)
ejemplos/*.crx         programas de ejemplo (uno correcto y tres con errores)
tests/                 pruebas con pytest
credix.py              CLI
```

## Ejecutar

```bash
pip install -r requirements.txt
python backend/app.py          # abrir http://127.0.0.1:5000
python credix.py ejemplos/credito_pyme.crx
python -m pytest -q
```

## El lenguaje

```
politica ESTANDAR {
    regla score >= 600 sino "Score por debajo del mínimo";
    regla endeudamiento <= 0.35 sino "La cuota supera el 35% del ingreso";
}
solicitud SOL-0147 { cliente "Inversiones Rímac SAC"; ruc "20512345671"; monto 18500;
                     plazo 24; ingreso 9200; deuda 800; score 710; tasa 18.5; }
evaluar SOL-0147 con ESTANDAR;
```

Variables de una regla: `monto plazo ingreso score tasa deuda cuota endeudamiento`.
