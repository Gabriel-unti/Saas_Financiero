# 🚀 CWC Workshops — Guía de Aplicación al Proyecto Personal
**Gabriel Untiveros | Consultoría Financiero-Digital | Lima, Perú**

> Este archivo es tu hoja de ruta personal para extraer valor concreto de los workshops de Anthropic y aplicarlos a tus proyectos activos de negocio independiente. No es un resumen — es un plan de ejecución.

---

## 📦 ¿Qué son estos workshops?

Materiales del evento **Code with Claude 2026** de Anthropic. Son proyectos funcionales que demuestran los patrones más avanzados de construcción con Claude Managed Agents. Licencia Apache 2.0 → puedes reutilizar el código en tus proyectos comerciales.

---

## 🗺️ Mapa: Workshop → Tu Proyecto

| Workshop | Carpeta | Relevancia | Prioridad |
|---|---|---|---|
| Compose Multi-Agent Systems | `agent-decomposition/` | Skills financieros, forecast de cash flow, reportes de tesorería | 🔴 ALTA |
| Agents That Remember | `agents-that-remember/` | Agente consultor con memoria de clientes | 🔴 ALTA |
| Production-Ready Agent (Deal Desk) | `production-ready-agent/` | Producto SaaS multi-agente para análisis financiero | 🟡 MEDIA-ALTA |
| Eval-Driven Agent Development | `eval-driven-agent-development/` | Evaluar y mejorar tu modelo de Churn (Proyecto 3) | 🟡 MEDIA |
| Picking the Right Model | `rightmodel/` | Optimizar costo de API en producción | 🟢 CUANDO ESCALES |
| How We Claude Code | `how-we-claude-code/` | Metodología de producto con clientes | 🟢 SIEMPRE |

---

## 🔴 PRIORIDAD 1 — `agent-decomposition/` → Tu Agente de Tesorería

### ¿Qué tiene este workshop?

Un agente de gestión de inventario con:
- **Skills cargados bajo demanda** (no en el prompt siempre)
- **Code execution** en vez de múltiples tool calls
- **Subagentes** solo cuando hay complejidad real
- Resultado: de 402 líneas de prompt monolítico a 15 líneas + skills modulares

### ¿Por qué te importa?

La arquitectura de inventario es un **espejo exacto** de tesorería:

| Inventario (workshop) | Tesorería (tu caso) |
|---|---|
| Stock por SKU | Saldo por cuenta bancaria |
| Punto de reorden | Saldo mínimo operativo |
| Días de cobertura | Días de caja disponibles |
| Proveedor / lead time | Fuente de liquidez / tiempo de gestión |
| Reporte semanal de inventario | Reporte semanal de flujo de caja |
| Alerta de stock crítico | Alerta de saldo bajo |
| Forecast de demanda | Forecast de egresos/ingresos |

### 📁 Archivos clave a estudiar

```
agent-decomposition/
├── .claude/skills/
│   ├── forecasting/
│   │   ├── SKILL.md              ← Leer primero: patrón de decisión
│   │   ├── rolling_mean.py       ← Adaptar a cashflow_forecast.py
│   │   └── batch_days_of_cover.py ← Adaptar a batch_dias_de_caja.py
│   ├── reorder-policy/
│   │   └── SKILL.md              ← Adaptar a politica-alerta-tesoreria
│   └── weekly-report/
│       └── SKILL.md              ← Adaptar a reporte-semanal-tesoreria
├── agents/before/stockpilot.py   ← Loop agentico base (Messages API)
└── evals/tasks.yaml              ← Cómo definir tareas de evaluación
```

---

### ✅ INSTRUCCIÓN 1 — Crear tu `cashflow_forecast.py`

Toma `agent-decomposition/.claude/skills/forecasting/rolling_mean.py` y adáptalo:

```python
#!/usr/bin/env python3
"""
Forecast de saldo de caja — rolling mean 14 días.
Basado en: cwc-workshops/agent-decomposition/.claude/skills/forecasting/rolling_mean.py

Uso: python cashflow_forecast.py CUENTA-001 14
Salida: JSON con {forecast_saldo, confidence, method, flags}
"""
import csv
import json
import sys

DATA = "./data/movimientos_diarios.csv"   # tu CSV de movimientos
cuenta_id = sys.argv[1]
horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 14

# Cargar historial de saldos diarios para esa cuenta
hist = [float(r["saldo_cierre"]) for r in csv.DictReader(open(DATA))
        if r["cuenta_id"] == cuenta_id]

recent = hist[-14:] if len(hist) >= 14 else hist
mean = sum(recent) / max(len(recent), 1)

print(json.dumps({
    "cuenta_id": cuenta_id,
    "forecast_saldo": round(mean * horizon / 14, 2),   # proyección al horizonte
    "dias_de_caja": round(mean / max(abs(mean * 0.1), 1)),  # días antes de alerta
    "confidence": 0.85 if len(recent) >= 14 else 0.60,
    "method": "rolling_mean_14d",
    "flags": [] if len(recent) >= 14 else ["historial_insuficiente"],
}))
```

**Campos del CSV de entrada que necesitas:**
```
cuenta_id, fecha, saldo_cierre, ingresos_dia, egresos_dia, moneda
```

---

### ✅ INSTRUCCIÓN 2 — Crear tu SKILL de Alerta de Tesorería

Crea el archivo `.claude/skills/alerta-tesoreria/SKILL.md` en tu proyecto:

```markdown
---
name: alerta-tesoreria
description: Reglas para determinar si una cuenta requiere acción urgente.
  Cargar cuando la tarea sea "revisar saldos", "alertas", o "¿hay liquidez?".
---

# Política de Alertas de Tesorería

## Inputs necesarios
- on_hand: saldo actual de la cuenta
- saldo_minimo_operativo: definido por empresa (configurar por cliente)
- avg_daily_flow: flujo neto promedio últimos 14 días
- dias_a_pago_critico: cuántos días hasta el próximo pago obligatorio

## Niveles de alerta

| Nivel | Condición | Acción |
|---|---|---|
| CRÍTICO | on_hand < saldo_minimo | Notificar gerencia + bloquear pagos no críticos |
| ALTO | dias_de_caja < dias_a_pago_critico | Activar línea de crédito / transferencia entre cuentas |
| MEDIO | dias_de_caja < 14 | Revisar egresos programados esta semana |
| OK | dias_de_caja >= 14 | Sin acción requerida |

## Fórmula de días de caja
dias_de_caja = on_hand / abs(avg_daily_flow)   (solo si avg_daily_flow < 0)
```

---

### ✅ INSTRUCCIÓN 3 — Crear tu SKILL de Reporte Semanal de Tesorería

Adapta `.claude/skills/weekly-report/SKILL.md`:

```markdown
---
name: reporte-semanal-tesoreria
description: Estructura del reporte semanal de flujo de caja.
  Cargar cuando pidan "reporte semanal", "resumen de tesorería", "informe del lunes".
---

## Estructura del reporte

# Reporte de Tesorería — Semana del {{fecha}}

## 🔴 Cuentas en Alerta (saldo < mínimo operativo)
| Cuenta | Banco | Saldo actual | Mínimo | Días de caja |

## 🟡 Pagos Críticos Esta Semana
| Concepto | Monto | Vencimiento | Cuenta origen |

## Posición Consolidada
| Moneda | Saldo total | Variación semana |

## Forecast Próximas 2 Semanas
Basado en rolling mean 14 días + compromisos programados.

## INSTRUCCIÓN: Hazlo en código, no en tool calls individuales
Los CSV de movimientos pueden tener miles de filas.
Escribe UN script Python que cargue todo y emita el markdown.
No hagas una tool call por cuenta — eso es el anti-patrón.
```

---

### ✅ INSTRUCCIÓN 4 — El Loop Agentico Base

El archivo `agents/before/stockpilot.py` te muestra el patrón mínimo para un agente agentico con tools usando la API de Anthropic directamente (sin frameworks). Es tu template para cualquier agente que construyas:

```python
# Patrón base — adaptar de stockpilot.py
while turns < max_turns:
    resp = client.messages.create(model=MODEL, tools=TOOL_DEFS, messages=messages)
    
    if resp.stop_reason == "end_turn":
        break
    
    # Ejecutar tools y continuar
    tool_results = [dispatch(block.name, block.input) for block in resp.content
                    if block.type == "tool_use"]
    messages.append({"role": "user", "content": tool_results})
```

**Usa este patrón** en lugar de frameworks complejos. Es todo lo que necesitas para el 80% de los casos.

---

## 🔴 PRIORIDAD 1 — `agents-that-remember/` → Tu Agente Consultor con Memoria

### ¿Qué tiene este workshop?

Muestra cómo pasar de un agente "goldfish" (olvida todo entre sesiones) a un "colega" (recuerda contexto acumulado) usando:
1. **Memory Store** — almacenamiento persistente entre sesiones
2. **Dreaming** — consolida transcripts históricos en memoria estructurada

### ¿Por qué te importa?

Para tu negocio de consultoría, esto es transformacional:

```
SIN memoria (como todos):
  Reunión con cliente → análisis → entregable → olvido total

CON memoria (tu ventaja):
  Sesión 1: cliente explica su situación financiera
  Sesión 2: agente ya sabe el contexto, recomienda sobre historial real
  Sesión 10: agente conoce patrones del negocio del cliente como un CFO interno
```

### 📁 Archivos clave a estudiar

```
agents-that-remember/
├── README.md           ← Leer completo — tiene el flujo de 3 pasos
└── scripts/
    └── bootstrap.sh    ← Setup del agente + environment + sesiones
```

### ✅ INSTRUCCIÓN 5 — Diseñar tu Memory Store de Cliente

Cuando implementes Claude Managed Agents con memoria, el `prompt` del Memory Resource es lo que controla **qué recuerda y cómo lo organiza**. Diseña el tuyo así:

```json
{
  "type": "memory_store",
  "memory_store_id": "{{MEM_ID}}",
  "prompt": "Eres el asesor financiero de {{nombre_empresa}}.
    Recordar siempre:
    - KPIs financieros por periodo (flujo de caja, DSO, DPO, cobertura)
    - Decisiones tomadas y su resultado
    - Contexto del negocio (sector, estacionalidad, clientes clave)
    - Compromisos y seguimientos pendientes
    - Preferencias de formato de reporte del cliente",
  "access": "read_write"
}
```

### ✅ INSTRUCCIÓN 6 — Aplicar Dreaming a tu Propio Contexto

Después de varias sesiones con un cliente, usa el Dreaming Service para consolidar:

```bash
ant beta:dreams create \
  --model claude-opus-4-7 \
  --input '{"type":"memory_store","memory_store_id":"MEM_ID"}' \
  --input '{"type":"sessions","session_ids":["SES_1","SES_2","SES_3"]}' \
  --instructions "Soy asesor financiero de la empresa X.
    Consolidar: ratios financieros por periodo, problemas identificados,
    soluciones implementadas, estado actual de KPIs."
```

---

## 🟡 PRIORIDAD 2 — `production-ready-agent/` → Tu Producto SaaS Multi-Agente

### ¿Qué tiene este workshop?

El Deal Desk es un sistema de análisis de M&A con:
- **Coordinador** que delega a 4 sub-agentes en paralelo
- **Memory Store** para lecciones de deals anteriores
- **MCP** para conectar con herramientas externas
- **UI en Next.js** que hace streaming de cada evento

### Tu versión: "Financial Pulse" — Dashboard de Salud Financiera para PYMEs

```
Coordinador financiero
├── Sub-agente: Análisis de liquidez (cash flow, días de caja)
├── Sub-agente: Cuentas por cobrar (aging, DSO, riesgo de mora)
├── Sub-agente: Cuentas por pagar (DPO, vencimientos críticos)
└── Sub-agente: Benchmarks sectoriales (comparar vs industria)
     └── Emite: Reporte ejecutivo con semáforos + recomendaciones
```

### ✅ INSTRUCCIÓN 7 — Estudiar la Arquitectura del Deal Desk

Lee en este orden:
1. `production-ready-agent/README.md` — arquitectura completa
2. `production-ready-agent/seed/agents/*.yaml` — cómo se definen los agentes
3. `production-ready-agent/starter/app/api/` — los 7 endpoints que implementar
4. `production-ready-agent/solution/app/api/` — solución de referencia

El patrón de los 7 TODOs es tu checklist para cualquier app con Managed Agents:
```
1. Listar sesiones
2. Crear sesión (agent + environment + recursos)
3. Enviar mensajes y outcomes
4. Recuperar sesión
5. Bridgear el event stream (SSE)
6. Confirmar tool calls gated
7. Eliminar sesión
```

---

## 🟡 PRIORIDAD 2 — `eval-driven-agent-development/` → Validar tu Modelo de Churn

### ¿Qué tiene este workshop?

Itera un agente generador de PPTX a través de 6 variantes, midiendo cada una con:
- **Graders programáticos** (métricas de estructura)
- **LLM-as-judge** (calidad subjetiva con criterios definidos)

### Aplicación directa a tu Proyecto 3 (Churn B2B, deadline 14-jun-2026)

En vez de presentaciones, tus variantes son **configuraciones del modelo Random Forest**:

```
Variante 0: Baseline (parámetros por defecto)
Variante 1: Class weight balanceado
Variante 2: Feature engineering (ratios financieros)
Variante 3: Threshold optimizado para recall
Variante 4: Ensemble con Gradient Boosting
Variante 5: QA-loop con LLM evaluando las predicciones de riesgo alto
```

### ✅ INSTRUCCIÓN 8 — Adaptar el Framework de Evaluación

Toma el patrón de `src/graders.ts` y crea tu `graders.py`:

```python
# Adaptado de eval-driven-agent-development/src/graders.ts

GRADERS_CHURN = [
    {
        "name": "recall_clase_churn",
        "description": "El modelo debe identificar al menos 75% de los churners reales",
        "check": lambda metrics: metrics["recall_churn"] >= 0.75,
        "weight": 3,  # crítico — mejor perder un falso positivo que un churn real
    },
    {
        "name": "precision_minima",
        "description": "No más del 40% de alarmas falsas",
        "check": lambda metrics: metrics["precision_churn"] >= 0.60,
        "weight": 2,
    },
    {
        "name": "features_financieras_usadas",
        "description": "El modelo usa al menos 3 features de ratios financieros",
        "check": lambda fi: any("ratio" in f or "dso" in f or "flujo" in f
                               for f in fi["top_10_features"]),
        "weight": 1,
    },
]
```

---

## 🟢 SIEMPRE — `how-we-claude-code/` → Metodología con Clientes

### Las 3 fases que debes aplicar en CADA proyecto de cliente

| Fase | Qué haces | Entregable |
|---|---|---|
| **1. Exploración** | Entrevista al cliente (Claude te ayuda a generar las preguntas) | Product spec / brief de necesidades |
| **2. Planificación** | 2-4 wireframes/mockups divergentes para comparar | HTML estático o Power BI mock |
| **3. Verificación** | Componentes con contratos verificables (tests automáticos) | Dashboard con criterios de aceptación definidos |

### ✅ INSTRUCCIÓN 9 — Prompt de Discovery con Clientes

Copia este prompt en tu próxima conversación antes de arrancar un proyecto:

```
Actúa como consultant senior de finanzas y datos.
Voy a hacer una entrevista de discovery con [nombre empresa].
Genera 10 preguntas clave que me permitan entender:
1. Su proceso actual de [área específica]
2. Sus puntos de dolor más costosos
3. Sus KPIs actuales y los deseados
4. Sus restricciones técnicas (sistemas, formatos de datos)
5. Cómo definen el éxito del proyecto

Sector: [construcción/retail/agroindustria]
Contacto: [cargo del interlocutor]
```

---

## 🟢 CUANDO ESCALES — `rightmodel/` → Optimizar Costos de API

### ¿Cuándo aplicar esto?

Cuando tengas agentes en producción con clientes pagando. El skill te ayuda a hacer un "sweep" de modelos para encontrar el punto óptimo calidad/costo.

### La lógica de decisión (aprenderla desde ahora):

```
Haiku 4.5   → Tareas simples: clasificación, extracción de datos, alertas
Sonnet 4.6  → Tareas medias: análisis financiero, generación de reportes
Opus 4.7    → Tareas complejas: forecasting multi-variable, auditoría, estrategia
```

Para un reporte de tesorería semanal: **Sonnet** es suficiente y cuesta ~10x menos que Opus.

---

## 🏗️ Arquitectura Recomendada para tu Negocio (basada en todos los workshops)

```
┌─────────────────────────────────────────────────────────┐
│              TU AGENTE FINANCIERO                        │
├─────────────────────────────────────────────────────────┤
│  CAPA 1: SKILLS (cargados bajo demanda)                  │
│  ├── alerta-tesoreria/SKILL.md                           │
│  ├── forecast-cashflow/SKILL.md + rolling_mean.py        │
│  ├── reporte-semanal/SKILL.md                            │
│  └── analisis-rfm/SKILL.md  (Proyecto 2)                 │
├─────────────────────────────────────────────────────────┤
│  CAPA 2: CODE EXECUTION (un script, no 100 tool calls)   │
│  ├── batch_analisis_cuentas.py                           │
│  └── generar_reporte.py                                  │
├─────────────────────────────────────────────────────────┤
│  CAPA 3: SUBAGENTES (solo cuando hay complejidad real)   │
│  ├── sub-agente: forecast estacional/promo               │
│  └── sub-agente: benchmarks sectoriales                  │
├─────────────────────────────────────────────────────────┤
│  CAPA 4: MEMORIA (diferenciador comercial)               │
│  ├── Memory Store por cliente                            │
│  └── Dreaming mensual de transcripts                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📅 Cronograma de Implementación

### Semana 1–2 (Ahora → 7-jun)
- [ ] Leer `agent-decomposition/README.md` completo
- [ ] Adaptar `rolling_mean.py` → `cashflow_forecast.py`
- [ ] Crear tu primer SKILL de alerta de tesorería
- [ ] Usar el patrón de evals para el Proyecto 3 (Churn)

### Semana 3–4 (8-jun → 21-jun)
- [ ] Leer `agents-that-remember/README.md`
- [ ] Diseñar el Memory Store prompt para tu primer cliente
- [ ] Estudiar arquitectura del `production-ready-agent`

### Mes 2 (jul)
- [ ] Construir MVP del agente financiero con Memory Store
- [ ] Testar con Trainyl o Estudio Contable de tía
- [ ] Aplicar `eval-driven-agent-development` para medir mejoras

### Mes 3 (ago)
- [ ] Desplegar producto a 2-3 clientes piloto
- [ ] Aplicar `rightmodel` para optimizar costos
- [ ] Iterar basado en feedback real

---

## 💡 El Marco de Decisión Más Importante (del workshop)

Antes de escribir cualquier agente, hazte estas preguntas:

```
¿La tarea es puntual y determinista? → TOOL CALL simple
¿La tarea tiene política/regla de negocio? → SKILL (archivo .md)
¿La tarea necesita cargar mucho contexto? → CODE EXECUTION (un script Python)
¿La tarea es tan compleja que necesita su propio contexto? → SUBAGENTE
¿El agente necesita recordar entre sesiones? → MEMORY STORE
¿Tienes transcripts históricos que el agente debería conocer? → DREAMING
```

---

## 🔗 Links de Referencia Clave

- Documentación Memory Stores: https://platform.claude.com/docs/en/managed-agents/memory
- Documentación Dreaming: https://platform.claude.com/docs/en/managed-agents/dreaming
- Claude Managed Agents Quickstart: https://platform.claude.com/docs/en/managed-agents/quickstart
- API Keys: https://platform.claude.com/settings/keys
- Claude API Models: https://docs.anthropic.com/en/docs/about-claude/models

---

> **Nota:** Este archivo fue generado el 25-may-2026 analizando los 8 workshops del repositorio `cwc-workshops-main`. Los workshops son de Anthropic (Apache 2.0). Toda adaptación de código en este documento es original para el caso de uso de tesorería y consultoría financiera.
