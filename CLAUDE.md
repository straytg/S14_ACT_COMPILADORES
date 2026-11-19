# Guía para el agente (Claude Code)

- Toda la lógica del compilador está en `metacompilador/`. **No** poner reglas de negocio en `backend/` ni `frontend/`.
- Para cambiar el lenguaje: editar `metacompilador/gramatica/credix.lark`, luego `lexer.py` (mismos terminales), `parser.py` (AST) y `semantico.py`.
- Toda etapa nueva devuelve `ErrorCompilacion` (ver `errores.py`); códigos: L=léxico, S=sintáctico, E/W=semántico.
- Verificar siempre con `python -m pytest -q` y `python credix.py ejemplos/credito_pyme.crx`.
- Estilo de interfaz: glassmorphism, malla de gradientes, plano técnico, ASCII cinético, pipeline isométrico, partículas.
