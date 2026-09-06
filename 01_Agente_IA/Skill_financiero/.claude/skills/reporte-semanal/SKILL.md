---
name: reporte-semanal-tesoreria
description: >
  Estructura del reporte semanal de flujo de caja y alertas.
  Cargar cuando pidan: reporte semanal, resumen de tesoreria, informe del lunes,
  como estamos en caja, posicion consolidada.
---

# Reporte Semanal de Tesoreria

## Regla principal (del workshop)

Genera el reporte ejecutando UN script Python. No hagas tool calls individuales por cuenta.
El CSV puede tener meses de historial — un script lo procesa todo en una sola llamada.

```bash
python .claude/skills/reporte-semanal/generar_reporte.py
```

Ese script ya integra el forecast + las alertas + la posicion consolidada.

## Cadencia

| Cadencia | Trigger | Contenido |
|---|---|---|
| **Lunes** | reporte semanal, informe del lunes | Posicion completa: alertas + forecast + pagos criticos semana |
| **Diario** | revision diaria, el sweep, como estamos | Solo cuentas con alerta CRITICO o ALTO |
| **Ad hoc** | cualquier otra pregunta | Scope a lo que pidieron |

Si no se especifica, inferir por contexto. Default: reporte semanal completo.

## Estructura del reporte semanal (markdown)

```
# Reporte de Tesoreria — Semana del {{fecha}}

## Resumen Ejecutivo
{{N}} cuentas revisadas | {{N_alertas}} requieren atencion | Posicion total: S/ XX,XXX

## Cuentas en Alerta
| Cuenta | Banco | Moneda | Saldo actual | Minimo | Dias de caja | Nivel | Accion |
(solo cuentas con nivel CRITICO, ALTO o MEDIO)

## Cuentas OK
| Cuenta | Banco | Moneda | Saldo actual | Dias de caja | Forecast 14d |

## Posicion Consolidada
| Moneda | Saldo total | Variacion semana |

## Pagos Criticos Esta Semana
(cuando haya datos de pagos programados — pendiente de implementar)

## Notas del Agente
Observaciones relevantes del periodo (tendencias, anomalias, recomendaciones).
```

## Cuando usar el script vs generar a mano

- **Siempre usa el script** para el reporte completo — tiene toda la logica integrada.
- **Genera a mano** solo si el usuario pide una cuenta especifica o un dato puntual.
  En ese caso, ejecuta solo `rolling_mean_cashflow.py` para esa cuenta.

## Importante: dias_de_caja = 999

No significa que la cuenta sea perfecta. Significa que en los ultimos 14 dias
los ingresos superaron a los egresos. Mencionarlo como 'flujo positivo esta semana'
y recomendar revisar el calendario de pagos proximos.