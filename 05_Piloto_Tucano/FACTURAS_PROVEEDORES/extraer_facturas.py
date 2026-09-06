# -*- coding: utf-8 -*-
"""
Extrae datos de facturas/recibos PDF de proveedores (Tucano Peru / Braidy Wonders SAC)
y los vuelca en un Excel de STAGING (borrador) para revision manual antes de pasarlos
al archivo maestro Facturas_Proveedores.xlsx.

USO:
    python extraer_facturas.py "C:\\ruta\\a\\carpeta_con_pdfs" [--out salida.xlsx]

No modifica el archivo maestro. Genera un .xlsx nuevo con las mismas columnas que
Tabla1, mas dos columnas de control (Archivo_Origen, Revisar) para que la persona
que revisa sepa de donde salio cada fila y que tan segura es la extraccion.

Filosofia: mejor dejar un campo en blanco y marcado "REVISAR" que inventar un valor.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pdfplumber
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
MESES_ABREV = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12,
}

COLUMNAS = [
    "File", "Tipo", "Tipo_Comprobante", "N°_Comprobante", "FechaEmision",
    "RUC", "Proveedor", "Moneda", "Importe", "Detracción", "Neto",
    "FechaVcto", "Estado", "Detalle",
    "Archivo_Origen", "Revisar",
]


def limpiar_monto(texto):
    """'1,234.56' o '1.234,56' -> 1234.56 (float). Devuelve None si no matchea."""
    if texto is None:
        return None
    t = texto.strip().replace(" ", "")
    t = t.replace(",", "")
    try:
        return round(float(t), 2)
    except ValueError:
        return None


def parsear_fecha_dmy(texto):
    """DD/MM/YYYY -> datetime.date"""
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def parsear_fecha_texto_largo(dia, mes_nombre, anio):
    """'24' 'Julio' '2026' -> date, usando diccionario de meses en espanol."""
    mes = MESES.get(mes_nombre.strip().lower())
    if not mes:
        return None
    try:
        return datetime(int(anio), mes, int(dia)).date()
    except ValueError:
        return None


def parsear_fecha_abrev(texto):
    """'10-ago-2026' -> date"""
    m = re.match(r"(\d{1,2})[-/](\w{3})[-/](\d{4})", texto.strip().lower())
    if not m:
        return None
    dia, mes_abr, anio = m.groups()
    mes = MESES_ABREV.get(mes_abr)
    if not mes:
        return None
    try:
        return datetime(int(anio), mes, int(dia)).date()
    except ValueError:
        return None


_TILDES = str.maketrans("ÁÉÍÓÚáéíóúÑñ", "AEIOUaeiouNn")


def sin_tildes(texto):
    """Quita tildes para poder detectar encabezados sin importar si el PDF los trae o no."""
    return texto.translate(_TILDES)


def extraer_texto(pdf_path):
    texto_paginas = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            texto_paginas.append(t)
    return "\n".join(texto_paginas)


def nuevo_registro(archivo):
    return {col: None for col in COLUMNAS} | {
        "Archivo_Origen": archivo.name,
        "Tipo": "PROVEEDOR",
        "Revisar": "",
    }


def marcar_revisar(reg, motivo):
    actual = reg.get("Revisar") or ""
    reg["Revisar"] = (actual + "; " + motivo).strip("; ")


# ---------------------------------------------------------------------------
# Parser 1: Recibo por Honorarios Electronico (RHE)
# ---------------------------------------------------------------------------

def es_rhe(texto):
    return "RECIBO POR HONORARIOS ELECTRONICO" in sin_tildes(texto.upper())


def parsear_rhe(texto, archivo):
    reg = nuevo_registro(archivo)
    reg["Tipo_Comprobante"] = "RHE"

    m = re.search(r"R\.?U\.?C\.?\s*[:\.]?\s*(\d{11})", texto)
    if m:
        reg["RUC"] = m.group(1)
    else:
        marcar_revisar(reg, "no se encontro RUC del emisor")

    m = re.search(r"Nro\.?\s*[:.]?\s*(E\d{3}\s*-?\s*\d+)", texto)
    if m:
        reg["N°_Comprobante"] = re.sub(r"\s+", " ", m.group(1)).strip()
    else:
        marcar_revisar(reg, "no se encontro numero de comprobante")

    # Nombre del proveedor: en el RHE (segun pdfplumber) siempre es la primera
    # linea del texto, justo antes de la linea "R.U.C. <numero>".
    m = re.search(r"^\s*(.+?)\s*\nR\.?U\.?C\.?\s*\d{11}", texto)
    if m:
        reg["Proveedor"] = m.group(1).strip()
    else:
        marcar_revisar(reg, "no se pudo identificar el nombre del proveedor, revisar manualmente")

    m = re.search(r"Fecha de emisi[oó]n\D{0,15}(\d{1,2})\s+de\s+(\w+)\s+del?\s*(\d{4})", texto, re.IGNORECASE)
    if m:
        f = parsear_fecha_texto_largo(*m.groups())
        if f:
            reg["FechaEmision"] = f
    if not reg["FechaEmision"]:
        marcar_revisar(reg, "no se encontro fecha de emision")

    m = re.search(r"Total por [Hh]onorarios:?\s*([\d,]+\.\d{2})", texto)
    importe = limpiar_monto(m.group(1)) if m else None

    m = re.search(r"Retenci[oó]n\s*\(\s*8\s*%\)\s*IR:?\s*\(?([\d,]+\.\d{2})\)?", texto)
    retencion = limpiar_monto(m.group(1)) if m else None

    m = re.search(r"Total Neto Recibido:?\s*([\d,]+\.\d{2})", texto)
    neto = limpiar_monto(m.group(1)) if m else None

    if importe is None and neto is not None:
        importe = neto
    if importe is not None:
        reg["Importe"] = importe
    else:
        marcar_revisar(reg, "no se encontro el importe (Total por honorarios)")

    if neto is not None:
        reg["Neto"] = neto
    elif importe is not None:
        reg["Neto"] = importe

    if retencion:
        reg["Detracción"] = retencion
        marcar_revisar(reg, "tiene RETENCION IR (no detraccion) cargada en col. Detraccion - confirmar criterio antes de pasar al maestro")

    if "SOLES" in texto.upper():
        reg["Moneda"] = "PEN"
    elif "DOLARES" in texto.upper() or "DÓLARES" in texto.upper():
        reg["Moneda"] = "USD"
    else:
        marcar_revisar(reg, "no se identifico la moneda")

    # File: buscar patron FILE seguido de digitos, en el concepto/observacion
    m = re.search(r"FILE\s*:?\s*(\d{6,10})", texto, re.IGNORECASE)
    if m:
        reg["File"] = m.group(1)

    # Vencimiento: si es al credito, buscar la fecha de la cuota (formato YYYY-MM-DD)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", texto)
    if m:
        try:
            reg["FechaVcto"] = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
        except ValueError:
            pass
    if not reg["FechaVcto"]:
        reg["FechaVcto"] = reg["FechaEmision"]

    # Concepto / detalle
    m = re.search(r"Por concepto de\s*(.+?)(?:\n\s*Observaci[oó]n|\n\s*Inciso)", texto, re.DOTALL | re.IGNORECASE)
    if m:
        detalle = re.sub(r"\s+", " ", m.group(1)).strip()
        m2 = re.search(r"Observaci[oó]n\s*(.+?)\n\s*Inciso", texto, re.DOTALL | re.IGNORECASE)
        if m2:
            obs = re.sub(r"\s+", " ", m2.group(1)).strip(" -")
            if obs:
                detalle = f"{detalle} ({obs})"
        reg["Detalle"] = detalle
    else:
        marcar_revisar(reg, "no se pudo extraer el detalle/concepto")

    return reg


# ---------------------------------------------------------------------------
# Parser 2: Factura Electronica "estilo SUNAT" (PDF-DOC-*, 1807/1847-style, etc.)
#   Cubre: Camping Tours, Arcobaleno, ETT House Tours, Transportes Laser,
#   Inversiones Fenix Tours, Cusco Aventuras Transtours, Peruvian... (parcial), etc.
# ---------------------------------------------------------------------------

def es_factura_sunat_generica(texto):
    t = sin_tildes(texto.upper())
    return "FACTURA ELECTRONICA" in t and "SUNAT" in t


SUFIJOS_EMPRESA = ("S.A.C", "E.I.R.L", "S.R.L", "S.A.", "SOCIEDAD", "SAC", "EIRL", "SRL", "LTDA")


def extraer_proveedor_por_sufijo(texto):
    """Busca la primera linea que 'suena' a razon social (S.A.C., E.I.R.L., SOCIEDAD...)
    que no sea el cliente (BRAIDY WONDERS SAC). Mas confiable que asumir una posicion
    fija, porque el orden en que pdfplumber extrae las cajas de texto varia mucho
    entre plantillas de distintos proveedores."""
    for linea in texto.splitlines():
        l = linea.strip()
        if not l or "BRAIDY WONDERS" in l.upper():
            continue
        if any(suf in l.upper() for suf in SUFIJOS_EMPRESA):
            return l
    return None


def parsear_factura_sunat_generica(texto, archivo):
    reg = nuevo_registro(archivo)
    reg["Tipo_Comprobante"] = "FACTURA"

    m = re.search(r"RUC:\s*(\d{11})", texto)
    if m:
        reg["RUC"] = m.group(1)
    else:
        marcar_revisar(reg, "no se encontro RUC del emisor")

    m = re.search(r"\b([EF]\d{3}\s*-\s*\d{2,8})\b", texto)
    if m:
        reg["N°_Comprobante"] = re.sub(r"\s+", "", m.group(1))
    else:
        marcar_revisar(reg, "no se encontro numero de comprobante")

    proveedor = extraer_proveedor_por_sufijo(texto)
    if proveedor:
        reg["Proveedor"] = proveedor
    else:
        marcar_revisar(reg, "no se pudo identificar el proveedor por razon social, revisar manualmente")

    m = re.search(r"Fecha de Emisi[oó]n\s*:?\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
    if m:
        reg["FechaEmision"] = parsear_fecha_dmy(m.group(1))
    else:
        marcar_revisar(reg, "no se encontro fecha de emision")

    t_upper = sin_tildes(texto.upper())
    if "DOLAR" in t_upper:
        reg["Moneda"] = "USD"
    elif "SOLES" in t_upper:
        reg["Moneda"] = "PEN"
    else:
        marcar_revisar(reg, "no se identifico la moneda")

    m = re.search(r"Importe Total\s*:?\s*[\$S/]*\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    importe = limpiar_monto(m.group(1)) if m else None
    if importe is not None:
        reg["Importe"] = importe
    else:
        marcar_revisar(reg, "no se encontro Importe Total")

    m = re.search(r"Monto neto pendiente de pago\s*:?\s*[\$S/]*\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    neto = limpiar_monto(m.group(1)) if m else None
    if neto is None:
        neto = importe
    reg["Neto"] = neto

    if importe is not None and neto is not None:
        det = round(importe - neto, 2)
        if det > 0.005:
            reg["Detracción"] = det
        m_det_pdf = re.search(r"Monto detracci[oó]n:\s*S/\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
        if m_det_pdf and det <= 0.005:
            marcar_revisar(reg, f"PDF indica detraccion S/{m_det_pdf.group(1)} pero el neto no la refleja (posible inconsistencia, igual que casos vistos antes)")

    m = re.search(r"FILE\s*:?\s*(\d{6,10})", texto, re.IGNORECASE)
    if m:
        reg["File"] = m.group(1)

    m = re.search(r"Fec\.?\s*Venc\.?\s*Monto\s*\n?\s*\d+\s+(\d{2}/\d{2}/\d{4})", texto)
    if m:
        reg["FechaVcto"] = parsear_fecha_dmy(m.group(1))
    else:
        reg["FechaVcto"] = reg["FechaEmision"]

    m = re.search(r"Descripci[oó]n\s*Valor Unitario.*?\n(.+?)(?:Valor de Venta de Operaciones Gratuitas|Sub Total)", texto, re.DOTALL)
    if m:
        detalle = re.sub(r"\s+", " ", m.group(1)).strip()
        detalle = re.sub(r"\d+\.\d{2}\s+\d+\.\d{2}(?=\s|$)", "", detalle)  # recorta columnas de precio pegadas
        reg["Detalle"] = detalle[:500]
    else:
        marcar_revisar(reg, "no se pudo extraer el detalle de servicio")

    return reg


# ---------------------------------------------------------------------------
# Parser 3: Casa Andina / Nessus Hoteles (facturas de hospedaje)
# ---------------------------------------------------------------------------

def es_casa_andina(texto):
    # OJO: NO usar solo "CASA ANDINA" como señal - aparece como texto incidental
    # en facturas de OTROS proveedores (transportistas que describen traslados
    # "HTL CASA ANDINA..."). "NESSUS HOTELES" es el nombre de la razon social
    # emisora y no aparece salvo que la factura sea realmente de ellos.
    return "NESSUS HOTELES" in texto.upper()


def parsear_casa_andina(texto, archivo):
    reg = nuevo_registro(archivo)
    reg["Tipo_Comprobante"] = "FACTURA"
    reg["Proveedor"] = "NESSUS HOTELES PERU S.A. (CASA ANDINA)"

    m = re.search(r"R\.?U\.?C\.?\s*N?°?\s*(\d{11})", texto)
    if m:
        reg["RUC"] = m.group(1)
    else:
        marcar_revisar(reg, "no se encontro RUC del emisor")

    m = re.search(r"\b([EF]\d{3}\s*-\s*\d{2,8})\b", texto)
    if m:
        reg["N°_Comprobante"] = re.sub(r"\s+", "", m.group(1))
    else:
        marcar_revisar(reg, "no se encontro numero de comprobante")

    m = re.search(r"Fecha Emisi[oó]n\s*:?\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
    if m:
        reg["FechaEmision"] = parsear_fecha_dmy(m.group(1))
    else:
        marcar_revisar(reg, "no se encontro fecha de emision")

    t_upper = sin_tildes(texto.upper())
    if "DOLAR" in t_upper:
        reg["Moneda"] = "USD"
    elif "SOLES" in t_upper:
        reg["Moneda"] = "PEN"
    else:
        marcar_revisar(reg, "no se identifico la moneda")

    m = re.search(r"IMPORTE TOTAL\s*\$?\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        reg["Importe"] = limpiar_monto(m.group(1))
        reg["Neto"] = reg["Importe"]  # Casa Andina no aplica detraccion en estas facturas
    else:
        marcar_revisar(reg, "no se encontro Importe Total")

    m = re.search(r"Fecha de Pago\s*:?\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
    if m:
        reg["FechaVcto"] = parsear_fecha_dmy(m.group(1))
    else:
        reg["FechaVcto"] = reg["FechaEmision"]

    m = re.search(r"Hu[eé]sped\s*:?(\S.*?)\s*Grupo", texto, re.IGNORECASE)
    if m:
        huesped = m.group(1).strip()
    else:
        huesped = None
    m2 = re.search(r"Reserva\s*:?(\S+)", texto, re.IGNORECASE)
    reserva = m2.group(1).strip() if m2 else None
    partes = ["ALOJAMIENTO"]
    if huesped:
        partes.append(f"HUESPED {huesped}")
    if reserva:
        partes.append(f"RESERVA {reserva}")
    reg["Detalle"] = ", ".join(partes) if len(partes) > 1 else None
    if not reg["Detalle"]:
        marcar_revisar(reg, "no se pudo armar el detalle (huesped/reserva)")

    m = re.search(r"FILE\s*:?\s*(\d{6,10})", texto, re.IGNORECASE)
    if m:
        reg["File"] = m.group(1)

    return reg


# ---------------------------------------------------------------------------
# Parser 4: Peruvian Culture Travel (formato "efact.pe")
# ---------------------------------------------------------------------------

def es_peruvian_culture(texto):
    return "PERUVIAN CULTURE TRAVEL" in texto.upper()


def parsear_peruvian_culture(texto, archivo):
    reg = nuevo_registro(archivo)
    reg["Tipo_Comprobante"] = "FACTURA"
    reg["Proveedor"] = "PERUVIAN CULTURE TRAVEL AGENCIA DE VIAJES Y TURISMO S.R.L."

    m = re.search(r"RUC:\s*(\d{11})", texto)
    if m:
        reg["RUC"] = m.group(1)
    else:
        marcar_revisar(reg, "no se encontro RUC del emisor")

    m = re.search(r"\b(F\d{3}\s*-\s*\d{2,8})\b", texto)
    if m:
        reg["N°_Comprobante"] = re.sub(r"\s+", "", m.group(1))
    else:
        marcar_revisar(reg, "no se encontro numero de comprobante")

    m = re.search(r"(\d{1,2}-\w{3}-\d{4})", texto)
    if m:
        reg["FechaEmision"] = parsear_fecha_abrev(m.group(1))
    else:
        marcar_revisar(reg, "no se encontro fecha de emision")

    t_upper = sin_tildes(texto.upper())
    if "DOLAR" in t_upper or "US DOLARES" in t_upper:
        reg["Moneda"] = "USD"
    elif "SOLES" in t_upper:
        reg["Moneda"] = "PEN"
    else:
        marcar_revisar(reg, "no se identifico la moneda")

    # "TOTAL USD X" a secas es el importe total del comprobante. Cuidado: NO debe
    # confundirse con "SUB TOTAL USD X" (subtotal antes de IGV) que aparece antes
    # en el mismo documento - por eso el lookbehind negativo.
    m = re.search(r"(?<!SUB )(?<!SUB)TOTAL\s+(?:USD|S/\.?|PEN)\s+([\d,]+\.\d{2})", texto, re.IGNORECASE)
    importe = limpiar_monto(m.group(1)) if m else None
    if importe is not None:
        reg["Importe"] = importe
    else:
        marcar_revisar(reg, "no se encontro el Importe Total")

    m = re.search(r"Neto a Pagar\s*(?:USD|S/\.?|PEN)?\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    neto = limpiar_monto(m.group(1)) if m else None
    if neto is None:
        neto = importe
    reg["Neto"] = neto
    if importe is not None and neto is not None:
        det = round(importe - neto, 2)
        if det > 0.005:
            reg["Detracción"] = det

    # Contado en todas las facturas vistas de este proveedor -> vencimiento = emision
    reg["FechaVcto"] = reg["FechaEmision"]

    m = re.search(r"DESCRIPCI[OÓ]N\s*\n?(.+?)(?:OBSERVACIONES|OP\. GRAVADAS)", texto, re.DOTALL | re.IGNORECASE)
    if m:
        detalle = re.sub(r"\s+", " ", m.group(1)).strip()
        reg["Detalle"] = detalle[:500]
    else:
        marcar_revisar(reg, "no se pudo extraer el detalle de servicio")

    m = re.search(r"FILE\s*:?\s*(\d{6,10})", texto, re.IGNORECASE)
    if m:
        reg["File"] = m.group(1)

    return reg


# ---------------------------------------------------------------------------
# Fallback generico: no reconocimos la plantilla. Extraemos lo minimo posible
# (RUC, un monto candidato) y marcamos TODO para revision manual.
# ---------------------------------------------------------------------------

def parsear_generico(texto, archivo):
    reg = nuevo_registro(archivo)
    marcar_revisar(reg, "FORMATO NO RECONOCIDO - revisar manualmente todos los campos")

    m = re.search(r"RUC:?\s*N?°?\s*(\d{11})", texto)
    if m:
        reg["RUC"] = m.group(1)

    m = re.search(r"(?:Importe Total|Total a Pagar|TOTAL A PAGAR|Total Pagar)\s*:?\s*[\$S/.]*\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        reg["Importe"] = limpiar_monto(m.group(1))
        reg["Neto"] = reg["Importe"]

    m = re.search(r"\b([EF]\d{3}\s*-?\s*\d{2,8})\b", texto)
    if m:
        reg["N°_Comprobante"] = re.sub(r"\s+", "", m.group(1))

    if "DOLAR" in texto.upper() or "DÓLAR" in texto.upper() or "USD" in texto.upper() or "US$" in texto:
        reg["Moneda"] = "USD"
    elif "SOLES" in texto.upper() or "S/" in texto:
        reg["Moneda"] = "PEN"

    proveedor = extraer_proveedor_por_sufijo(texto)
    if proveedor:
        reg["Proveedor"] = proveedor
    else:
        primeras_lineas = [l.strip() for l in texto.splitlines() if l.strip()][:3]
        if primeras_lineas:
            reg["Proveedor"] = primeras_lineas[0]

    return reg


PARSERS = [
    (es_rhe, parsear_rhe),
    (es_casa_andina, parsear_casa_andina),
    (es_peruvian_culture, parsear_peruvian_culture),
    (es_factura_sunat_generica, parsear_factura_sunat_generica),
]


def procesar_pdf(pdf_path):
    archivo = Path(pdf_path)
    try:
        texto = extraer_texto(archivo)
    except Exception as e:
        reg = nuevo_registro(archivo)
        marcar_revisar(reg, f"ERROR AL ABRIR/LEER EL PDF: {e}")
        return reg

    if not texto.strip():
        reg = nuevo_registro(archivo)
        marcar_revisar(reg, "PDF sin texto extraible (posible escaneo/imagen) - revisar manualmente")
        return reg

    for detector, parser in PARSERS:
        if detector(texto):
            return parser(texto, archivo)

    return parsear_generico(texto, archivo)


def escribir_staging(registros, out_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Staging"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4472C4")
    revisar_fill = PatternFill("solid", fgColor="FFF2CC")

    for c, col in enumerate(COLUMNAS, start=1):
        cell = ws.cell(row=1, column=c, value=col)
        cell.font = header_font
        cell.fill = header_fill

    for r, reg in enumerate(registros, start=2):
        for c, col in enumerate(COLUMNAS, start=1):
            val = reg.get(col)
            cell = ws.cell(row=r, column=c, value=val)
            if col in ("FechaEmision", "FechaVcto") and val:
                cell.number_format = "d/mm/yyyy"
            if col in ("Importe", "Detracción", "Neto") and val is not None:
                cell.number_format = '#,##0.00'
        if reg.get("Revisar"):
            for c in range(1, len(COLUMNAS) + 1):
                ws.cell(row=r, column=c).fill = revisar_fill

    for c, col in enumerate(COLUMNAS, start=1):
        ws.column_dimensions[get_column_letter(c)].width = min(max(len(col) + 2, 12), 60)
    ws.column_dimensions[get_column_letter(COLUMNAS.index("Detalle") + 1)].width = 60
    ws.column_dimensions[get_column_letter(COLUMNAS.index("Revisar") + 1)].width = 50

    ws.freeze_panes = "A2"
    wb.save(out_path)


def main():
    ap = argparse.ArgumentParser(description="Extrae datos de facturas PDF a un Excel de staging")
    ap.add_argument("carpeta", help="Carpeta con los PDF a procesar")
    ap.add_argument("--out", default=None, help="Ruta del Excel de salida (por defecto: staging_<fecha>.xlsx en la misma carpeta)")
    args = ap.parse_args()

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"ERROR: '{carpeta}' no es una carpeta valida.", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(carpeta.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en '{carpeta}'.")
        sys.exit(0)

    out_path = Path(args.out) if args.out else carpeta / f"staging_{datetime.now():%Y%m%d_%H%M%S}.xlsx"

    registros = []
    n_ok, n_revisar = 0, 0
    for pdf in pdfs:
        print(f"Procesando: {pdf.name}")
        reg = procesar_pdf(pdf)
        registros.append(reg)
        if reg.get("Revisar"):
            n_revisar += 1
        else:
            n_ok += 1

    escribir_staging(registros, out_path)
    print(f"\nListo. {len(registros)} archivo(s) procesados -> {out_path}")
    print(f"  Sin marcas de revision: {n_ok}")
    print(f"  Con marcas de revision: {n_revisar} (filas resaltadas en amarillo)")
    print("\nIMPORTANTE: este archivo es un BORRADOR. Revisar cada fila (sobre todo las")
    print("resaltadas) antes de pasar los datos al archivo maestro Facturas_Proveedores.xlsx.")


if __name__ == "__main__":
    main()
