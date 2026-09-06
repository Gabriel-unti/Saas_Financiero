#!/usr/bin/env python3
"""
Genera el reporte semanal de tesoreria en markdown.
Integra: forecast de caja + alertas + posicion consolidada.

Uso:    python generar_reporte.py
Output: markdown del reporte (stdout) o archivo .md
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
from datetime import date

DATA        = Path(__file__).parent.parent.parent.parent / "data" / "movimientos_diarios.csv"
FECHA_HOY   = date.today().strftime("%d-%b-%Y")

# Saldos minimos operativos (configurar por cliente)
SALDO_MINIMO = {"CUENTA-001": 50_000, "CUENTA-002": 10_000, "CUENTA-003": 5_000}
NOMBRES      = {"CUENTA-001": "BCP", "CUENTA-002": "BBVA", "CUENTA-003": "Interbank"}

# ── Cargar y agrupar historial ────────────────────────────────────────────
historial = defaultdict(list)
for r in csv.DictReader(open(DATA)):
    historial[r["cuenta_id"]].append({
        "saldo_cierre": float(r["saldo_cierre"]),
        "ingresos_dia": float(r["ingresos_dia"]),
        "egresos_dia":  float(r["egresos_dia"]),
        "moneda":        r["moneda"],
    })

# ── Calcular forecast y alerta por cuenta ────────────────────────────────
cuentas = []
for cuenta_id, registros in historial.items():
    saldos   = [r["saldo_cierre"] for r in registros]
    ingresos = [r["ingresos_dia"]  for r in registros]
    egresos  = [r["egresos_dia"]   for r in registros]
    moneda   = registros[0]["moneda"]

    flujos      = [i - e for i, e in zip(ingresos[-14:], egresos[-14:])]
    flujo_dia   = sum(flujos) / max(len(flujos), 1)
    saldo_act   = saldos[-1]
    saldo_ant   = saldos[-8] if len(saldos) >= 8 else saldos[0]  # hace 7 dias
    variacion   = saldo_act - saldo_ant
    forecast    = round(saldo_act + flujo_dia * 14, 2)
    dias_caja   = round(saldo_act / abs(flujo_dia), 1) if flujo_dia < 0 else 999
    confidence  = 0.85 if len(saldos) >= 14 else 0.60
    saldo_min   = SALDO_MINIMO.get(cuenta_id, 0)

    # Nivel de alerta
    if confidence < 0.60:
        nivel, prioridad = "REVISAR", 0
        accion = "Historial insuficiente"
    elif saldo_act < saldo_min:
        nivel, prioridad = "CRITICO", 1
        accion = "Notificar gerencia. Activar linea de credito."
    elif dias_caja < 7:
        nivel, prioridad = "ALTO", 2
        accion = "Transferencia urgente. Revisar pagos semana."
    elif dias_caja < 14:
        nivel, prioridad = "MEDIO", 3
        accion = "Revisar egresos programados."
    else:
        nivel, prioridad = "OK", 4
        accion = "Sin accion requerida"

    cuentas.append({
        "cuenta_id": cuenta_id, "banco": NOMBRES.get(cuenta_id, "-"),
        "moneda": moneda, "saldo_actual": saldo_act, "saldo_anterior": saldo_ant,
        "variacion": variacion, "saldo_minimo": saldo_min,
        "dias_de_caja": dias_caja, "flujo_dia": flujo_dia, "forecast_14d": forecast,
        "nivel_alerta": nivel, "accion": accion, "prioridad": prioridad,
    })

cuentas.sort(key=lambda x: x["prioridad"])

# ── Posicion consolidada por moneda ──────────────────────────────────────
pos_pen = sum(c["saldo_actual"] for c in cuentas if c["moneda"] == "PEN")
pos_usd = sum(c["saldo_actual"] for c in cuentas if c["moneda"] == "USD")

n_alertas = sum(1 for c in cuentas if c["prioridad"] <= 3)

# ── Generar markdown ─────────────────────────────────────────────────────
md = []
md.append(f"# Reporte de Tesoreria — Semana del {FECHA_HOY}")
md.append("")
md.append("## Resumen Ejecutivo")
md.append(f"- **Cuentas revisadas:** {len(cuentas)}")
md.append(f"- **Requieren atencion:** {n_alertas}")
md.append(f"- **Posicion PEN:** S/ {pos_pen:,.2f}")
md.append(f"- **Posicion USD:** USD {pos_usd:,.2f}")
md.append("")

# Cuentas en alerta
alertas = [c for c in cuentas if c["prioridad"] <= 3]
if alertas:
    md.append("## Cuentas en Alerta")
    md.append("| Cuenta | Banco | Moneda | Saldo actual | Minimo | Dias de caja | Nivel | Accion |")
    md.append("|---|---|---|---|---|---|---|---|")
    for c in alertas:
        dias_str = str(c["dias_de_caja"]) if c["dias_de_caja"] < 999 else "flujo+"
        md.append(f"| {c['cuenta_id']} | {c['banco']} | {c['moneda']} | "
                  f"{c['moneda']} {c['saldo_actual']:>12,.0f} | "
                  f"{c['saldo_minimo']:>10,.0f} | "
                  f"{dias_str} | **{c['nivel_alerta']}** | {c['accion']} |")
    md.append("")

# Cuentas OK
ok = [c for c in cuentas if c["prioridad"] > 3]
if ok:
    md.append("## Cuentas OK")
    md.append("| Cuenta | Banco | Moneda | Saldo actual | Variacion 7d | Forecast 14d |")
    md.append("|---|---|---|---|---|---|")
    for c in ok:
        var_str = f"+{c['variacion']:,.0f}" if c["variacion"] >= 0 else f"{c['variacion']:,.0f}"
        md.append(f"| {c['cuenta_id']} | {c['banco']} | {c['moneda']} | "
                  f"{c['moneda']} {c['saldo_actual']:>12,.0f} | "
                  f"{var_str} | {c['moneda']} {c['forecast_14d']:>12,.0f} |")
    md.append("")

# Posicion consolidada
md.append("## Posicion Consolidada")
md.append("| Moneda | Saldo total |")
md.append("|---|---|")
md.append(f"| PEN | S/ {pos_pen:,.2f} |")
md.append(f"| USD | USD {pos_usd:,.2f} |")
md.append("")

# Notas del agente
md.append("## Notas del Agente")
notas = []
for c in cuentas:
    if c["dias_de_caja"] == 999:
        notas.append(f"- {c['cuenta_id']}: flujo neto positivo esta semana ({c['moneda']} {c['flujo_dia']:+,.0f}/dia). Revisar pagos proximos.")
if not notas:
    notas = ["- Sin observaciones adicionales."]
md.extend(notas)

print(chr(10).join(md))