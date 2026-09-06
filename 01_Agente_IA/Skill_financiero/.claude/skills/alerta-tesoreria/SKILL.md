---
name: alerta-tesoreria
description: >
  Reglas para determinar si una cuenta bancaria requiere accion urgente.
  Cargar cuando la tarea sea: revisar saldos, alertas, hay liquidez,
  cual cuenta esta critica, o despues de ejecutar el forecast.
---

# Politica de Alertas de Tesoreria

## Inputs necesarios

Vienen del output de `batch_dias_de_caja.py` o `rolling_mean_cashflow.py`:

```json
{
  "cuenta_id":     "CUENTA-001",
  "saldo_actual":   356608.41,
  "saldo_minimo":   50000,
  "dias_de_caja":   45.2,
  "flujo_neto_dia": 1968.91,
  "confidence":     0.85,
  "flags":          []
}
```

## Niveles de alerta (evaluar en este orden)

| Nivel | Condicion | Accion inmediata |
|---|---|---|
| **CRITICO** | `saldo_actual < saldo_minimo` | Notificar gerencia. Bloquear pagos no criticos. Activar linea de credito. |
| **ALTO** | `dias_de_caja < 7` | Transferencia urgente entre cuentas. Revisar pagos de la semana. |
| **MEDIO** | `dias_de_caja < 14` | Revisar egresos programados. Confirmar fondeos pendientes. |
| **OK** | `dias_de_caja >= 14` Y `saldo_actual >= saldo_minimo` | Sin accion requerida. |

## Formula de dias_de_caja

```
Si flujo_neto_dia < 0:
    dias_de_caja = saldo_actual / abs(flujo_neto_dia)
Si flujo_neto_dia >= 0:
    dias_de_caja = 999  (flujo positivo, sin limite en ventana actual)
```

**Importante:** `dias_de_caja = 999` no significa que la cuenta este perfecta,
significa que en los ultimos 14 dias los ingresos superaron a los egresos.
Puede haber pagos programados grandes que cambien esto — consultar el calendario de pagos.

## Regla de confidence

Si `confidence < 0.60` (historial insuficiente o datos anomalos):
- **No recomendar accion automatica** sobre esa cuenta.
- Incluir en el reporte con nivel `REVISAR` y los flags como contexto.
- El tesorero debe revisar manualmente.

## Output esperado por cuenta

```json
{
  "cuenta_id":          "CUENTA-001",
  "nivel_alerta":        "OK",
  "accion_recomendada": "Sin accion requerida",
  "prioridad":           4
}
```

Prioridades para ordenar el reporte: CRITICO=1, ALTO=2, MEDIO=3, OK=4, REVISAR=0.

## Cuando NO usar este skill

- Para medidas DAX de Power BI (usar dax-tesoreria)
- Para analisis de cuentas por cobrar o pagar (son dominios distintos)
- Para decisiones de inversion del excedente (requiere criterio del CFO)