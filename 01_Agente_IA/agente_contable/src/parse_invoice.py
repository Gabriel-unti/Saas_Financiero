"""
Extractor generico de comprobantes de compra en PDF -> dict de campos base.

Adapta el patron de extraccion con pdfplumber ya usado en produccion
(Tesoreria Braidy Wonders) pero desacoplado de una sola empresa: no asume
un receptor fijo ni un layout de una sola fuente. Funciona por regex sobre
el texto plano extraido, no por posicion fija de lineas, para tolerar
variacion de formato entre emisores reales.

Regla clave heredada del pipeline real: un RHE (Recibo por Honorarios
Electronico) no lleva IGV. Nunca derivar Valor_Venta como Total/1.18
cuando no hay IGV -- eso generaria un credito fiscal inexistente.
"""

import re
from pathlib import Path

import pdfplumber

RE_RUC = re.compile(r"RUC:\s*(\d{11})")
RE_SERIE = re.compile(r"\b([A-Z]\d{3,4}-\d{4,8})\b")
RE_FECHA = re.compile(r"Fecha de Emision:\s*(\d{2}/\d{2}/\d{4})")
RE_MONEDA = re.compile(r"Moneda:\s*(\w+)")
RE_VALOR_VENTA = re.compile(r"Valor Venta:\s*([\d,]+\.\d{2})")
RE_IGV = re.compile(r"IGV \(18%\):\s*([\d,]+\.\d{2})")
RE_TOTAL_FB = re.compile(r"Importe Total:\s*([\d,]+\.\d{2})")
RE_MONTO_BRUTO = re.compile(r"Monto Bruto:\s*([\d,]+\.\d{2})")
RE_TOTAL_RHE = re.compile(r"^Total:\s*([\d,]+\.\d{2})", re.MULTILINE)
RE_MEDIO_PAGO = re.compile(r"Forma de Pago:\s*(.+)")
RE_CONCEPTO_RHE = re.compile(r"Por concepto de:\s*(.+)")
RE_ETIQUETA_FB = re.compile(r"(FACTURA ELECTRONICA|BOLETA DE VENTA ELECTRONICA)")
RE_DETRACCION = re.compile(
    r"Sujeto a detraccion:\s*SI\s*-\s*Codigo\s*(\S+)\s*-\s*Tasa\s*(\d+)%"
)
RE_MONTO_DETRACCION = re.compile(r"Monto de detraccion:\s*S/\s*([\d,]+\.\d{2})")
RE_SPOT_BAJO_UMBRAL = re.compile(r"Codigo SPOT (\S+) presente")


def _num(match) -> float | None:
    if match is None:
        return None
    return float(match.group(1).replace(",", ""))


def parse_invoice(pdf_path: str | Path) -> dict:
    """Extrae los campos base de un comprobante de compra (PDF) a un dict.

    Campos devueltos: archivo_origen, tipo_comprobante, serie_correlativo,
    fecha_emision, ruc_emisor, razon_social_emisor, ruc_receptor, concepto,
    moneda, base_imponible, igv, total, medio_pago, aplica_detraccion,
    codigo_spot, tasa_detraccion, monto_detraccion.

    Un campo que no se pudo leer del PDF se marca "NO_VISIBLE" (o None
    para numericos) en vez de inventarse -- regla ya validada en el
    pipeline real de Tesoreria.
    """
    pdf_path = Path(pdf_path)
    with pdfplumber.open(pdf_path) as pdf:
        texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)

    lineas = [l.strip() for l in texto.splitlines() if l.strip()]

    es_rhe = "RECIBO POR HONORARIOS ELECTRONICO" in texto
    es_boleta = "BOLETA DE VENTA ELECTRONICA" in texto
    es_factura = "FACTURA ELECTRONICA" in texto

    if es_rhe:
        tipo_comprobante = "RHE"
    elif es_boleta:
        tipo_comprobante = "boleta"
    elif es_factura:
        tipo_comprobante = "factura"
    else:
        tipo_comprobante = "NO_VISIBLE"

    rucs = RE_RUC.findall(texto)
    ruc_emisor = rucs[0] if len(rucs) > 0 else "NO_VISIBLE"
    ruc_receptor = rucs[1] if len(rucs) > 1 else "NO_VISIBLE"

    serie_match = RE_SERIE.search(texto)
    serie_correlativo = serie_match.group(1) if serie_match else "NO_VISIBLE"

    fecha_match = RE_FECHA.search(texto)
    fecha_emision = fecha_match.group(1) if fecha_match else "NO_VISIBLE"

    moneda_match = RE_MONEDA.search(texto)
    moneda = moneda_match.group(1) if moneda_match else "PEN"

    medio_pago_match = RE_MEDIO_PAGO.search(texto)
    medio_pago = medio_pago_match.group(1).strip() if medio_pago_match else "NO_VISIBLE"

    if es_rhe:
        razon_social_emisor = lineas[2] if len(lineas) > 2 else "NO_VISIBLE"

        concepto_match = RE_CONCEPTO_RHE.search(texto)
        concepto = concepto_match.group(1).strip() if concepto_match else "NO_VISIBLE"

        base_imponible = _num(RE_MONTO_BRUTO.search(texto))
        total = _num(RE_TOTAL_RHE.search(texto))
        if base_imponible is None:
            base_imponible = total
        igv = 0.00
    else:
        etiqueta_match = RE_ETIQUETA_FB.search(texto)
        if etiqueta_match and lineas:
            razon_social_emisor = lineas[0].split(etiqueta_match.group(1))[0].strip()
        else:
            razon_social_emisor = "NO_VISIBLE"

        base_imponible = _num(RE_VALOR_VENTA.search(texto))
        igv = _num(RE_IGV.search(texto))
        if igv is None:
            igv = 0.00
        total = _num(RE_TOTAL_FB.search(texto))

        concepto = "NO_VISIBLE"
        idx_desc = next((i for i, l in enumerate(lineas) if l.startswith("Descripcion")), None)
        if idx_desc is not None and idx_desc + 1 < len(lineas):
            candidata = lineas[idx_desc + 1]
            if base_imponible is not None:
                candidata = candidata.replace(f"{base_imponible:.2f}", "").strip()
            concepto = candidata

    detraccion_match = RE_DETRACCION.search(texto)
    spot_bajo_umbral_match = RE_SPOT_BAJO_UMBRAL.search(texto)
    if detraccion_match:
        aplica_detraccion = "si"
        codigo_spot = detraccion_match.group(1)
        tasa_detraccion = int(detraccion_match.group(2)) / 100
        monto_detraccion = _num(RE_MONTO_DETRACCION.search(texto))
        if monto_detraccion is None:
            monto_detraccion = 0.00
    elif spot_bajo_umbral_match:
        aplica_detraccion = "no"
        codigo_spot = spot_bajo_umbral_match.group(1)
        tasa_detraccion = ""
        monto_detraccion = 0.00
    else:
        aplica_detraccion = "no"
        codigo_spot = ""
        tasa_detraccion = ""
        monto_detraccion = 0.00

    return dict(
        archivo_origen=pdf_path.name,
        tipo_comprobante=tipo_comprobante,
        serie_correlativo=serie_correlativo,
        fecha_emision=fecha_emision,
        ruc_emisor=ruc_emisor,
        razon_social_emisor=razon_social_emisor,
        ruc_receptor=ruc_receptor,
        concepto=concepto,
        moneda=moneda,
        base_imponible=base_imponible,
        igv=igv,
        total=total,
        medio_pago=medio_pago,
        aplica_detraccion=aplica_detraccion,
        codigo_spot=codigo_spot,
        tasa_detraccion=tasa_detraccion,
        monto_detraccion=monto_detraccion,
    )
