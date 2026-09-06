#!/usr/bin/env python3
"""
Generador de medidas DAX de tesoreria adaptadas a las columnas reales de un Excel.

Flujo de uso (2 fases):
  Fase 1 - INSPECCIONAR:
      python generar_dax.py inspeccionar <archivo.xlsx>
    -> imprime las hojas, sus columnas, y un MAPEO SUGERIDO (auto-detectado).
       Copia ese mapeo, corrigelo si hace falta, y guardalo como un .json.

  Fase 2 - GENERAR:
      python generar_dax.py generar <archivo.xlsx> <mapeo.json> <salida.md> [--una-moneda] [--dias 7 15 30]
    -> escribe el .md con todas las medidas ya con los nombres reales sustituidos.

La auto-deteccion solo SUGIERE. El usuario confirma el mapeo antes de generar,
porque un nombre de columna equivocado produce DAX que falla silenciosamente en
Power BI. Ver SKILL.md, "Reglas de oro".
"""
import sys
import json
import argparse

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl. Instala con: pip install openpyxl --break-system-packages")


# ---------------------------------------------------------------------------
# Diccionario de sinonimos para auto-deteccion (case-insensitive, por substring)
# Cada clave logica -> lista de fragmentos que suelen aparecer en columnas reales.
# ---------------------------------------------------------------------------
SINONIMOS_COL = {
    "importe":    ["importe", "monto", "valor", "amount", "importe_pago", "importepagar"],
    "tipo_mov":   ["tipo_movimiento", "tipo movimiento", "flujo", "tipo", "mov", "naturaleza"],
    "moneda":     ["moneda", "currency", "divisa"],
    "saldo":      ["saldo", "balance"],
    "fecha":      ["fecha", "date", "dia"],
    "categoria":  ["categoria", "categoría", "concepto", "rubro", "cuenta"],
    "banco":      ["banco", "bank", "entidad"],
}
SINONIMOS_HOJA = {
    "real":     ["real", "movimiento", "historico", "histórico", "flujo_real", "banco"],
    "proy":     ["proy", "proyect", "forecast", "futuro", "2026", "presupuesto"],
    "saldos":   ["saldo", "balance"],
    "tc":       ["tipo_cambio", "tipo cambio", "tc", "cambio", "fx"],
}


def _match(nombre, fragmentos):
    n = str(nombre).strip().lower()
    for f in fragmentos:
        if f in n:
            return True
    return False


def leer_columnas(ws):
    """Devuelve la primera fila (encabezados) de una hoja."""
    for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
        return [c for c in row if c is not None]
    return []


def inspeccionar(ruta):
    wb = openpyxl.load_workbook(ruta, read_only=True)
    print(f"\n=== Archivo: {ruta} ===\n")

    info_hojas = {}
    for nombre in wb.sheetnames:
        cols = leer_columnas(wb[nombre])
        info_hojas[nombre] = cols
        print(f"Hoja '{nombre}': {cols}")

    # Auto-detectar hojas
    def detectar_hoja(clave):
        for h in wb.sheetnames:
            if _match(h, SINONIMOS_HOJA[clave]):
                return h
        return None

    hoja_real = detectar_hoja("real")
    hoja_proy = detectar_hoja("proy")
    hoja_saldos = detectar_hoja("saldos")
    hoja_tc = detectar_hoja("tc")

    # Auto-detectar columnas dentro de la hoja real (la mas representativa)
    cols_ref = info_hojas.get(hoja_real, [])
    def detectar_col(clave):
        for c in cols_ref:
            if _match(c, SINONIMOS_COL[clave]):
                return c
        return None

    mapeo = {
        "tabla_real":   hoja_real or "REVISAR",
        "tabla_proy":   hoja_proy or "REVISAR",
        "tabla_saldos": hoja_saldos or "REVISAR",
        "tabla_tc":     hoja_tc or "REVISAR",
        "tabla_fecha":  "Fecha",           # tabla calendario: casi siempre se crea en Power BI
        "tabla_selector": "Selector Moneda",
        "col_importe":  detectar_col("importe") or "REVISAR",
        "col_tipo_mov": detectar_col("tipo_mov") or "REVISAR",
        "col_moneda":   detectar_col("moneda") or "REVISAR",
        "col_saldo":    detectar_col("saldo") or "REVISAR",
        "col_fecha":    detectar_col("fecha") or "REVISAR",
        "col_fecha_calendario": "Date",
        "val_ingreso":  "INGRESO",
        "val_egreso":   "EGRESO",
        "val_pen":      "PEN",
        "val_usd":      "USD",
        "egresos_negativos": True,
    }

    print("\n=== MAPEO SUGERIDO (revisa los 'REVISAR' y corrige) ===")
    print(json.dumps(mapeo, indent=2, ensure_ascii=False))
    print("\nGuarda esto como mapeo.json, corrigelo, y luego corre:")
    print(f"  python generar_dax.py generar '{ruta}' mapeo.json salida.md")


# ---------------------------------------------------------------------------
# Generacion del .md a partir del mapeo confirmado
# ---------------------------------------------------------------------------
def q(tabla):
    """Pone comillas simples a nombres de tabla con espacios, como exige DAX."""
    return f"'{tabla}'" if (" " in tabla and not tabla.startswith("'")) else tabla


def generar(ruta_xlsx, ruta_mapeo, salida, una_moneda=False, dias=(7, 15, 30)):
    with open(ruta_mapeo, encoding="utf-8") as f:
        m = json.load(f)

    R = q(m["tabla_real"]); P = q(m["tabla_proy"]); S = q(m["tabla_saldos"])
    TC = q(m["tabla_tc"]); F = q(m["tabla_fecha"]); SEL = q(m["tabla_selector"])
    imp, tm, mon, sal = m["col_importe"], m["col_tipo_mov"], m["col_moneda"], m["col_saldo"]
    fc, fcal = m["col_fecha"], m["col_fecha_calendario"]
    vin, veg, vpen, vusd = m["val_ingreso"], m["val_egreso"], m["val_pen"], m["val_usd"]
    signo = "+" if m.get("egresos_negativos", True) else "-"

    out = []
    w = out.append

    w(f"# Medidas DAX — Dashboard Tesorería\n")
    w(f"Generado automáticamente desde `{ruta_xlsx}`. Modo: "
      f"{'UNA MONEDA' if una_moneda else 'MULTI-MONEDA PEN/USD'}.\n")

    w("\n## 1. Medidas base (flujo real)\n")
    w("```dax")
    w(f'Total Ingresos = CALCULATE ( SUM ( {R}[{imp}] ), {R}[{tm}] = "{vin}" )')
    w(f'Total Egresos  = CALCULATE ( SUM ( {R}[{imp}] ), {R}[{tm}] = "{veg}" )')
    w(f'Flujo Neto = [Total Ingresos] {signo} [Total Egresos]')
    w(f'Saldo Final = CALCULATE ( SUM ( {R}[{sal}] ), LASTNONBLANK ( {R}[{fc}], CALCULATE ( SUM ( {R}[{sal}] ) ) ) )')
    w(f'Flujo Acumulado = CALCULATE ( [Flujo Neto], FILTER ( ALL ( {F}[{fcal}] ), {F}[{fcal}] <= MAX ( {F}[{fcal}] ) ) )')
    w("```")

    w("\n## 2. Medidas proyectadas\n")
    w("```dax")
    w(f'Ingresos Proyectados = CALCULATE ( SUM ( {P}[{imp}] ), {P}[{tm}] = "{vin}" )')
    w(f'Egresos Proyectados  = CALCULATE ( SUM ( {P}[{imp}] ), {P}[{tm}] = "{veg}" )')
    w(f'Flujo Neto Proyectado = [Ingresos Proyectados] {signo} [Egresos Proyectados]')
    w("```")

    if not una_moneda:
        w("\n## 3. Multi-moneda PEN/USD\n")
        w("```dax")
        w(f'Moneda Seleccionada = SELECTEDVALUE ( {SEL}[Moneda], "{vpen}" )')
        w(f'TC Aplicado =')
        w(f'VAR _ult = CALCULATE ( MAX ( {TC}[Fecha] ), ALL ( {TC} ) )')
        w(f'VAR _compra = CALCULATE ( MAX ( {TC}[TC - COMPRA] ), ALL ( {TC} ), {TC}[Fecha] = _ult )')
        w(f'VAR _venta  = CALCULATE ( MAX ( {TC}[TC - VENTA] ),  ALL ( {TC} ), {TC}[Fecha] = _ult )')
        w(f'RETURN DIVIDE ( _compra + _venta, 2 )')
        w("")
        for etq, filtro in [("Ingresos", vin), ("Egresos", veg)]:
            w(f'{etq} x Moneda =')
            w(f'VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]')
            w(f'VAR _pen = CALCULATE ( SUM ( {R}[{imp}] ), {R}[{tm}] = "{filtro}", {R}[{mon}] = "{vpen}" )')
            w(f'VAR _usd = CALCULATE ( SUM ( {R}[{imp}] ), {R}[{tm}] = "{filtro}", {R}[{mon}] = "{vusd}" )')
            w(f'RETURN IF ( _m = "{vusd}", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )')
            w("")
        w(f'Flujo Neto x Moneda = [Ingresos x Moneda] {signo} [Egresos x Moneda]')
        w("```")

    w("\n## 4. Vencimientos (alertas de pago)\n")
    w("```dax")
    for n in dias:
        w(f'Pagos {n} dias =')
        if una_moneda:
            w(f'VAR _hoy = TODAY () VAR _hasta = _hoy + {n}')
            w(f'RETURN ABS ( CALCULATE ( SUM ( {P}[{imp}] ), {P}[{tm}] = "{veg}", {P}[{fc}] >= _hoy, {P}[{fc}] <= _hasta ) )')
        else:
            w(f'VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]')
            w(f'VAR _hoy = TODAY () VAR _hasta = _hoy + {n}')
            w(f'VAR _pen = CALCULATE ( SUM ( {P}[{imp}] ), {P}[{tm}] = "{veg}", {P}[{mon}] = "{vpen}", {P}[{fc}] >= _hoy, {P}[{fc}] <= _hasta )')
            w(f'VAR _usd = CALCULATE ( SUM ( {P}[{imp}] ), {P}[{tm}] = "{veg}", {P}[{mon}] = "{vusd}", {P}[{fc}] >= _hoy, {P}[{fc}] <= _hasta )')
            w(f'RETURN ABS ( IF ( _m = "{vusd}", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc ) )')
        w("")
    w("```")

    w("\n## 5. Saldos\n")
    w("```dax")
    if una_moneda:
        w(f'Saldo Base Actual =')
        w(f'VAR _ultFecha = CALCULATE ( MAX ( {S}[{fc}] ), ALL ( {S} ) )')
        w(f'RETURN CALCULATE ( SUM ( {S}[{sal}] ), {S}[{fc}] = _ultFecha, REMOVEFILTERS ( {F} ) )')
    else:
        w(f'Saldo Base Actual =')
        w(f'VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]')
        w(f'VAR _ultFecha = CALCULATE ( MAX ( {S}[Fecha] ), ALL ( {S} ) )')
        w(f'VAR _pen = CALCULATE ( SUM ( {S}[Saldo Soles] ),   {S}[Fecha] = _ultFecha, REMOVEFILTERS ( {F} ) )')
        w(f'VAR _usd = CALCULATE ( SUM ( {S}[Saldo Dólares] ), {S}[Fecha] = _ultFecha, REMOVEFILTERS ( {F} ) )')
        w(f'RETURN IF ( _m = "{vusd}", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )')
    w("```")

    w("\n## Orden de creación sugerido")
    w("1. Conectar Excel y verificar tipos en Power Query.")
    w("2. Crear tabla `_Medidas` vacía.")
    if not una_moneda:
        w("3. Crear `Moneda Seleccionada` y `TC Aplicado` primero (todo depende de ellas).")
    w("4. Medidas base → proyectadas → x moneda → vencimientos → saldos.")
    w("5. Visuales: KPI cards → flujo → donut categorías → barras por mes → tabla detalle.")

    texto = "\n".join(out) + "\n"
    with open(salida, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"OK: medidas escritas en {salida}")
    print(f"Modo: {'una moneda' if una_moneda else 'multi-moneda'} | vencimientos: {list(dias)}")


def main():
    ap = argparse.ArgumentParser(description="Generador de medidas DAX de tesoreria")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_i = sub.add_parser("inspeccionar", help="Inspecciona el Excel y sugiere un mapeo")
    p_i.add_argument("xlsx")

    p_g = sub.add_parser("generar", help="Genera el .md de medidas")
    p_g.add_argument("xlsx")
    p_g.add_argument("mapeo")
    p_g.add_argument("salida")
    p_g.add_argument("--una-moneda", action="store_true", help="Proyecto de una sola moneda")
    p_g.add_argument("--dias", nargs="+", type=int, default=[7, 15, 30],
                     help="Horizontes de vencimiento (default 7 15 30)")

    args = ap.parse_args()
    if args.cmd == "inspeccionar":
        inspeccionar(args.xlsx)
    else:
        generar(args.xlsx, args.mapeo, args.salida,
                una_moneda=args.una_moneda, dias=tuple(args.dias))


if __name__ == "__main__":
    main()
