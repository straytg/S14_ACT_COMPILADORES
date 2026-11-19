import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from metacompilador import compilar  # noqa: E402
from metacompilador.runtime import cuota_francesa  # noqa: E402
from metacompilador.semantico import ruc_valido  # noqa: E402

EJ = Path(__file__).resolve().parent.parent / "ejemplos"

BASE = '''politica P { regla score >= 600 sino "bajo"; }
solicitud SOL-0001 { cliente "A"; ruc "20512345671"; monto 10000; plazo 12; ingreso 5000; score %d; tasa 20; }
evaluar SOL-0001 con P;'''


def codigos(src):
    return {e["codigo"] for e in compilar(src)["errores"]}


def test_ejemplo_completo():
    r = compilar((EJ / "credito_pyme.crx").read_text(encoding="utf-8"))
    assert r["ok"]
    decisiones = [x["decision"] for x in r["resultados"]]
    assert decisiones == ["APROBADO", "RECHAZADO", "APROBADO"]


def test_cronograma_cuadra():
    r = compilar(BASE % 700)
    res = r["resultados"][0]
    assert res["decision"] == "APROBADO"
    assert len(res["cronograma"]) == 12
    assert res["cronograma"][-1]["saldo"] < 0.05
    assert abs(res["cuota"] - cuota_francesa(10000, 12, 20)) < 0.01


def test_rechazo_por_score():
    res = compilar(BASE % 500)["resultados"][0]
    assert res["decision"] == "RECHAZADO" and res["motivos"] == ["bajo"]


def test_errores_lexicos():
    assert codigos('solicitud SOL-0001 { cliente "x; }') == {"L02"}
    assert "L03" in codigos("solicitud SOL-0001 { monto 12abc; }")
    assert "L01" in codigos("solicitud SOL-0001 { # }")


def test_errores_sintacticos():
    assert "S01" in codigos("solicitud SOL-0001 { monto 100 plazo 12; }")
    assert "S02" in codigos("solicitud SOL-0001 { monto 100;")


def test_errores_semanticos():
    assert "E03" in codigos('solicitud SOL-0001 { cliente "A"; }')
    assert "E06" in codigos((BASE % 700).replace("score 700", "score 1500"))
    assert "E07" in codigos(BASE.replace("20512345671", "20512345670") % 700)
    assert "E08" in codigos("evaluar SOL-0009 con P;")
    assert "E10" in codigos('politica P { regla edad > 3 sino "x"; }')
    assert "E01" in codigos((BASE % 700) + "\n" + BASE.split("\n", 1)[1].rsplit("\n", 1)[0] % 700)


def test_ruc():
    assert ruc_valido("20512345671") and not ruc_valido("20512345672")
    assert not ruc_valido("1234")
