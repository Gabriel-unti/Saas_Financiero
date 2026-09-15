"""
Genera comprobantes de compra 100% sinteticos (PDF) + CSV de referencia
para el desarrollo del Agente Contable (semana 1, dia 2 del plan).

Todos los RUC, razones sociales y montos son inventados. El receptor
("ANDINA SOLUTIONS SAC") es una empresa demo ficticia, sin relacion con
ningun cliente real -- por decision explicita, este set nunca usa datos
de Braidy Wonders / Tucano Peru.

Uso: python generar_comprobantes_compra.py
Salida: samples/compras/*.pdf + samples/compras_ground_truth.csv
"""

import csv
from pathlib import Path

from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

RECEPTOR_RUC = "20512345678"
RECEPTOR_RAZON = "ANDINA SOLUTIONS SAC"

COMPROBANTES = [
    dict(
        archivo="FC-001_transportes_carga_sur.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000145",
        fecha_emision="15/09/2026",
        ruc_emisor="20487654321",
        razon_social_emisor="TRANSPORTES CARGA SUR SAC",
        concepto="Servicio de transporte de carga nacional",
        moneda="PEN",
        base_imponible=3500.00,
        igv=630.00,
        total=4130.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="si",
        codigo_spot="026",
        tasa_detraccion=0.04,
        cuenta_gasto_pcge="631",
        notas="",
    ),
    dict(
        archivo="FC-002_office_supply_peru.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000146",
        fecha_emision="16/09/2026",
        ruc_emisor="20498765432",
        razon_social_emisor="OFFICE SUPPLY PERU SAC",
        concepto="Compra de suministros de oficina",
        moneda="PEN",
        base_imponible=850.00,
        igv=153.00,
        total=1003.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="",
    ),
    dict(
        archivo="FC-003_servitec_mantenimiento.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000147",
        fecha_emision="17/09/2026",
        ruc_emisor="20476543210",
        razon_social_emisor="SERVITEC MANTENIMIENTO SAC",
        concepto="Mantenimiento de equipos de computo",
        moneda="PEN",
        base_imponible=1200.00,
        igv=216.00,
        total=1416.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="si",
        codigo_spot="022",
        tasa_detraccion=0.12,
        cuenta_gasto_pcge="632",
        notas="",
    ),
    dict(
        archivo="RHE-001_maria_quispe.pdf",
        tipo_comprobante="RHE",
        serie_correlativo="E001-000078",
        fecha_emision="18/09/2026",
        ruc_emisor="10456789012",
        razon_social_emisor="MARIA ELENA QUISPE TORRES",
        concepto="Servicio de asesoria contable mensual",
        moneda="PEN",
        base_imponible=1800.00,
        igv=0.00,
        total=1800.00,
        afectacion_igv="no_gravado",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="Sin IGV: no derivar Valor_Venta como Total/1.18",
    ),
    dict(
        archivo="BV-001_ferreteria_constructor.pdf",
        tipo_comprobante="boleta",
        serie_correlativo="B001-008821",
        fecha_emision="19/09/2026",
        ruc_emisor="20505566778",
        razon_social_emisor="FERRETERIA EL CONSTRUCTOR EIRL",
        concepto="Utiles de oficina varios",
        moneda="PEN",
        base_imponible=180.00,
        igv=32.40,
        total=212.40,
        afectacion_igv="gravada",
        medio_pago="Efectivo",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="",
    ),
    dict(
        archivo="FC-004_seguridad_integral.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000148",
        fecha_emision="20/09/2026",
        ruc_emisor="20465432109",
        razon_social_emisor="SEGURIDAD INTEGRAL SAC",
        concepto="Servicio de vigilancia (1 dia)",
        moneda="PEN",
        base_imponible=500.00,
        igv=90.00,
        total=590.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="no",
        codigo_spot="021",
        tasa_detraccion="",
        cuenta_gasto_pcge="639",
        notas="Codigo SPOT 021 esta en la lista, pero el importe (590) "
        "no supera el umbral de S/700: NO aplica detraccion.",
    ),
    dict(
        archivo="FC-005_publicidad_digital.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000149",
        fecha_emision="21/09/2026",
        ruc_emisor="20443322110",
        razon_social_emisor="PUBLICIDAD DIGITAL PERU SAC",
        concepto="Campana de publicidad digital",
        moneda="PEN",
        base_imponible=5000.00,
        igv=900.00,
        total=5900.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="",
    ),
    dict(
        archivo="RHE-002_jorge_ramos.pdf",
        tipo_comprobante="RHE",
        serie_correlativo="E001-000079",
        fecha_emision="22/09/2026",
        ruc_emisor="10498765432",
        razon_social_emisor="JORGE LUIS RAMOS FLORES",
        concepto="Servicio de asesoria legal societaria",
        moneda="PEN",
        base_imponible=2500.00,
        igv=0.00,
        total=2500.00,
        afectacion_igv="no_gravado",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="Sin IGV: no derivar Valor_Venta como Total/1.18",
    ),
    dict(
        archivo="BV-002_grifo_san_isidro.pdf",
        tipo_comprobante="boleta",
        serie_correlativo="B001-008822",
        fecha_emision="23/09/2026",
        ruc_emisor="20411223344",
        razon_social_emisor="GRIFO SAN ISIDRO EIRL",
        concepto="Combustible (Diesel B5) para unidad de transporte",
        moneda="PEN",
        base_imponible=320.00,
        igv=57.60,
        total=377.60,
        afectacion_igv="gravada",
        medio_pago="Efectivo",
        aplica_detraccion="no",
        codigo_spot="",
        tasa_detraccion="",
        cuenta_gasto_pcge="",
        notas="",
    ),
    dict(
        archivo="FC-006_inmobiliaria_centro.pdf",
        tipo_comprobante="factura",
        serie_correlativo="F001-000150",
        fecha_emision="24/09/2026",
        ruc_emisor="20422334455",
        razon_social_emisor="INMOBILIARIA CENTRO SAC",
        concepto="Alquiler de local comercial (setiembre 2026)",
        moneda="PEN",
        base_imponible=4000.00,
        igv=720.00,
        total=4720.00,
        afectacion_igv="gravada",
        medio_pago="Transferencia bancaria",
        aplica_detraccion="si",
        codigo_spot="020",
        tasa_detraccion=0.12,
        cuenta_gasto_pcge="634",
        notas="",
    ),
]


def monto_detraccion(c):
    if c["aplica_detraccion"] == "si" and c["tasa_detraccion"]:
        return round(c["total"] * c["tasa_detraccion"], 2)
    return ""


def dibujar_factura_o_boleta(cv, c):
    ancho, alto = A5
    y = alto - 40

    cv.setFont("Helvetica-Bold", 11)
    cv.drawString(30, y, c["razon_social_emisor"])
    cv.setFont("Helvetica", 9)
    cv.drawString(30, y - 14, f"RUC: {c['ruc_emisor']}")

    etiqueta = {"factura": "FACTURA ELECTRONICA", "boleta": "BOLETA DE VENTA ELECTRONICA"}[
        c["tipo_comprobante"]
    ]
    cv.setFont("Helvetica-Bold", 10)
    cv.drawRightString(ancho - 30, y, etiqueta)
    cv.drawRightString(ancho - 30, y - 14, c["serie_correlativo"])

    y -= 40
    cv.setFont("Helvetica", 9)
    cv.drawString(30, y, f"Senor(es): {RECEPTOR_RAZON}")
    y -= 12
    cv.drawString(30, y, f"RUC: {RECEPTOR_RUC}")
    y -= 12
    cv.drawString(30, y, f"Fecha de Emision: {c['fecha_emision']}")
    y -= 12
    cv.drawString(30, y, f"Moneda: {c['moneda']}")

    y -= 20
    cv.line(30, y, ancho - 30, y)
    y -= 14
    cv.setFont("Helvetica-Bold", 9)
    cv.drawString(30, y, "Descripcion")
    cv.drawRightString(ancho - 30, y, "Importe")
    y -= 12
    cv.setFont("Helvetica", 9)
    cv.drawString(30, y, c["concepto"])
    cv.drawRightString(ancho - 30, y, f"{c['base_imponible']:.2f}")

    y -= 16
    cv.line(30, y, ancho - 30, y)
    y -= 14
    cv.drawRightString(ancho - 30, y, f"Valor Venta: {c['base_imponible']:.2f}")
    y -= 12
    cv.drawRightString(ancho - 30, y, f"IGV (18%): {c['igv']:.2f}")
    y -= 12
    cv.setFont("Helvetica-Bold", 9)
    cv.drawRightString(ancho - 30, y, f"Importe Total: {c['total']:.2f}")

    y -= 24
    cv.setFont("Helvetica", 9)
    cv.drawString(30, y, f"Forma de Pago: {c['medio_pago']}")

    if c["aplica_detraccion"] == "si":
        y -= 14
        cv.drawString(
            30,
            y,
            f"Sujeto a detraccion: SI - Codigo {c['codigo_spot']} - "
            f"Tasa {int(c['tasa_detraccion'] * 100)}%",
        )
        y -= 12
        cv.drawString(30, y, f"Monto de detraccion: S/ {monto_detraccion(c):.2f}")
    elif c["codigo_spot"]:
        y -= 14
        cv.drawString(
            30, y, f"Codigo SPOT {c['codigo_spot']} presente, no supera umbral de deteccion."
        )


def dibujar_rhe(cv, c):
    ancho, alto = A5
    y = alto - 40

    cv.setFont("Helvetica-Bold", 11)
    cv.drawCentredString(ancho / 2, y, "RECIBO POR HONORARIOS ELECTRONICO")
    y -= 16
    cv.setFont("Helvetica", 9)
    cv.drawCentredString(ancho / 2, y, c["serie_correlativo"])

    y -= 28
    cv.drawString(30, y, c["razon_social_emisor"])
    y -= 12
    cv.drawString(30, y, f"RUC: {c['ruc_emisor']}")

    y -= 24
    cv.line(30, y, ancho - 30, y)
    y -= 14
    cv.drawString(30, y, f"Senor(es): {RECEPTOR_RAZON}")
    y -= 12
    cv.drawString(30, y, f"RUC: {RECEPTOR_RUC}")
    y -= 12
    cv.drawString(30, y, f"Fecha de Emision: {c['fecha_emision']}")

    y -= 20
    cv.line(30, y, ancho - 30, y)
    y -= 14
    cv.drawString(30, y, f"Por concepto de: {c['concepto']}")

    y -= 24
    cv.setFont("Helvetica-Bold", 9)
    cv.drawRightString(ancho - 30, y, f"Monto Bruto: {c['base_imponible']:.2f}")
    y -= 12
    cv.drawRightString(ancho - 30, y, f"Total: {c['total']:.2f}")

    y -= 24
    cv.setFont("Helvetica", 9)
    cv.drawString(30, y, f"Forma de Pago: {c['medio_pago']}")


def generar_pdf(ruta: Path, c: dict):
    cv = canvas.Canvas(str(ruta), pagesize=A5)
    if c["tipo_comprobante"] == "RHE":
        dibujar_rhe(cv, c)
    else:
        dibujar_factura_o_boleta(cv, c)
    cv.showPage()
    cv.save()


def generar_csv(ruta: Path):
    columnas = [
        "archivo",
        "tipo_comprobante",
        "serie_correlativo",
        "fecha_emision",
        "ruc_emisor",
        "razon_social_emisor",
        "ruc_receptor",
        "razon_social_receptor",
        "concepto",
        "moneda",
        "base_imponible",
        "igv",
        "total",
        "afectacion_igv",
        "medio_pago",
        "aplica_detraccion",
        "codigo_spot",
        "tasa_detraccion",
        "monto_detraccion",
        "cuenta_gasto_pcge",
        "notas",
    ]
    with ruta.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for c in COMPROBANTES:
            fila = {
                **c,
                "ruc_receptor": RECEPTOR_RUC,
                "razon_social_receptor": RECEPTOR_RAZON,
                "monto_detraccion": monto_detraccion(c),
            }
            writer.writerow({k: fila.get(k, "") for k in columnas})


def main():
    base = Path(__file__).parent
    dir_pdfs = base / "compras"
    dir_pdfs.mkdir(exist_ok=True)

    for c in COMPROBANTES:
        generar_pdf(dir_pdfs / c["archivo"], c)

    generar_csv(base / "compras_ground_truth.csv")
    print(f"{len(COMPROBANTES)} comprobantes generados en {dir_pdfs}")
    print(f"CSV de referencia: {base / 'compras_ground_truth.csv'}")


if __name__ == "__main__":
    main()
