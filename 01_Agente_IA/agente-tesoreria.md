# Agente de Tesorería — Documentación Técnica
**Gabriel Untiveros | Financial Pulse**  
**Versión:** 1.0 | **Fecha:** 2026-05-26

---

## 1. ¿Qué es este sistema?

Un agente conversacional que analiza liquidez empresarial usando la API de Anthropic (Claude). El tesorero escribe preguntas en lenguaje natural y recibe análisis estructurado: forecasts de caja, alertas por cuenta, reportes semanales.

**Diferencial técnico:** no es un chatbot genérico. Tiene acceso a datos reales del cliente, políticas de negocio configurables por empresa, y memoria persistente entre sesiones.

---

## 2. Arquitectura

```
Tu pregunta (tesorero.py)
        ↓
[Memoria SQLite] → inyecta historial en el system prompt
        ↓
Claude (claude-sonnet-4-6) — razona con contexto completo
        ↓
Decide qué herramienta usar
        ↓
bash_execute → ejecuta script Python local
   ó
read_skill   → lee política .md bajo demanda
        ↓
Recibe el resultado → interpreta → responde en español
        ↓
[Guarda sesión + estados en SQLite]
```

### Las 2 herramientas del agente

| Tool | Función | Por qué solo 2 |
|---|---|---|
| `bash_execute` | Ejecuta scripts Python en la máquina local | Un script procesa TODAS las cuentas en 1 llamada |
| `read_skill` | Lee archivos `.md` de política bajo demanda | El prompt se mantiene corto — las políticas entran solo cuando se necesitan |

### Los 3 SKILLs de tesorería

| Archivo | Cuándo se carga | Qué define |
|---|---|---|
| `forecast-cashflow/SKILL.md` | Al pedir proyecciones | Rolling mean vs método alternativo; interpretación de confidence |
| `alerta-tesoreria/SKILL.md` | Al revisar liquidez | CRÍTICO / ALTO / MEDIO / OK y sus umbrales por días de caja |
| `reporte-semanal/SKILL.md` | Al generar el reporte | Estructura del reporte ejecutivo semanal |

### Los scripts de cómputo

| Script | Input | Output |
|---|---|---|
| `batch_dias_de_caja.py` | `movimientos_diarios.csv` (todas las cuentas) | JSON array: `[{cuenta_id, saldo_actual, dias_de_caja, flujo_neto_dia, ...}]` |
| `rolling_mean_cashflow.py CUENTA-ID 14` | CSV + cuenta + horizonte | JSON: forecast individual |
| `generar_reporte.py` | `movimientos_diarios.csv` | Markdown: reporte semanal completo |

---

## 3. Estructura de archivos

```
Skill_financiero/
├── tesorero.py                          ← CLI principal (ejecutable)
├── .env                                  ← ANTHROPIC_API_KEY (no subir a git)
├── data/
│   ├── movimientos_diarios.csv           ← DATOS DEL CLIENTE (reemplazar con reales)
│   ├── reporte_semanal_ultimo.md         ← último reporte generado
│   └── memory/
│       └── agente_tesoreria.db           ← memoria SQLite (historial de sesiones)
├── .claude/
│   └── skills/
│       ├── forecast-cashflow/
│       │   ├── SKILL.md
│       │   ├── rolling_mean_cashflow.py
│       │   └── batch_dias_de_caja.py
│       ├── alerta-tesoreria/
│       │   └── SKILL.md
│       └── reporte-semanal/
│           ├── SKILL.md
│           └── generar_reporte.py
└── cwc_workshop/
    ├── 01_datos_simulados.ipynb
    ├── 02_cashflow_forecast.ipynb
    ├── 03_skills_tesoreria.ipynb
    ├── 04_loop_agentico.ipynb
    ├── 05_memory_store.ipynb
    └── GUIA_PASO_A_PASO.md
```

---

## 4. Cómo usar `tesorero.py`

### Requisitos previos

```bash
# 1. Activar el entorno virtual
D:\Proyecto_Gabriel\.venv\Scripts\activate

# 2. Verificar que el .env tiene la API key
# Archivo: Skill_financiero/.env
# Contenido: ANTHROPIC_API_KEY=sk-ant-...
```

### Iniciar el agente

```bash
cd D:\Proyecto_Gabriel\Skill_financiero
python tesorero.py
```

Al iniciar, el agente muestra el estado de memoria actual:
```
╔══════════════════════════════════════════════════╗
║   AGENTE DE TESORERÍA — Gabriel Untiveros        ║
║   CFO Interno | claude-sonnet-4-6                ║
╚══════════════════════════════════════════════════╝

  Historial: 3 sesión(es) guardada(s)
  Cuentas (último estado conocido):
    CUENTA-001: 🟢 OK | Saldo: 356,608 | Flujo/día: +1,969
    CUENTA-002: 🟢 OK | Saldo: 224,331 | Flujo/día: +1,289
    CUENTA-003: 🟢 OK | Saldo: 118,639 | Flujo/día: +187
```

### Preguntas que puede responder

```
Tú: ¿Cómo estamos en caja esta semana?
Tú: Genera el reporte semanal de tesorería
Tú: ¿Cuántos días de caja tiene CUENTA-002?
Tú: ¿Cuál es la cuenta con más riesgo y por qué?
Tú: ¿Cambió algo respecto a la última revisión?
Tú: Dame un resumen de las últimas 3 semanas
```

### Comandos especiales

| Comando | Función |
|---|---|
| `/historial` | Ver las últimas 5 sesiones (fecha, query, tokens usados) |
| `/pendientes` | Ver acciones pendientes registradas |
| `/hecho CLAVE VALOR` | Guardar configuración del cliente |
| `/completar N` | Marcar acción N como completada |
| `/reset` | Borrar toda la memoria (pide confirmación) |
| `/salir` | Salir |
| `/ayuda` | Lista de comandos |

### Opciones de línea de comandos

```bash
python tesorero.py                         # inicio normal
python tesorero.py --reset-memory          # borra historial y empieza fresco
python tesorero.py --db cliente_abc.db     # usa base de datos diferente (multi-cliente)
```

---

## 5. Formato del dataset

El agente procesa un CSV con esta estructura exacta:

```
cuenta_id,fecha,saldo_cierre,ingresos_dia,egresos_dia,moneda
CUENTA-001,2026-02-24,254544.34,19738.50,15194.16,PEN
CUENTA-001,2026-02-25,255123.13,17516.07,16937.29,PEN
...
CUENTA-002,2026-02-24,180000.00,45000.00,5000.00,PEN
...
CUENTA-003,2026-02-24,95000.00,2500.00,1800.00,USD
```

### Columnas requeridas

| Columna | Tipo | Descripción |
|---|---|---|
| `cuenta_id` | string | Identificador único de la cuenta (ej: `CUENTA-001`, o `BCP-PEN-01`) |
| `fecha` | YYYY-MM-DD | Fecha del registro |
| `saldo_cierre` | float | Saldo al cierre del día |
| `ingresos_dia` | float | Total de ingresos en el día |
| `egresos_dia` | float | Total de egresos en el día |
| `moneda` | string | `PEN` o `USD` |

### Reglas

- Mínimo recomendado: **60 días** por cuenta (el forecast necesita historia suficiente)
- Óptimo: **90 días** por cuenta
- Cada cuenta debe tener registros diarios continuos (sin saltar días)
- Múltiples cuentas en el mismo archivo, identificadas por `cuenta_id`

### Archivo destino

```
Skill_financiero/data/movimientos_diarios.csv
```

El agente siempre lee de esa ruta. Para un cliente nuevo: reemplazar ese archivo o crear un script de transformación.

---

## 6. Agregar datos reales de banco

### Opción A — Exportar desde el banco (más directa)

Los bancos peruanos permiten exportar movimientos a CSV o Excel:

| Banco | Cómo exportar |
|---|---|
| **BCP** | Banca por Internet → Cuentas → Movimientos → Exportar → Excel |
| **BBVA** | Banca Online → Mis Cuentas → Movimientos → Descargar → CSV |
| **Interbank** | Interbank.pe → Cuentas → Historial → Exportar a Excel |
| **Scotiabank** | Web → Cuentas → Extracto → Descargar CSV |

El extracto bancario tiene el formato bruto (fecha, descripción, monto, saldo). Necesita transformación para adaptarse al formato del agente.

Ver: `docs/transformar-datos-banco.md` (instrucciones de transformación por banco).

### Opción B — Dataset público para pruebas

Para una demo o piloto sin datos de cliente real:

- **Kaggle — Financial Transactions Dataset:**  
  `https://www.kaggle.com/datasets/ealaxi/paysim1`  
  Transacciones sintéticas de pagos móviles. Requiere transformación al formato del agente.

- **Synthea Financial Dataset:**  
  Datos sintéticos de empresas para simulación de tesorería.

### Opción C — Generar datos sintéticos calibrados

El NB 01 genera datos sintéticos con parámetros configurables (saldo inicial, volatilidad, patrones de planilla, eventos de estrés). Para calibrar a un cliente real: ajustar los parámetros con los promedios históricos del cliente.

---

## 7. Configuración por cliente (Multi-cliente)

Para usar el agente con diferentes clientes sin mezclar datos:

```bash
# Cliente A: Constructora Andina
python tesorero.py --db memoria_constructora_andina.db

# Cliente B: Trainyl
python tesorero.py --db memoria_trainyl.db
```

Cada `--db` tiene su propia memoria SQLite independiente. Los datos (`movimientos_diarios.csv`) se reemplazan antes de cada sesión, o se mantienen separados con un script de carga.

---

## 8. La capa de memoria

### Qué persiste entre sesiones

| Tabla SQLite | Contenido |
|---|---|
| `sessions` | Fecha, query, resumen, turns, tokens |
| `alertas` | Estado de cada cuenta por sesión (nivel, saldo, flujo/día) |
| `client_facts` | Configuración del cliente (ej: `CUENTA-002.alerta = Revisar día 15`) |
| `pending_actions` | Acciones recomendadas no completadas |

### Cómo se inyecta en el prompt

Al inicio de cada sesión, `build_context_block()` construye un bloque de texto con las últimas 3 sesiones, el estado actual por cuenta, las acciones pendientes y la configuración del cliente. Este bloque se añade al system prompt antes de que Claude reciba la pregunta del usuario.

Costo real del contexto histórico: ~300-500 tokens extra por sesión ≈ $0.001 adicional. Despreciable.

### Registrar acciones manualmente

```
/hecho CUENTA-002.alerta  Monitorear los días 13-15 (planilla BBVA)
/hecho cliente.nombre     Constructora Andina S.A.C.
/pendiente Revisar calendario pagos USD CUENTA-003
/completar 1
```

---

## 9. Modelo de costos

Basado en ejecuciones reales con `claude-sonnet-4-6`:

| Tipo de consulta | Turns | Tokens totales | Costo USD |
|---|---|---|---|
| Consulta de liquidez | 2–3 | ~7,000–9,000 | ~$0.025–0.035 |
| Reporte semanal | 2–3 | ~7,000 | ~$0.025 |
| Cuenta individual | 2–3 | ~7,000 | ~$0.025 |
| Con historial de memoria | +1 | +500–800 | +$0.001 |

**Proyección mensual:**

| Uso | Costo mensual estimado |
|---|---|
| 5 queries/semana (uso ligero) | ~$0.50 |
| 20 queries/semana (uso regular) | ~$2.00 |
| 50 queries/semana (uso intensivo) | ~$5.00 |

Para un cliente que paga S/ 500–1,500/mes, el margen operativo es >95%.

---

## 10. Solución de problemas

### El agente no encuentra el CSV

```
AssertionError: Falta .../batch_dias_de_caja.py
```
→ Ejecutar NB 02 y NB 03 para regenerar los scripts.

### Error de API key

```
ERROR: ANTHROPIC_API_KEY no encontrada.
```
→ Verificar que `Skill_financiero/.env` existe con `ANTHROPIC_API_KEY=sk-ant-...`

### El agente responde "no tengo datos"

→ Verificar que `data/movimientos_diarios.csv` tiene al menos 60 días de datos.  
→ El archivo debe tener exactamente las 6 columnas requeridas (ver Sección 5).

### El forecast devuelve `dias_de_caja: 999`

→ El valor 999 es el centinela para "flujo neto positivo". Significa que en el periodo analizado los ingresos superaron los egresos y no hay fecha proyectada de agotamiento de caja. No es un error — es el estado OK.

---

## 11. Desarrollo: cómo extender el agente

### Agregar un nuevo SKILL

1. Crear `Skill_financiero/.claude/skills/nuevo-skill/SKILL.md`
2. El agente lo carga automáticamente con `read_skill nuevo-skill/SKILL.md`
3. Agregar una línea al system prompt en `tesorero.py` indicando cuándo usarlo

### Agregar un nuevo script de cómputo

1. Crear el script en `.claude/skills/[categoria]/nuevo_script.py`
2. El script debe leer desde `Path(__file__).parent.parent.parent.parent / "data"` (4 niveles arriba del script)
3. Actualizar las rutas en el system prompt de `tesorero.py`

### Agregar multi-moneda

El CSV ya soporta múltiples monedas via la columna `moneda`. Los scripts de forecast calculan por separado PEN y USD. Para agregar EUR: agregar registros con `moneda=EUR` y el agente los procesa automáticamente.

---

*Documentación generada: 2026-05-26*  
*Stack: Python 3.11 · Anthropic SDK · SQLite · claude-sonnet-4-6*
