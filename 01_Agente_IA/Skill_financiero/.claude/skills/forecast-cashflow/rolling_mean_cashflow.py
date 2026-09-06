#!/usr/bin/env python3
# Adaptado de: cwc-workshops/agent-decomposition/.claude/skills/forecasting/rolling_mean.py
# Cambios: sku->cuenta_id, units_sold->saldo_cierre, agrega dias_de_caja
"""
Forecast de saldo de caja — rolling mean 14 dias.

Uso:    python rolling_mean_cashflow.py CUENTA-001 14
Output: JSON con {cuenta_id, forecast_saldo, dias_de_caja, confidence, method, flags}
"""
import csv, json, sys
from pathlib import Path

DATA = Path(__file__).parent.parent.parent.parent / "data" / "movimientos_diarios.csv"
cuenta_id = sys.argv[1]
horizon   = int(sys.argv[2]) if len(sys.argv) > 2 else 14

# Cargar historial de saldos para esa cuenta
rows = [r for r in csv.DictReader(open(DATA)) if r["cuenta_id"] == cuenta_id]
if not rows:
    print(json.dumps({"error": f"Cuenta {cuenta_id} no encontrada"}))
    sys.exit(1)

moneda  = rows[0]["moneda"]
saldos  = [float(r["saldo_cierre"]) for r in rows]
ingresos = [float(r["ingresos_dia"]) for r in rows]
egresos  = [float(r["egresos_dia"]) for r in rows]

# Rolling mean 14 dias (o todo el historial si hay menos)
recent_saldos  = saldos[-14:] if len(saldos) >= 14 else saldos
recent_flujo   = [i - e for i, e in zip(ingresos[-14:], egresos[-14:])]

mean_saldo     = sum(recent_saldos) / max(len(recent_saldos), 1)
mean_flujo_dia = sum(recent_flujo) / max(len(recent_flujo), 1)

# Dias de caja: cuantos dias aguanta al ritmo actual de egresos
# (solo tiene sentido si el flujo neto es negativo)
saldo_actual = saldos[-1]
if mean_flujo_dia < 0:
    dias_de_caja = round(saldo_actual / abs(mean_flujo_dia), 1)
else:
    dias_de_caja = 999  # flujo positivo: sin limite en ventana actual

# Forecast: proyectar el saldo al horizonte dado
forecast_saldo = round(saldo_actual + mean_flujo_dia * horizon, 2)

tiene_14d = len(saldos) >= 14
print(json.dumps({
    "cuenta_id":      cuenta_id,
    "moneda":          moneda,
    "saldo_actual":    round(saldo_actual, 2),
    "forecast_saldo":  forecast_saldo,
    "dias_de_caja":    dias_de_caja,
    "flujo_neto_dia":  round(mean_flujo_dia, 2),
    "horizon_dias":    horizon,
    "confidence":      0.85 if tiene_14d else 0.60,
    "method":          "rolling_mean_14d",
    "flags":           [] if tiene_14d else ["historial_insuficiente"],
}))