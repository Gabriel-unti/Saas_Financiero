"""
Prueba manual del Dia 3: parse_invoice contra 3 comprobantes sinteticos
que cubren los casos exigidos por el plan (factura sin detraccion,
factura con detraccion, RHE sin IGV). Compara contra los valores fuente
en samples/generar_comprobantes_compra.py (COMPROBANTES).

Uso: python tests/test_parse_invoice_dia3.py
"""

import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))
sys.path.insert(0, str(BASE / "samples"))

from parse_invoice import parse_invoice  # noqa: E402
from generar_comprobantes_compra import COMPROBANTES  # noqa: E402

CASOS = ["FC-002_office_supply_peru.pdf", "FC-003_servitec_mantenimiento.pdf", "RHE-001_maria_quispe.pdf"]

FUENTE = {c["archivo"]: c for c in COMPROBANTES}

CAMPOS_A_COMPARAR = [
    "tipo_comprobante",
    "serie_correlativo",
    "fecha_emision",
    "ruc_emisor",
    "razon_social_emisor",
    "concepto",
    "moneda",
    "base_imponible",
    "igv",
    "total",
    "medio_pago",
    "aplica_detraccion",
    "codigo_spot",
    "tasa_detraccion",
]


def main():
    errores = 0
    for archivo in CASOS:
        extraido = parse_invoice(BASE / "samples" / "compras" / archivo)
        esperado = FUENTE[archivo]
        print(f"\n=== {archivo} ===")
        for campo in CAMPOS_A_COMPARAR:
            val_extraido = extraido.get(campo)
            val_esperado = esperado.get(campo)
            ok = val_extraido == val_esperado
            marca = "OK" if ok else "FAIL"
            if not ok:
                errores += 1
            print(f"  [{marca}] {campo}: extraido={val_extraido!r} esperado={val_esperado!r}")

    print(f"\n--- {'TODO OK' if errores == 0 else f'{errores} campo(s) con error'} ---")
    return errores


if __name__ == "__main__":
    sys.exit(main())
