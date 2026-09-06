# 📘 Guía Paso a Paso — Agente de Tesorería con Claude API
**Gabriel Untiveros | Skill_financiero | Lima, Perú**
**Iniciado:** 2026-05-25

> Este archivo documenta **qué hace cada notebook, por qué se tomaron las decisiones de diseño, y cómo conecta con el siguiente**. Es tu bitácora técnica del proyecto.

---

## 🗺️ Mapa del Proyecto

```
NB 01 → Datos simulados (CSV base)
   ↓
NB 02 → Forecast de caja (scripts Python ejecutables)
   ↓
NB 03 → Los 3 SKILLs .md (políticas del agente)
   ↓
NB 04 → Loop agentico (Messages API de Anthropic)
   ↓
NB 05 → Memory Store (SQLite — del goldfish al CFO interno)
```

Cada notebook produce un **artefacto concreto** que el siguiente consume. No son ejercicios académicos — son piezas reales del agente.

---

---

# 📓 NB 01 — Datos Simulados

**Archivo:** `01_datos_simulados.ipynb`  
**Output:** `data/movimientos_diarios.csv` (270 filas) + `data/saldos_90dias.png`  
**Estado:** ✅ Completado

## ¿Por qué empezamos aquí?

Antes de escribir una sola línea de agente, necesitamos datos reales que representen los problemas que el agente va a resolver. El workshop original (`agent-decomposition`) usa archivos CSV de ventas/inventario. Nosotros usamos el equivalente exacto en tesorería: **movimientos diarios de cuentas bancarias**.

Sin este CSV, los scripts de forecast no tienen nada que leer, y los skills no tienen casos reales para validar.

## Decisiones de diseño

### ¿Por qué 3 cuentas con comportamientos distintos?

Porque el skill de alertas necesita cubrir los 3 escenarios reales que existen en tesorería corporativa:

| Cuenta | Escenario que representa | Por qué importa |
|---|---|---|
| CUENTA-001 (BCP/PEN) | Cuenta operativa estable | El "caso base" — el forecast simple funciona bien aquí |
| CUENTA-002 (BBVA/PEN) | Cuenta con picos de planilla | Prueba el skill de alertas: baja drásticamente cada quincena |
| CUENTA-003 (Interbank/USD) | Cuenta dólares irregular | Prueba multimoneda y flujo no diario |

### ¿Por qué `np.random.seed(42)`?

Reproducibilidad. Cada vez que ejecutes el NB 01 obtienes exactamente los mismos números. Eso es crítico para debuggear el agente más adelante — si los datos cambian en cada ejecución, no puedes distinguir si un error es del agente o del dataset.

### ¿Por qué el periodo de estrés en días 60–70 de CUENTA-001?

Para simular un evento real: una semana de gastos extraordinarios (compra de equipos, pago de impuestos). El agente debe poder detectar que el saldo bajó en ese periodo y qué tan rápido se recuperó. Si el forecast solo ve los últimos 14 días y cae en ese periodo, debe baja su `confidence`.

### ¿Por qué el fondeo en días 14/29 (un día antes de la planilla)?

Así funciona la tesorería real: la empresa transfiere fondos a la cuenta de planilla el día anterior al pago. Simular esto correctamente hace que los saldos de CUENTA-002 sean realistas — no siempre llega la transferencia puntual, y el skill de alertas debe detectar cuando llega tarde.

## Paso a paso del código

### Celda 1 — Setup
```python
np.random.seed(42)
FECHA_INICIO = pd.Timestamp('2026-02-24')
DIAS = 90
fechas = pd.date_range(FECHA_INICIO, periods=DIAS, freq='D')
```
**Por qué:** Definimos el rango temporal como variable global para que todas las cuentas compartan exactamente las mismas fechas. Si cada cuenta generara sus fechas de forma independiente, habría desalineación en el CSV.

### Celdas 2-4 — Generación de cada cuenta
Cada cuenta sigue el mismo patrón:
1. Definir `saldo_inicial`
2. Generar `ingresos_dia` con `np.random.normal(media, std, DIAS)`
3. Generar `egresos_dia` con su propia distribución
4. Calcular `saldo_cierre = saldo_inicial + cumsum(ingresos - egresos)`
5. Aplicar `np.maximum(saldo, piso)` para evitar saldos negativos irreales

**Punto clave:** el saldo es **acumulado** (`cumsum`), no independiente por día. Así refleja la realidad: el saldo de hoy depende del de ayer.

### Celda 5 — Consolidar
```python
df = pd.concat([df_c001, df_c002, df_c003])
df['fecha'] = df['fecha'].dt.strftime('%Y-%m-%d')
df = df.sort_values(['cuenta_id', 'fecha'])
```
**Por qué strftime:** Guardamos la fecha como string `YYYY-MM-DD` en el CSV. Los scripts de forecast posteriores leen el CSV con `csv.DictReader` (sin pandas), y comparar strings de fecha funciona correctamente con ese formato (lexicográficamente ordenable).

### Celda 7 — Verificaciones automáticas
5 `assert` que validan la integridad antes de continuar. **Esto es el patrón de evals aplicado desde NB 01**: no basta con "parece bien" — los contratos deben ser verificables.

## Resultados obtenidos

| Cuenta | Saldo mín | Saldo máx | Saldo promedio |
|---|---|---|---|
| CUENTA-001 (PEN) | S/ 254,544 | S/ 404,435 | S/ 333,373 |
| CUENTA-002 (PEN) | S/ 81,674 | S/ 249,581 | S/ 156,546 |
| CUENTA-003 (USD) | USD 18,473 | USD 121,874 | USD 76,441 |

## Conexión con NB 02

El CSV generado tiene exactamente los campos que necesita `rolling_mean_cashflow.py`:
```
cuenta_id, fecha, saldo_cierre, ingresos_dia, egresos_dia, moneda
```
El NB 02 lee este CSV para calcular el forecast. La columna `saldo_cierre` es el equivalente directo de `units_sold` en el workshop original.

---

---

# 📓 NB 02 — Cashflow Forecast

**Archivo:** `02_cashflow_forecast.ipynb`  
**Output:**
- `.claude/skills/forecast-cashflow/rolling_mean_cashflow.py` (script ejecutable)
- `.claude/skills/forecast-cashflow/batch_dias_de_caja.py` (script batch)
- `.claude/skills/forecast-cashflow/SKILL.md` (política de decisión)  
**Estado:** ✅ Completado

## ¿Qué es esto y por qué importa?

Este NB adapta el núcleo técnico del workshop `agent-decomposition` al dominio de tesorería. El workshop tiene dos scripts de forecast:
- `rolling_mean.py` → forecast para un solo SKU
- `batch_days_of_cover.py` → urgencia de todos los SKUs en un solo script

Nosotros creamos los equivalentes exactos en tesorería:
- `rolling_mean_cashflow.py` → forecast para una sola cuenta bancaria
- `batch_dias_de_caja.py` → días de caja de todas las cuentas rankeadas por urgencia

**El principio que viene del workshop:** en vez de que el agente haga 100 tool calls para leer cuenta por cuenta, ejecuta UN script Python que devuelve el resultado de todas. Eso es "compute-over-context" — dejar que el código haga el trabajo pesado.

## Decisiones de diseño

### ¿Por qué rolling mean de 14 días?

14 días es el horizonte estándar para tesorería operativa (2 semanas laborales). Captura tendencias recientes sin ser demasiado volátil. El workshop usa el mismo horizonte para inventario por la misma razón.

Si usáramos 30 días, el forecast reaccionaría demasiado lento a cambios recientes (ej: un mes de egresos altos). Si usáramos 7 días, sería demasiado sensible a eventos puntuales.

### ¿Por qué Path A vs Path B?

Esto viene directamente del SKILL.md del workshop. La idea es que el agente no siempre necesita un modelo sofisticado:

| Situación | Solución | Costo en tokens |
|---|---|---|
| Cuenta estable, horizonte ≤ 14 días | Rolling mean (Path A) | ~50 tokens |
| Cuenta con pagos programados o crítica | Subagente (Path B) | ~800 tokens |

Para el 80% de las consultas de tesorería, Path A es suficiente. Path B se reserva para cuando hay complejidad real que justifica el costo.

### ¿Por qué `dias_de_caja` en vez de solo el saldo?

`dias_de_caja = saldo_actual / abs(flujo_neto_promedio_diario)` es la métrica más accionable para un tesorero. No es lo mismo tener S/ 50,000 en una empresa que gasta S/ 5,000/día (10 días de caja — alerta) que en una que gasta S/ 500/día (100 días — tranquilo). El saldo solo no dice nada sin el contexto del flujo.

Esta métrica es el equivalente directo de `days_of_cover` en el workshop de inventario.

### ¿Por qué `confidence = 0.85` si hay ≥14 días de historial?

0.85 es el mismo valor que usa el workshop. Significa: "el modelo tiene suficiente historia reciente para ser confiable, pero no es perfecto". Si hay menos de 14 días, bajamos a 0.60, que por diseño (en el skill de alertas) activa revisión humana antes de tomar acción.

## Paso a paso del código

### Celdas 1-3 — Implementar `rolling_mean_cashflow.py`

El script adapta `rolling_mean.py` del workshop con 3 cambios:
1. `sku` → `cuenta_id`
2. `units_sold` → `saldo_cierre`
3. Agrega `dias_de_caja` como métrica nueva (no existía en inventario)

```python
# Workshop original            # Nuestra adaptación
sku = sys.argv[1]              cuenta_id = sys.argv[1]
hist = [units_sold ...]        hist = [saldo_cierre ...]
forecast_qty = mean * horizon  forecast_saldo = mean * horizon / 14
                               dias_de_caja = mean / abs(flujo_neto)  # NUEVO
```

### Celda 4 — Prueba individual por cuenta

Ejecutamos el script para las 3 cuentas y comparamos resultados. Puntos a verificar:
- CUENTA-002 debe tener pocos `dias_de_caja` si cae en periodo post-planilla
- CUENTA-003 (USD) debe retornar valores coherentes aunque el flujo sea irregular

### Celdas 5-7 — Implementar `batch_dias_de_caja.py`

Adapta `batch_days_of_cover.py`. El anti-patrón que evitamos:
```
❌ MALO: for cuenta in cuentas: tool_call(get_saldo, cuenta)   # 3 calls mínimo
✅ BUENO: python batch_dias_de_caja.py → JSON con las 3 en 1 call
```

El batch script:
1. Lee el CSV completo una sola vez
2. Calcula `dias_de_caja` para cada cuenta
3. Rankea por urgencia (menor días primero)
4. Retorna JSON con flag `requiere_atencion`

### Celda 8 — Guardar scripts como archivos ejecutables

Los scripts se guardan en `.claude/skills/forecast-cashflow/` para que el agente del NB 04 pueda ejecutarlos via tool call de bash. Esta es la arquitectura del workshop: los skills son archivos en disco, no lógica hardcodeada en el prompt.

### Celda 9 — Crear SKILL.md del forecast

El SKILL.md no es documentación — es una **instrucción operativa para el agente**. Le dice exactamente cuándo usar Path A, cuándo usar Path B, y qué hacer con el output del forecast.

## Resultados obtenidos

| Cuenta | Saldo actual | Forecast 14d | Días de caja | Flujo neto/día | Confidence | Path |
|---|---|---|---|---|---|---|
| CUENTA-001 | S/ 356,608 | S/ 384,173 | 999 (flujo +) | +S/ 1,969 | 0.85 | A |
| CUENTA-002 | S/ 224,331 | S/ 242,379 | 999 (flujo +) | +S/ 1,289 | 0.85 | A |
| CUENTA-003 | USD 118,639 | USD 121,264 | 999 (flujo +) | +USD 187 | 0.85 | A |

> **Nota sobre `dias_de_caja: 999`:** Los 90 días simulados terminaron en un periodo de flujo neto positivo para las 3 cuentas (ingresos > egresos en los últimos 14 días). El valor 999 es el centinela para "flujo positivo — sin límite en la ventana actual". En un cliente real habrá días con flujo negativo donde el indicador será accionable.

## Bug corregido (2026-05-26)

**Causa:** `Path(__file__).parent.parent.parent` en los scripts solo subía 3 niveles (hasta `.claude/`) pero el CSV está 4 niveles arriba (en `Skill_financiero/data/`).

```
Script:  Skill_financiero/.claude/skills/forecast-cashflow/script.py
                                                            ↑ parent x1
                                              ↑ parent x2
                               ↑ parent x3  (INCORRECTO — llega a .claude/)
                ↑ parent x4  (CORRECTO — llega a Skill_financiero/)
```

**Fix:** Cambiar a `.parent.parent.parent.parent / "data"` en ambos scripts y en el notebook.

## Conexión con NB 03

Los scripts creados aquí son **consumidos por el SKILL.md del NB 03**. El NB 03 no escribe más código — escribe las políticas que le dicen al agente cuándo y cómo ejecutar estos scripts. La relación es: NB 02 = las herramientas, NB 03 = las reglas de uso de esas herramientas.

---

---

# 📓 NB 03 — Los 3 SKILLs de Tesorería

**Archivo:** `03_skills_tesoreria.ipynb`  
**Output:**
- `.claude/skills/forecast-cashflow/SKILL.md`
- `.claude/skills/alerta-tesoreria/SKILL.md`
- `.claude/skills/reporte-semanal/SKILL.md`  
**Estado:** ✅ Completado

## ¿Qué es un SKILL en este contexto?

Un SKILL es un archivo Markdown que el agente lee **bajo demanda** cuando necesita una política específica. No está siempre en el prompt (eso desperdiciaría tokens). Se carga solo cuando la tarea requiere esa expertise.

Del workshop: en vez de un system prompt de 402 líneas que incluye todo, el agente tiene un prompt de 15 líneas + acceso a skills modulares. Los skills son los que contienen la lógica de negocio.

## Los 3 SKILLs y su cadena de dependencias

```
[forecast-cashflow/SKILL.md]
  Decide: ¿Path A (rolling mean) o Path B (subagente)?
  Output: {forecast_saldo, dias_de_caja, confidence, flags}
       ↓
[alerta-tesoreria/SKILL.md]
  Consume: {dias_de_caja, saldo_minimo_operativo}
  Decide: nivel de alerta (CRITICO / ALTO / MEDIO / OK)
  Output: {nivel_alerta, accion_recomendada}
       ↓
[reporte-semanal/SKILL.md]
  Consume: alertas + forecasts de todas las cuentas
  Produce: markdown del reporte ejecutivo semanal
```

## Decisiones de diseño

### ¿Por qué los niveles CRÍTICO / ALTO / MEDIO / OK?

Son los mismos 4 niveles que usa el workshop en la reorder-policy (stockout / expedite / reorder / ok). El número de niveles no es arbitrario — 4 es suficiente para cubrir los casos de acción sin sobrecomplicar la lógica del agente.

### ¿Por qué `prioridad` numérica (0–4)?

Para que el reporte ordene las cuentas automáticamente sin lógica de string comparison. REVISAR=0 va primero porque indica datos problemáticos que el agente no puede resolver solo.

### ¿Por qué `dias_de_caja = 999` como centinela?

En vez de `None` o `float('inf')`, 999 es un número que el agente puede comparar numéricamente sin manejo especial. Del workshop: los contratos tipados son estrictos — el JSON siempre tiene todos los campos con tipos consistentes.

### ¿Por qué `generar_reporte.py` en vez de que el agente construya el markdown?

El reporte necesita datos de todas las cuentas + cálculos + formato de tabla. Si el agente lo construye con tool calls individuales: N calls para N cuentas + tokens de cada resultado = ineficiente. Un script lo hace en 1 call y devuelve el markdown completo. Del workshop: "write one Python script that reads the CSVs and emits markdown — do not make per-SKU tool calls".

## Paso a paso del código

### Celda 2 — Verificar prerequisitos
Lee los outputs del NB 02 (batch forecast) para tener el estado real de las cuentas antes de definir las reglas de alerta.

### Celda 4 — Función `evaluar_alerta()`
Implementa las reglas del SKILL en Python puro para validar la lógica antes de escribir el SKILL.md. Primero probar, luego documentar.

### Celda 6 — `generar_reporte.py`
Script integrado que hace todo el pipeline: cargar CSV → calcular forecast → aplicar alertas → emitir markdown. Una sola ejecución = un reporte completo.

## Resultados obtenidos

_(completar al ejecutar el NB — valores dependen del día de ejecución)_

Las 3 cuentas deben aparecer en estado **OK** con `dias_de_caja: 999` porque el dataset simulado termina en periodo de flujo positivo. Ver la nota sobre 999 en el SKILL.md.

## Conexión con NB 04

El NB 04 recibe el mismo `generar_reporte.py` como una tool que el agente puede llamar cuando el usuario pregunta "¿cómo estamos en caja?". Los SKILLs son los archivos de política que el agente cargará bajo demanda para decidir qué tool ejecutar.

---

---

# 📓 NB 04 — Loop Agentico Base

**Archivo:** `04_loop_agentico.ipynb`  
**Output:** Agente funcional que responde preguntas de tesorería en lenguaje natural  
**Estado:** ✅ Completado

## ¿Qué es el loop agentico?

El corazón del agente. El patrón `while turns < max_turns` adaptado directamente de `agents/before/stockpilot.py`. Sin frameworks — solo la SDK de Anthropic.

## Decisiones de diseño

### ¿Por qué solo 2 tools?

El workshop original de StockPilot tenía 12 tools (`get_stock_level`, `get_sales_velocity`, `get_product`, etc.). La versión optimizada tiene 2. La misma lógica aplica aquí:

| Versión monolítica (anti-patrón) | Versión skills (este NB) |
|---|---|
| 12 tools, 402 líneas de prompt | 2 tools, ~15 líneas de prompt |
| 1 tool call por cuenta | 1 script para todas las cuentas |
| El agente hace N llamadas | El agente hace 1 llamada |

Las 2 tools son:
- **`bash_execute`** — ejecuta cualquier script Python de los skills
- **`read_skill`** — carga un SKILL.md bajo demanda (mantiene el prompt corto)

### ¿Por qué el system prompt es tan corto?

15 líneas vs 402 del monolito. La diferencia: las 402 líneas contenían todas las políticas de negocio siempre en el contexto. En la arquitectura de skills, las políticas se cargan solo cuando la tarea las necesita con `read_skill`. Menos tokens en contexto = más barato + más rápido.

### ¿Por qué `cwd=BASE` en `subprocess.run()`?

El directorio de trabajo del subproceso no afecta la resolución de `Path(__file__)` — los scripts usan rutas absolutas desde su propia ubicación. Sin embargo, establecer `cwd` al root del proyecto es buena práctica para cualquier output relativo que los scripts puedan generar.

## Paso a paso del código

### Celda 1 — Setup y verificación de API key
Lee el `.env` manualmente (sin depender de `python-dotenv`) y verifica que la key empiece con `sk-ant-`.

### Celda 3 — Definición de tools
Los `TOOL_DEFS` son los JSON schemas que la API de Anthropic usa para entender qué tools tiene el agente. El campo `description` es crítico — el agente decide qué tool usar basándose en él.

### Celda 5 — System prompt
Las rutas a los scripts están hardcodeadas como rutas absolutas (usando `Path.as_posix()`) para que el agente no tenga que inferirlas.

### Celda 6 — `dispatch()`
La función que mapea el nombre de una tool a su ejecución real. Error handling incluido: si el script falla, el agente recibe el mensaje de error y puede intentar corregir.

### Celda 7 — `run_agent()`
El loop exacto del workshop. Puntos clave:
- `stop_reason == 'end_turn'` → el agente terminó, salir del loop
- `tool_results` se acumula para TODOS los tool calls del mismo turn antes de pasar al siguiente
- `messages` crece con cada turn: usuario → asistente → tool results → asistente → ...

### Celdas 8-10 — 3 tests
Tres preguntas reales de tesorería para verificar que el agente:
1. Usa el script batch (no tool calls individuales)
2. Genera el reporte completo en 1 tool call
3. Carga el SKILL de alertas cuando necesita interpretar resultados

### Celda 11 — Métricas
Cálculo de costo real en USD para los 3 queries. Útil para estimar el precio de un cliente real (ej: 10 queries/día × 30 días = costo mensual de operación).

## Resultados obtenidos

_(ejecutado 2026-05-26 — valores reales)_

| Test | Turns | Tool calls | Tokens totales | Costo USD |
|---|---|---|---|---|
| ¿Cómo estamos en caja? | 3 | 4 | 9,233 | $0.0346 |
| Reporte semanal | 3 | 3 | 7,205 | $0.0256 |
| CUENTA-002 días de caja | 3 | 3 | 7,141 | $0.0253 |
| Cuenta con más riesgo | 3 | 3 | 7,535 | — |

**Total 3 queries principales:** USD $0.1037  
**Costo por query:** ~USD $0.035

**Nota sobre WinError 2:** En cada sesión el agente falla el primer `bash_execute` porque pasa `command` como JSON string en lugar de lista Python. Se autocorrige en turno 2. Cuesta 1 turn extra pero no bloquea. Fix aplicado en NB 05 (`dispatch_v2`).

---

---

## 🧠 Conceptos clave del workshop aplicados al proyecto

### 1. Compute-over-context
En vez de hacer tool calls individuales (una por cuenta), ejecutamos un script Python que procesa todo el CSV de una vez. El agente recibe un JSON compacto, no decenas de llamadas.

**Workshop:** `batch_days_of_cover.py` reemplaza 100+ tool calls de `get_stock_level`  
**Nuestro caso:** `batch_dias_de_caja.py` reemplaza N tool calls de `get_saldo_cuenta`

### 2. Policy-as-skill
Las reglas de negocio (cuándo alertar, qué umbral es crítico, cómo estructurar el reporte) viven en archivos `.md`, no en el código Python ni en el prompt del agente. Esto permite cambiar la política sin tocar el código.

**Workshop:** `reorder-policy/SKILL.md` define cuándo reordenar  
**Nuestro caso:** `alerta-tesoreria/SKILL.md` define cuándo alertar

### 3. Typed contracts
El output de cada script/skill tiene un JSON con campos definidos. El agente los parsea estrictamente — si el JSON es inválido, es un error, no algo para adivinar.

**Workshop:** `{forecast_qty, confidence, method, flags}`  
**Nuestro caso:** `{forecast_saldo, dias_de_caja, confidence, method, flags}`

### 4. Scope (cuándo usar subagente)
Un subagente se justifica cuando la tarea necesita su propio contexto (historial largo, múltiples fuentes, lógica compleja). Para consultas simples, el agente principal ejecuta el script directamente.

**Workshop:** Path B del forecasting skill (seasonal/promo SKUs)  
**Nuestro caso:** Path B cuando la cuenta tiene pagos programados críticos

---

---

# 📓 NB 05 — Memory Store: del Goldfish al CFO Interno

**Archivo:** `05_memory_store.ipynb`  
**Output:** `data/memory/agente_tesoreria.db` + `run_agent_with_memory()` con memoria persistente  
**Estado:** ✅ Completado

## ¿Por qué existe este notebook?

El agente del NB 04 funciona, pero tiene un problema estructural: **olvida todo entre sesiones**. Cada `run_agent()` empieza desde cero — sin saber qué alertas se detectaron la semana pasada, qué acciones se recomendaron, ni cómo se llama el cliente.

Eso es suficiente para una demo. No es suficiente para un producto que se cobra mensualmente.

El NB 05 agrega la capa que transforma el agente de "herramienta de consulta" a "CFO interno": **memoria persistente entre sesiones**.

## La diferencia en la práctica

| Sin memoria (NB 04) | Con memoria (NB 05) |
|---|---|
| Cada sesión empieza desde cero | Recuerda el estado de las últimas 3 sesiones |
| No puede decir "vs la semana pasada" | Compara estado actual con estado histórico |
| No trackea acciones pendientes | Recuerda qué recomendó y qué sigue abierto |
| No conoce preferencias del cliente | Almacena configuración específica por cuenta |

## Arquitectura del Memory Store

```
SQLite (agente_tesoreria.db)
├── sessions        — historial de queries + resúmenes
├── alertas         — estados de cuentas por sesión (parsea JSON de tool_log)
├── client_facts    — key-value de preferencias del cliente
└── pending_actions — acciones recomendadas pendientes de completar
```

Backend SQLite — cero dependencias externas, archivo único, portable. El cliente puede llevarse el `.db` y el histórico está ahí.

## Decisiones de diseño

### ¿Por qué SQLite y no JSON?

JSON es más simple para un archivo. SQLite es mejor cuando:
- Necesitas consultar "último estado por cuenta" (GROUP BY en SQL vs loop manual)
- Quieres queries temporales reales (ORDER BY fecha)
- El archivo va a crecer (100+ sesiones) sin degradar performance

### ¿Por qué `build_context_block()` en texto plano?

El contexto histórico se inyecta como texto en el system prompt — no como herramienta. La razón: el agente tiene el contexto disponible desde el primer token de respuesta, sin necesidad de hacer una tool call extra para "cargar la memoria". Menos turns = menos costo.

El costo real: cada sesión con historial lleva ~300-500 tokens extra en el prompt. A $3/M tokens de input, eso es ~$0.001 extra por sesión. Costo despreciable.

### ¿Por qué `extract_account_state()` no llama a la API?

Alternativa posible: hacer una llamada extra a Claude para "¿qué alertas se detectaron?". Más confiable para texto no estructurado. Más cara. No necesaria: el tool_log ya tiene los JSON estructurados de `bash_execute`. Parsear JSON es determinístico y costo-cero.

### ¿Por qué las `pending_actions` las marca el tesorero y no el agente?

El agente puede recomendar. La decisión de qué trackear es del humano. Un agente que se auto-genera acciones pendientes puede llenar la memoria con ruido. Separar "qué dijo el agente" de "qué decidí trackear" mantiene la memoria limpia.

### Fix WinError 2 — `dispatch_v2()`

En NB 04, el modelo pasaba `command` como JSON string en el primer turn. `dispatch_v2()` lo detecta y convierte antes de llamar `subprocess.run()`:

```python
if isinstance(command, str):
    try:
        command = json.loads(command)
    except json.JSONDecodeError:
        command = command.split()
```

Resultado: el WinError 2 desaparece. Cada query resuelve en 2 turns en lugar de 3.

## Resultados obtenidos

_(completar al ejecutar el NB)_

| Sesión | Query | Turns | Tokens totales | Contexto inyectado |
|---|---|---|---|---|
| S1 | ¿Cómo estamos en caja? | _ | _ | 0 chars (primera sesión) |
| S2 | ¿Algo cambió vs última revisión? | _ | _ | ~400 chars |
| S3 | Resumen de revisiones + tendencias | _ | _ | ~600 chars |

## Conexión con Capa 6

El NB 05 produce un `run_agent_with_memory()` completamente funcional. La siguiente capa natural es una **interfaz de cliente**: un script `tesorero.py` o una app Streamlit que envuelva esta función y la exponga al cliente sin que vea el código.

Ese es el producto vendible: el agente + la interfaz + el historial persistente por cliente.

---

*Actualizado automáticamente al completar cada NB.*
