# 🏦 Skill Financiero — Agente de Tesorería con Claude API
**Gabriel Untiveros | Skill_financiero | Lima, Perú**
**Iniciado:** 2026-05-25 | **Horizonte:** Semanas 1–2 (hasta 7-jun-2026)

---

## 🎯 Objetivo de este proyecto

Construir las **3 piezas fundamentales** del Agente de Tesorería (Capa 1 de la arquitectura final), adaptando los patrones del workshop `agent-decomposition` de Anthropic CWC 2026 al dominio de tesorería corporativa.

Este proyecto es el punto de partida de **Financial Pulse**, el producto SaaS de análisis financiero para PYMEs.

---

## 📁 Estructura del proyecto

```
Skill_financiero/
│
├── PROYECTO.md                          ← Este archivo (instrucciones)
│
├── data/
│   └── movimientos_diarios.csv          ← Dataset simulado (creado en NB 01)
│
├── .claude/
│   └── skills/
│       ├── forecast-cashflow/
│       │   ├── SKILL.md                 ← Política de decisión de forecast
│       │   └── rolling_mean_cashflow.py ← Script ejecutable (Path A)
│       ├── alerta-tesoreria/
│       │   └── SKILL.md                 ← Reglas de alerta por nivel
│       └── reporte-semanal/
│           └── SKILL.md                 ← Estructura del reporte semanal
│
├── 01_datos_simulados.ipynb             ← Crear dataset de movimientos
├── 02_cashflow_forecast.ipynb           ← Adaptar rolling_mean.py → tesorería
├── 03_skills_tesoreria.ipynb            ← Crear y validar los 3 SKILLs
└── 04_loop_agentico.ipynb               ← Implementar el loop base (Messages API)
```

---

## 📓 Notebooks — Descripción y Orden de Ejecución

### `01_datos_simulados.ipynb` — Dataset de Movimientos Diarios
**Propósito:** Crear el CSV de entrada que usan todos los scripts siguientes.  
**Input:** Ninguno (datos sintéticos generados con `numpy`/`pandas`)  
**Output:** `data/movimientos_diarios.csv`  

Campos del CSV:
| Campo | Tipo | Descripción |
|---|---|---|
| `cuenta_id` | str | ID de cuenta bancaria (ej: `CUENTA-001`) |
| `fecha` | date | Fecha del movimiento (`YYYY-MM-DD`) |
| `saldo_cierre` | float | Saldo al cierre del día (soles) |
| `ingresos_dia` | float | Ingresos totales del día |
| `egresos_dia` | float | Egresos totales del día |
| `moneda` | str | `PEN` o `USD` |

Escenarios a simular (al menos 3 cuentas con comportamientos distintos):
- `CUENTA-001`: Cuenta operativa principal, flujo estable
- `CUENTA-002`: Cuenta con pagos de planilla (pico de egresos quincenales)
- `CUENTA-003`: Cuenta USD, con exposición a tipo de cambio

---

### `02_cashflow_forecast.ipynb` — Forecast de Saldo de Caja
**Propósito:** Adaptar `rolling_mean.py` del workshop al dominio de tesorería. Implementar Path A (forecast propio) y Path B (cuándo delegar a subagente).  
**Input:** `data/movimientos_diarios.csv`  
**Output:** JSON con `{cuenta_id, forecast_saldo, dias_de_caja, confidence, method, flags}`  

Referencia del workshop:
```
cwc-workshops-main/cwc-workshops-main/agent-decomposition/
  .claude/skills/forecasting/rolling_mean.py
  .claude/skills/forecasting/batch_days_of_cover.py
```

Adaptaciones clave vs. el original:
| Workshop (inventario) | Este proyecto (tesorería) |
|---|---|
| `sku` | `cuenta_id` |
| `units_sold` | `saldo_cierre` |
| `forecast_qty` (unidades) | `forecast_saldo` (soles/USD) |
| `days_of_cover` | `dias_de_caja` |
| Path B: es_estacional | Path B: es_cuenta_critica o pagos_programados |

---

### `03_skills_tesoreria.ipynb` — Los 3 SKILLs de Tesorería
**Propósito:** Crear los 3 archivos SKILL.md y verificar que son coherentes entre sí (el output de uno es el input del siguiente).  
**Input:** Resultado del forecast del NB 02  
**Output:** 3 archivos SKILL.md en `.claude/skills/`  

Los 3 skills y su relación:
```
forecast-cashflow/SKILL.md
       ↓ produce: {forecast_saldo, dias_de_caja, confidence, flags}
       
alerta-tesoreria/SKILL.md
       ↓ consume: {dias_de_caja, saldo_minimo_operativo}
       ↓ produce: {nivel_alerta, accion_recomendada}
       
reporte-semanal/SKILL.md
       ↓ consume: alerts + forecasts de todas las cuentas
       ↓ produce: markdown del reporte ejecutivo
```

---

### `04_loop_agentico.ipynb` — Loop Agentico Base (Messages API)
**Propósito:** Implementar el patrón `while turns < max_turns` usando la Anthropic SDK directamente (sin frameworks). Este es el corazón del agente.  
**Input:** Prompt del usuario + tools definidos  
**Output:** Respuesta del agente + transcript + métricas (tokens, turns)  

Referencia del workshop:
```
cwc-workshops-main/cwc-workshops-main/agent-decomposition/
  agents/before/stockpilot.py   ← patrón base a adaptar
```

Tools a implementar en el loop:
| Tool | Descripción |
|---|---|
| `get_saldo_cuenta` | Retorna saldo actual de una cuenta |
| `run_forecast` | Ejecuta `rolling_mean_cashflow.py` para una cuenta |
| `run_batch_forecast` | Forecast de todas las cuentas en un solo script |
| `get_pagos_programados` | Pagos críticos de la semana |
| `generar_reporte_semanal` | Ejecuta el script de reporte completo |

---

## ⚙️ Setup del entorno

### Requerimientos
```
python >= 3.10
anthropic >= 0.50
pandas >= 2.0
numpy >= 1.24
jupyter
python-dotenv
```

### Variables de entorno
Crea un archivo `.env` en `Skill_financiero/` con:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Instalación
```bash
pip install anthropic pandas numpy jupyter python-dotenv
```

---

## 🧠 Principio de diseño (del workshop)

> **Antes de escribir cualquier código de agente, preguntarse:**
>
> | ¿Qué tipo de tarea? | Solución |
> |---|---|
> | Puntual y determinista | TOOL CALL simple |
> | Política / regla de negocio | SKILL (.md) |
> | Cargar mucho contexto de golpe | CODE EXECUTION (script Python) |
> | Complejidad propia + contexto propio | SUBAGENTE |
> | Recordar entre sesiones | MEMORY STORE (Fase 2) |

El anti-patrón a evitar: hacer 100 tool calls individuales cuando un solo script Python resuelve lo mismo en 1 call.

---

## 📊 Criterios de éxito (Semana 1–2)

- [ ] Dataset de 90 días generado para 3 cuentas (NB 01)
- [ ] `rolling_mean_cashflow.py` ejecuta y retorna JSON válido (NB 02)
- [ ] Batch forecast de 3 cuentas en una sola ejecución (NB 02)
- [ ] Los 3 SKILL.md creados con contratos de I/O bien definidos (NB 03)
- [ ] Loop agentico responde a "¿qué cuenta tiene menos días de caja?" (NB 04)
- [ ] Loop agentico genera reporte semanal en markdown (NB 04)

---

## 🔗 Referencias

| Recurso | Ruta |
|---|---|
| Workshop fuente | `D:\Proyecto_Gabriel\cwc-workshops-main\cwc-workshops-main\agent-decomposition\` |
| rolling_mean.py original | `.claude/skills/forecasting/rolling_mean.py` |
| stockpilot.py (loop base) | `agents/before/stockpilot.py` |
| Guía de aplicación completa | `D:\Proyecto_Gabriel\cwc-workshops-main\APLICACION_A_MI_PROYECTO.md` |
| Docs Anthropic SDK | https://docs.anthropic.com/en/api/getting-started |
| Modelos Claude | https://docs.anthropic.com/en/docs/about-claude/models |

---

> **Nota de arquitectura:** Este proyecto es la **Capa 1 (Skills)** y parte de la **Capa 2 (Code Execution)** de la arquitectura de 4 capas del Agente Financiero. Las Capas 3 (Subagentes) y 4 (Memory Store) se construyen en la fase siguiente (Semana 3–4, `agents-that-remember/`).
