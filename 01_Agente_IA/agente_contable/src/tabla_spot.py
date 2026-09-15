"""
Tabla de referencia del Sistema de Pago de Obligaciones Tributarias (SPOT /
detracciones) -- Anexo III (servicios) y Anexo IV (transporte de bienes por
via terrestre) de la RS N 183-2004/SUNAT y modificatorias.

Fuente: https://orientacion.sunat.gob.pe/apendices-del-sistema-de-detracciones
(consultada 2026-09-15). Numeral, descripcion, tasa vigente y base legal
verificados contra el texto de esa pagina. El codigo de 3 digitos (el que
imprime el comprobante electronico, Catalogo N 27 de SUNAT) esta confirmado
para el 026 contra una factura real (RIGAL LIMOUSINE PERU S.A.C. - E001-1359,
samples/reales) -- el resto de codigos de 3 digitos viene de la misma pagina
de orientacion pero NO fue verificado de forma independiente contra el texto
legal completo: usar con precaucion frente a un cliente real (verificado=False).

El umbral general del Anexo III es S/700 por comprobante (operaciones que no
lo superen no estan sujetas a detraccion, aunque el codigo si figure en la
lista). El Anexo IV (transporte de bienes por via terrestre) es un regimen
aparte con su propio umbral y codigo, que no se pudo verificar todavia.
"""

SPOT_ANEXO_III = [
    dict(
        numeral=1,
        codigo="012",
        descripcion="Intermediacion laboral y tercerizacion",
        tasa=0.12,
        vigente_desde="2018-04-01",
        cuenta_gasto_pcge="639",
        base_legal="RS 183-2004/SUNAT, modif. RS 071-2018/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=2,
        codigo="019",
        descripcion="Arrendamiento de bienes",
        tasa=0.10,
        vigente_desde="2004-01-01",
        cuenta_gasto_pcge="635",
        base_legal="RS 183-2004/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=3,
        codigo="020",
        descripcion="Mantenimiento y reparacion de bienes muebles",
        tasa=0.12,
        vigente_desde="2018-04-01",
        cuenta_gasto_pcge="634",
        base_legal="RS 183-2004/SUNAT, modif. RS 071-2018/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=4,
        codigo="021",
        descripcion="Movimiento de carga",
        tasa=0.10,
        vigente_desde="2004-01-01",
        cuenta_gasto_pcge="631",
        base_legal="RS 183-2004/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=5,
        codigo="022",
        descripcion="Otros servicios empresariales",
        tasa=0.12,
        vigente_desde="2018-04-01",
        cuenta_gasto_pcge="639",
        base_legal="RS 183-2004/SUNAT, modif. RS 071-2018/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=6,
        codigo="024",
        descripcion="Comision mercantil",
        tasa=0.10,
        vigente_desde="2004-01-01",
        cuenta_gasto_pcge="639",
        base_legal="RS 183-2004/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=7,
        codigo="025",
        descripcion="Fabricacion de bienes por encargo",
        tasa=0.10,
        vigente_desde="2004-01-01",
        cuenta_gasto_pcge="633",
        base_legal="RS 183-2004/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=8,
        codigo="026",
        descripcion="Servicio de transporte de personas",
        tasa=0.10,
        vigente_desde="2004-01-01",
        cuenta_gasto_pcge="631",
        base_legal="RS 183-2004/SUNAT",
        verificado=True,
        notas="Codigo y tasa confirmados contra factura real (RIGAL LIMOUSINE "
        "PERU S.A.C. - E001-1359, emitida 25/08/2026).",
    ),
    dict(
        numeral=9,
        codigo="030",
        descripcion="Contratos de construccion",
        tasa=0.04,
        vigente_desde="2013-11-01",
        cuenta_gasto_pcge="639",
        base_legal="RS 183-2004/SUNAT, modif. RS 265-2013/SUNAT",
        verificado=False,
    ),
    dict(
        numeral=10,
        codigo="037",
        descripcion="Demas servicios gravados con el IGV",
        tasa=0.12,
        vigente_desde="2018-04-01",
        cuenta_gasto_pcge="639",
        base_legal="RS 183-2004/SUNAT, modif. RS 071-2018/SUNAT",
        verificado=False,
    ),
]

# Regimen aparte del Anexo III -- transporte de bienes (carga) por via
# terrestre. NO usar el codigo 026 (transporte de PERSONAS) para este caso,
# error que tenia el set sintetico original.
SPOT_ANEXO_IV_TRANSPORTE_BIENES = dict(
    descripcion="Transporte de bienes realizado por via terrestre",
    tasa=0.04,
    umbral_operacion=400.00,
    cuenta_gasto_pcge="631",
    base_legal="RS 073-2006/SUNAT",
    verificado=False,
    notas="Codigo de 3 digitos y vigencia del umbral pendientes de confirmar "
    "contra el Catalogo 27 de SUNAT -- no usar frente a un cliente real sin "
    "verificar.",
)

UMBRAL_GENERAL_ANEXO_III = 700.00


def buscar_por_codigo(codigo: str) -> dict | None:
    for fila in SPOT_ANEXO_III:
        if fila["codigo"] == codigo:
            return fila
    return None


def aplica_detraccion(codigo: str, importe_total: float) -> bool:
    """Anexo III: aplica si el codigo esta en la tabla y el importe total
    del comprobante supera el umbral general de S/700, sin importar la
    moneda del comprobante (regla simplificada del MVP)."""
    fila = buscar_por_codigo(codigo)
    if fila is None:
        return False
    return importe_total > UMBRAL_GENERAL_ANEXO_III


def calcular_monto_detraccion(codigo: str, importe_total: float) -> float:
    if not aplica_detraccion(codigo, importe_total):
        return 0.0
    fila = buscar_por_codigo(codigo)
    return round(importe_total * fila["tasa"], 2)
