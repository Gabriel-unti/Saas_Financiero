"""
Ground truth RCE-alineado para las 11 facturas REALES de proveedores de
Braidy Wonders SAC agregadas en
02_Piloto_P5/Fuente_Original_Proyecto_contable/facturas_proveedores/.

A diferencia de samples/generar_comprobantes_compra.py (que genera PDFs
sinteticos), este script NO crea PDFs -- los comprobantes ya existen y son
reales. Solo transcribe a mano, campo por campo, lo que cada PDF dice
realmente, en la misma estructura de columnas (Campo1-37 RCE + CLU) que
el set sintetico, para poder validar el extractor de manana contra ambos
origenes con el mismo criterio.

Decision registrada: usar estos datos reales de Braidy Wonders es una
excepcion consciente a la regla general de "solo datos sinteticos" del
plan de 8 semanas (ver 03_Docs_Tecnicas/est-bien-me-parece-snappy-thacker.md,
decision #1), confirmada explicitamente por el usuario el 2026-09-14.

Uso: python generar_ground_truth_compras_reales.py
Salida: data/compras_reales_ground_truth.csv
"""

import csv
from pathlib import Path

RUTA_FACTURAS = "02_Piloto_P5/Fuente_Original_Proyecto_contable/facturas_proveedores"

RECEPTOR_RUC = "20605765417"
RECEPTOR_RAZON = "BRAIDY WONDERS SAC"

COLUMNAS_RCE = [
    ("campo01_ruc", "ruc"),
    ("campo02_razon_social_titular", "razon_social_titular"),
    ("campo03_periodo", "periodo"),
    ("campo04_car_sunat", "car_sunat"),
    ("campo05_fecha_emision", "fecha_emision"),
    ("campo06_fecha_vcto_pago", "fecha_vencimiento_pago"),
    ("campo07_tipo_cp", "tipo_cp"),
    ("campo08_serie_cdp", "serie_cdp"),
    ("campo09_anio", "anio"),
    ("campo10_nro_inicial", "nro_inicial"),
    ("campo11_nro_final", "nro_final"),
    ("campo12_tipo_doc_identidad", "tipo_doc_identidad_proveedor"),
    ("campo13_nro_doc_identidad", "nro_doc_identidad_proveedor"),
    ("campo14_razon_social_proveedor", "razon_social_proveedor"),
    ("campo15_bi_gravado_dg", "bi_gravado_dg"),
    ("campo16_igv_dg", "igv_dg"),
    ("campo17_bi_gravado_dgng", "bi_gravado_dgng"),
    ("campo18_igv_dgng", "igv_dgng"),
    ("campo19_bi_gravado_dng", "bi_gravado_dng"),
    ("campo20_igv_dng", "igv_dng"),
    ("campo21_valor_adq_ng", "valor_adq_ng"),
    ("campo22_isc", "isc"),
    ("campo23_icbper", "icbper"),
    ("campo24_otros_trib_cargos", "otros_trib_cargos"),
    ("campo25_total_cp", "total_cp"),
    ("campo26_moneda", "moneda"),
    ("campo27_tipo_cambio", "tipo_cambio"),
    ("campo33_clasif_bss_sss", "clasif_bss_sss"),
    ("campo37_car_orig", "car_orig"),
    ("clu1_aplica_detraccion", "clu1_aplica_detraccion"),
    ("clu2_codigo_spot", "clu2_codigo_spot"),
    ("clu3_tasa_detraccion", "clu3_tasa_detraccion"),
    ("clu4_monto_detraccion", "clu4_monto_detraccion"),
    ("clu5_cuenta_gasto_pcge", "clu5_cuenta_gasto_pcge"),
    ("clu6_archivo_origen", "clu6_archivo_origen"),
    ("clu7_notas", "clu7_notas"),
]

BASE = dict(
    ruc=RECEPTOR_RUC,
    razon_social_titular=RECEPTOR_RAZON,
    car_sunat="",
    tipo_doc_identidad_proveedor="6",
    bi_gravado_dgng=0.00,
    igv_dgng=0.00,
    bi_gravado_dng=0.00,
    igv_dng=0.00,
    isc=0.00,
    icbper=0.00,
    tipo_cambio="",
    clasif_bss_sss="",
    car_orig="",
)

FILAS = [
    dict(
        BASE,
        fecha_emision="03/09/2026",
        fecha_vencimiento_pago="03/09/2026",
        periodo="202609",
        tipo_cp="01",
        serie_cdp="F303",
        anio="",
        nro_inicial="00020682",
        nro_final="00020682",
        nro_doc_identidad_proveedor="20114803228",
        razon_social_proveedor="INVERSIONES NACIONALES DE TURISMO S.A.",
        bi_gravado_dg=584.53,
        igv_dg=105.22,
        valor_adq_ng=0.00,
        otros_trib_cargos=58.45,
        total_cp=748.20,
        moneda="USD",
        tipo_cambio=3.360,
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/20114803228-01-F303-00020682.pdf",
        clu7_notas="Pago a cuenta de alojamiento (no es el total del servicio). "
        "Recargo al consumo (R.CONS. 10%) de $58.45 va en Otros Trib/Cargos, no en IGV.",
    ),
    dict(
        BASE,
        fecha_emision="30/07/2026",
        fecha_vencimiento_pago="30/07/2026",
        periodo="202607",
        tipo_cp="01",
        serie_cdp="F011",
        anio="",
        nro_inicial="29848",
        nro_final="29848",
        nro_doc_identidad_proveedor="20442088811",
        razon_social_proveedor="ALBERGUE OLLANTAYTAMBO EIRL",
        bi_gravado_dg=440.63,
        igv_dg=79.31,
        valor_adq_ng=0.00,
        otros_trib_cargos=44.06,
        total_cp=564.00,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/ALBERGUE OLLANTAYTAMBO EIRL - F011-29848.pdf",
        clu7_notas="Otros Cargos 44.06 no identificados explicitamente en el PDF "
        "(probable propina/servicio).",
    ),
    dict(
        BASE,
        fecha_emision="02/09/2026",
        fecha_vencimiento_pago="02/09/2026",
        periodo="202609",
        tipo_cp="01",
        serie_cdp="F003",
        anio="",
        nro_inicial="00000044",
        nro_final="00000044",
        nro_doc_identidad_proveedor="20606383356",
        razon_social_proveedor="ALQA GALERIA DE EXPRESIONES ANDINAS SRL",
        bi_gravado_dg=488.69,
        igv_dg=51.31,
        valor_adq_ng=0.00,
        otros_trib_cargos=0.00,
        total_cp=540.00,
        moneda="PEN",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/ALQA GALERIA DE EXPRESIONES ANDINAS SRL - F003-00000044.pdf",
        clu7_notas="",
    ),
    dict(
        BASE,
        fecha_emision="28/08/2026",
        fecha_vencimiento_pago="28/08/2026",
        periodo="202608",
        tipo_cp="01",
        serie_cdp="FT21",
        anio="",
        nro_inicial="00005578",
        nro_final="00005578",
        nro_doc_identidad_proveedor="20513469129",
        razon_social_proveedor="ANDEAN EXPERIENCE S.A.C.",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=2037.09,
        otros_trib_cargos=203.71,
        total_cp=2240.80,
        moneda="USD",
        tipo_cambio=3.348,
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/ANDEAN EXPERIENCE S.A.C. - FT21-00005578.pdf",
        clu7_notas="Exportacion de servicios (IGV 0%, DL 919): el proveedor no cobra IGV, "
        "va a Valor Adq. NG, sin credito fiscal que reclamar.",
    ),
    dict(
        BASE,
        fecha_emision="07/09/2026",
        fecha_vencimiento_pago="07/09/2026",
        periodo="202609",
        tipo_cp="02",
        serie_cdp="E001",
        anio="",
        nro_inicial="123",
        nro_final="123",
        nro_doc_identidad_proveedor="10438198984",
        razon_social_proveedor="ANICAMA ZAMORA SAULO CHRIS",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=2500.00,
        otros_trib_cargos=0.00,
        total_cp=2500.00,
        moneda="PEN",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/ANICAMA ZAMORA SAULO CHRIS - E001-123.pdf",
        clu7_notas="RHE de S/2500 con 'Retencion (8%) IR: (0.00)': el emisor probablemente "
        "cuenta con certificado de suspension de retencion de 4ta categoria (SUNAT), lo que "
        "lo obliga a asumir directamente el pago de su impuesto en vez de que Braidy Wonders "
        "se lo retenga. El extractor debe leer el 0.00 impreso, no calcular 8% por defecto.",
    ),
    dict(
        BASE,
        fecha_emision="04/08/2026",
        fecha_vencimiento_pago="14/08/2026",
        periodo="202608",
        tipo_cp="02",
        serie_cdp="E001",
        anio="",
        nro_inicial="742",
        nro_final="742",
        nro_doc_identidad_proveedor="10214605606",
        razon_social_proveedor="CATACORA RAMIREZ PAUL FRED",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=400.00,
        otros_trib_cargos=0.00,
        total_cp=400.00,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/CATACORA RAMIREZ PAUL FRED - E001742.pdf",
        clu7_notas="Al credito, 1 cuota vence 14/08/2026. Retencion 8% IR mostrada como "
        "0.00, mismo caso que ANICAMA: probable certificado de suspension de retencion "
        "de 4ta categoria del emisor.",
    ),
    dict(
        BASE,
        fecha_emision="01/07/2026",
        fecha_vencimiento_pago="01/07/2026",
        periodo="202607",
        tipo_cp="01",
        serie_cdp="E001",
        anio="",
        nro_inicial="6498",
        nro_final="6498",
        nro_doc_identidad_proveedor="20527988331",
        razon_social_proveedor="GRUPO TOURBULENCIA EN PERU S.R.L.",
        bi_gravado_dg=1704.00,
        igv_dg=306.72,
        valor_adq_ng=0.00,
        otros_trib_cargos=0.00,
        total_cp=2010.72,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="si",
        clu2_codigo_spot="NO_VISIBLE",
        clu3_tasa_detraccion="NO_VISIBLE",
        clu4_monto_detraccion="NO_VISIBLE",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=(
            f"{RUTA_FACTURAS}/GRUPO TOURBULENCIA EN PERU S.R.L. (XTREME TOURBULENCIA) - E001-6498.pdf"
        ),
        clu7_notas="El PDF confirma 'OPERACION SUJETO A DETRACCION' pero no imprime codigo "
        "ni tasa ni monto -- esto es comun en PYMEs (no es un error del documento). El "
        "extractor no debe inventar el dato: debe clasificar el servicio por su descripcion "
        "(aqui: operacion de tour, candidato a numeral 10 'Demas servicios gravados con el "
        "IGV', codigo 037, 12% segun src/tabla_spot.py) y calcular el monto el mismo, en vez "
        "de depender de que el proveedor lo imprima.",
    ),
    dict(
        BASE,
        fecha_emision="20/08/2026",
        fecha_vencimiento_pago="20/08/2026",
        periodo="202608",
        tipo_cp="01",
        serie_cdp="F008",
        anio="",
        nro_inicial="00035739",
        nro_final="00035739",
        nro_doc_identidad_proveedor="20536047906",
        razon_social_proveedor="HOTELERIA PERUANA S.A.C.",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=138.18,
        otros_trib_cargos=13.82,
        total_cp=152.00,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/HOTELERIA PERUANA S.A.C. (TIERRA VIVA HOTELS) - F008-00035739.pdf",
        clu7_notas="Exportacion de servicios de hospedaje a no domiciliados (DL 919, IGV 0%), "
        "mismo patron que ANDEAN EXPERIENCE.",
    ),
    dict(
        BASE,
        fecha_emision="25/08/2026",
        fecha_vencimiento_pago="09/09/2026",
        periodo="202608",
        tipo_cp="01",
        serie_cdp="E001",
        anio="",
        nro_inicial="1359",
        nro_final="1359",
        nro_doc_identidad_proveedor="20433412860",
        razon_social_proveedor="RIGAL LIMOUSINE PERU S.A.C.",
        bi_gravado_dg=2240.00,
        igv_dg=403.20,
        valor_adq_ng=0.00,
        otros_trib_cargos=0.00,
        total_cp=2643.20,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="si",
        clu2_codigo_spot="026",
        clu3_tasa_detraccion=0.10,
        clu4_monto_detraccion=888.00,
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/RIGAL LIMOUSINE PERU S.A.C. - E001-1359.pdf",
        clu7_notas="Codigo 026 = Servicio de transporte de PERSONAS, tasa 10% -- confirmado "
        "contra este documento real y usado como fuente para src/tabla_spot.py (el set "
        "sintetico usaba 4% asumiendo 'transporte de carga', ya corregido: ese es un "
        "regimen aparte, Anexo IV). Monto de detraccion (S/888.00) esta en SOLES pese a que "
        "la factura es en USD: la detraccion siempre se deposita en moneda nacional.",
    ),
    dict(
        BASE,
        fecha_emision="20/05/2026",
        fecha_vencimiento_pago="20/05/2026",
        periodo="202605",
        tipo_cp="02",
        serie_cdp="E001",
        anio="",
        nro_inicial="411",
        nro_final="411",
        nro_doc_identidad_proveedor="10422800102",
        razon_social_proveedor="SARMIENTO LOPEZ LUIS RONALD",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=33.00,
        otros_trib_cargos=0.00,
        total_cp=33.00,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/SARMIENTO LOPEZ LUIS RONALD - E001-411.pdf",
        clu7_notas="Unico RHE del set real donde SI se aplico la retencion de 8% IR (2.64): "
        "a diferencia de ANICAMA y CATACORA, este emisor no tiene certificado de suspension "
        "de retencion de 4ta categoria, asi que Braidy Wonders SI debe retenerle el 8%. El "
        "extractor debe leer el monto de retencion impreso (no asumir 8% ni 0% por defecto: "
        "depende de si el emisor tiene o no el certificado vigente). "
        "Total Neto Recibido tras retencion: 30.36 (no usado aqui, el CP registra el bruto).",
    ),
    dict(
        BASE,
        fecha_emision="27/08/2026",
        fecha_vencimiento_pago="03/09/2026",
        periodo="202608",
        tipo_cp="01",
        serie_cdp="FELE",
        anio="",
        nro_inicial="11538",
        nro_final="11538",
        nro_doc_identidad_proveedor="20556034134",
        razon_social_proveedor="VILLA SAN BLAS S.A.C.",
        bi_gravado_dg=0.00,
        igv_dg=0.00,
        valor_adq_ng=316.36,
        otros_trib_cargos=31.64,
        total_cp=348.00,
        moneda="USD",
        tipo_cambio="",
        clu1_aplica_detraccion="no",
        clu2_codigo_spot="",
        clu3_tasa_detraccion="",
        clu4_monto_detraccion="",
        clu5_cuenta_gasto_pcge="",
        clu6_archivo_origen=f"{RUTA_FACTURAS}/VILLA SAN BLAS S.A.C (ANANAY HOTELS) - FELE-11538.pdf",
        clu7_notas="Exportacion de servicios de hospedaje (DL 919, IGV 0%), mismo patron que "
        "ANDEAN EXPERIENCE y HOTELERIA PERUANA. Servicios(10%) de $31.64 va en Otros Trib/Cargos.",
    ),
]


def generar_csv(ruta: Path):
    columnas = [nombre_columna for nombre_columna, _ in COLUMNAS_RCE]
    with ruta.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for fila in FILAS:
            writer.writerow(
                {nombre_columna: fila[clave_interna] for nombre_columna, clave_interna in COLUMNAS_RCE}
            )


def main():
    ruta = Path(__file__).parent / "compras_reales_ground_truth.csv"
    generar_csv(ruta)
    print(f"{len(FILAS)} filas escritas en {ruta}")


if __name__ == "__main__":
    main()
