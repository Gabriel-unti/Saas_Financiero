#!/usr/bin/env python3
# Adaptado de: cwc-workshops/agent-decomposition/.claude/skills/forecasting/batch_days_of_cover.py
"""
Dias de caja para TODAS las cuentas, rankeadas por urgencia.

Uso:    python batch_dias_de_caja.py [top_n]
Output: JSON array ordenado por dias_de_caja ascendente
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

DATA = Path(__file__).parent.parent.parent.parent / "data" / "movimientos_diarios.csv"
top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 20

# Saldos minimos operativos por cuenta (configurar por cliente)
SALDO_MINIMO = {"CUENTA-001": 50000, "CUENTA-002": 10000, "CUENTA-003": 5000}

# Agrupar historial por cuenta
historial = defaultdict(list)
for r in csv.DictReader(open(DATA)):
    historial[r["cuenta_id"]].append({
        "fecha":        r["fecha"],
        "saldo_cierre": float(r["saldo_cierre"]),
        "ingresos_dia": float(r["ingresos_dia"]),
        "egresos_dia":  float(r["egresos_dia"]),
        "moneda":        r["moneda"],
    })

rows = []
for cuenta_id, registros in historial.items():
    saldos   = [r["saldo_cierre"] for r in registros]
    ingresos = [r["ingresos_dia"]  for r in registros]
    egresos  = [r["egresos_dia"]   for r in registros]
    moneda   = registros[0]["moneda"]

    recent_flujo = [i - e for i, e in zip(ingresos[-14:], egresos[-14:])]
    mean_flujo   = sum(recent_flujo) / max(len(recent_flujo), 1)
    saldo_actual = saldos[-1]
    saldo_min    = SALDO_MINIMO.get(cuenta_id, 0)

    if mean_flujo < 0:
        dias_de_caja = round(saldo_actual / abs(mean_flujo), 1)
    else:
        dias_de_caja = 999

    rows.append({
        "cuenta_id":         cuenta_id,
        "moneda":             moneda,
        "saldo_actual":       round(saldo_actual, 2),
        "saldo_minimo":       saldo_min,
        "dias_de_caja":       dias_de_caja,
        "flujo_neto_dia":     round(mean_flujo, 2),
        "bajo_minimo":        saldo_actual < saldo_min,
        "requiere_atencion":  dias_de_caja < 14 or saldo_actual < saldo_min,
        "confidence":         0.85 if len(saldos) >= 14 else 0.60,
    })

rows.sort(key=lambda r: r["dias_de_caja"])
print(json.dumps(rows[:top_n], indent=2))