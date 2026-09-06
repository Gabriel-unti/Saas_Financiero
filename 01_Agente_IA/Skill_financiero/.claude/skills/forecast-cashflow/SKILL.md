---
name: forecast-cashflow
description: >
  Como calcular el forecast de saldo de caja para una cuenta bancaria.
  Cargar cuando la tarea involucre: forecast, proyeccion, dias de caja,
  cuanto saldo habra, cuantos dias aguanta, o revisar liquidez.
---

# Forecast de Saldo de Caja

Hay dos caminos. Elige el mas barato que da un resultado confiable.

## Path A — Calcular directamente (code execution)

Usar cuando TODOS se cumplen:
- horizonte <= 14 dias
- cuenta sin pagos criticos programados esta semana
- historial >= 14 dias disponible

Entonces es solo un rolling mean. El script ya esta escrito:

```bash
# Forecast individual
python .claude/skills/forecast-cashflow/rolling_mean_cashflow.py CUENTA-001 14

# Todas las cuentas rankeadas por urgencia (el preferido para revision diaria)
python .claude/skills/forecast-cashflow/batch_dias_de_caja.py
```

Una sola llamada Bash. No hagas un loop de tool calls — eso es el anti-patron.

## Path B — Delegar a subagente

Usar cuando CUALQUIERA se cumple:
- hay pagos programados criticos en los proximos 7 dias
- la cuenta es de tipo planilla o USD con exposicion cambiaria
- horizonte > 14 dias
- el historial tiene menos de 14 dias

Por que subagente: la cuenta puede tener eventos que el rolling mean no captura.
El subagente carga el historial completo en su propio contexto y lo analiza.

## Output del script (contrato estricto)

```json
{
  "cuenta_id":     "CUENTA-001",
  "moneda":         "PEN",
  "saldo_actual":   333500.00,
  "forecast_saldo": 340000.00,
  "dias_de_caja":   45.2,
  "flujo_neto_dia": 450.00,
  "horizon_dias":   14,
  "confidence":     0.85,
  "method":         "rolling_mean_14d",
  "flags":          []
}
```

Parsear el JSON estrictamente. Si es invalido, es un error — no adivinar.

## Que hacer con el resultado

Pasar `{dias_de_caja, saldo_actual, confidence, flags}` al skill `alerta-tesoreria`.

Regla critica: **si `confidence < 0.60`, no recomendar accion automatica.**
Escalar a revision humana con los flags como contexto.

## Niveles de confidence

| Valor | Significado | Accion |
|---|---|---|
| 0.85 | Historial suficiente (>=14d) | Proceder con el forecast |
| 0.60 | Historial corto (<14d) | Escalar a revision humana |
| < 0.60 | Error o datos anomalos | No actuar, reportar al usuario |