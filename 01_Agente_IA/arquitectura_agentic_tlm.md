# Análisis Arquitectónico — agentic-tlm
**Fuente:** https://github.com/chrisshayan/agentic-tlm  
**Analizado:** Mayo 2026 · Código fuente leído directamente (src/agents/, src/core/)  
**Propósito:** Blueprint de diseño para el Financial Pulse — Capa 4 y arquitectura multi-agente

---

## El Hallazgo Clave

El `MessageBus` del repo NO usa Kafka en su implementación real — usa `asyncio.Queue()` nativo de Python. Kafka aparece en `requirements.txt` como opción de escala para producción enterprise, pero el **patrón funciona con Python puro**. Esto significa que la arquitectura completa es replicable en tu entorno actual (Python 3.11 + anthropic) sin infraestructura externa.

---

## Estructura de Archivos Relevantes

```
src/
├── agents/
│   ├── base_agent.py      ← Clase abstracta que heredan todos los agentes
│   ├── cffa.py            ← Cash Flow Forecasting Agent
│   ├── loa.py             ← Liquidity Optimization Agent
│   ├── mmea.py            ← Money Market Execution Agent
│   ├── rha.py             ← Risk & Hedging Agent
│   ├── rra.py             ← Regulatory Reporting Agent
│   └── taaa.py            ← Treasury Analytics & Advisory Agent
└── core/
    ├── message_bus.py     ← Bus pub/sub central (asyncio.Queue)
    ├── orchestrator.py    ← Coordinador central (registro + health)
    ├── data_pipeline.py   ← Pipeline de datos de mercado
    ├── monitoring.py      ← Métricas y observabilidad
    └── security.py        ← JWT + autenticación
```

---

## Patrón 1 — BaseAgent (Clase Abstracta)

Todos los agentes heredan de `BaseAgent(ABC)`. El contrato que deben implementar:

```python
class BaseAgent(ABC):

    # OBLIGATORIOS — cada agente implementa su lógica aquí
    @abstractmethod
    async def _initialize(self):   # Setup inicial (conexiones, modelos, etc.)
        pass

    @abstractmethod
    async def _main_loop(self):    # Lógica principal — se ejecuta en loop continuo
        pass

    @abstractmethod
    async def _cleanup(self):      # Limpieza al apagar
        pass

    @abstractmethod
    async def _handle_message(self, message: Message):  # Respuesta a mensajes
        pass
```

**Ciclo de vida completo:**
```
STOPPED → STARTING → RUNNING → STOPPING → STOPPED
                  ↘ ERROR ↗
```

**Lo que BaseAgent provee automáticamente:**
- `start()` / `stop()` / `restart()` / `health_check()`
- Heartbeat automático cada 30 segundos via `MessageBus`
- Contador de errores + auto-reporte al orquestador
- Métricas: `messages_processed`, `errors_encountered`, `uptime_seconds`
- `_shutdown_event` (asyncio.Event) para parada limpia

**Estado interno que mantiene cada agente:**
```python
self.status          # AgentStatus enum
self.start_time      # datetime
self.last_heartbeat  # datetime
self.error_count     # int
self.last_error      # str
self.metrics         # dict con contadores
self.config          # dict de configuración
```

---

## Patrón 2 — MessageBus (Pub/Sub con asyncio.Queue)

El bus de comunicación entre agentes. Implementación real: **~80 líneas de Python puro**.

```python
class MessageBus:
    def __init__(self):
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.message_queue = asyncio.Queue()   # ← sin Kafka, sin Redis

    # Registrar handler para un tipo de mensaje
    def subscribe(self, message_type: MessageType, handler: Callable):
        self.subscribers[message_type].append(handler)

    # Publicar un mensaje (cualquier agente puede llamar esto)
    async def publish(self, message: Message):
        await self.message_queue.put(message)

    # Loop interno — entrega mensajes a suscriptores
    async def _process_messages(self):
        while self.is_running:
            message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
            await self._deliver_message(message)
```

**Tipos de mensajes definidos (MessageType enum):**
```python
AGENT_HEARTBEAT        # "sigo vivo" — cada 30 segundos
AGENT_ERROR            # error reportado por un agente
SYSTEM_ALERT           # alertas de umbral (liquidez, VaR)
SYSTEM_SHUTDOWN        # apagado coordinado
CASH_FLOW_FORECAST     # output del agente CFFA
LIQUIDITY_ALERT        # alerta del agente LOA
RISK_ALERT             # alerta del agente RHA
PORTFOLIO_OPTIMIZATION # recomendación del agente LOA
MARKET_UPDATE          # datos de mercado actualizados
FORECAST_UPDATE        # actualización de pronóstico
SYSTEM_STATUS          # estado general del sistema
```

**Flujo de un mensaje:**
```
Agente A → publish(Message) → asyncio.Queue → _deliver_message() → handler de Agente B
```

---

## Patrón 3 — AgentOrchestrator (Coordinador Central)

El orquestador es el único componente que conoce a todos los agentes. Los agentes no se conocen entre sí — solo se comunican via MessageBus.

**Responsabilidades:**
1. Registro de agentes con grafo de dependencias
2. Arranque en orden topológico (dependencias primero)
3. Parada en orden inverso
4. Health check cada 30 segundos
5. Auto-recovery: `restart` si heartbeat viejo, `stop` si error crítico
6. Loop de coordinación cada 10 segundos (backpressure, deadlock detection)

**Registro con dependencias:**
```python
orchestrator.register_agent(cffa_agent, dependencies=[])
orchestrator.register_agent(loa_agent, dependencies=["cffa_id"])
orchestrator.register_agent(mmea_agent, dependencies=["loa_id", "cffa_id"])
```

**Arranque en orden topológico:**
```python
# El orquestador resuelve: ¿quién puede arrancar ahora?
ready = [aid for aid in remaining
         if agent_dependencies[aid].issubset(started)]
```

**Estrategias de recovery automático:**
```python
recovery_strategy = {
    "stale_heartbeat":      "restart",
    "health_check_failed":  "restart",
    "communication_error":  "restart",
    "critical_error":       "stop"
}
```

---

## Los 6 Agentes Especializados

| Agente | Sigla | Función | Update interval |
|--------|-------|---------|----------------|
| Cash Flow Forecasting | CFFA | Pronóstico de flujo de caja (LSTM/Transformer) | 60 seg |
| Liquidity Optimization | LOA | Optimización de liquidez + alertas de umbral | 30 seg |
| Money Market Execution | MMEA | Ejecución en mercado de dinero | 10 seg |
| Risk & Hedging | RHA | VaR, pruebas de estrés, cobertura | 120 seg |
| Regulatory Reporting | RRA | Reportes regulatorios automáticos | 300 seg |
| Treasury Analytics & Advisory | TAAA | Q&A en lenguaje natural, análisis ad-hoc | 5 seg |

---

## Qué Necesitas para Replicar Este Patrón

Lo que el patrón realmente requiere (sin la infraestructura enterprise):

```bash
# Ya tienes:
anthropic==0.104.1   # LLM calls
pydantic>=2.0        # validación de datos

# Necesitas agregar:
pip install langchain langchain-anthropic   # orquestación LLM
pip install structlog                       # logging estructurado
pip install python-dotenv                  # gestión de .env

# Opcional para Capa 4 (Memory Store):
pip install mem0ai          # memoria persistente para agentes
pip install chromadb        # base vectorial local
```

**Lo que NO necesitas para replicar el patrón:**
- ❌ PostgreSQL / Redis / InfluxDB (solo para escala enterprise)
- ❌ Apache Kafka (asyncio.Queue hace lo mismo en escala pequeña)
- ❌ PyTorch / TensorFlow (reemplaza LSTM con llamadas a Claude)
- ❌ Ray RLLib (reinforcement learning para trading real)
- ❌ Bloomberg API (reemplaza con yfinance gratuito o datos propios)

---

## Blueprint para Financial Pulse — Capa 4

Aplicando este patrón al Financial Pulse con tus herramientas actuales:

```
Financial Pulse Multi-Agent (tu versión)
├── BaseAgent               ← copiar patrón directamente
├── MessageBus              ← copiar implementación asyncio.Queue (~80 líneas)
├── AgentOrchestrator       ← simplificar (sin Prometheus, sin Kafka)
│
├── agents/
│   ├── forecasting_agent.py    ← equivalente a CFFA (usa Claude + tus datos)
│   ├── analysis_agent.py       ← equivalente a TAAA (Q&A financiero)
│   └── reporting_agent.py      ← equivalente a RRA (genera reportes)
│
└── core/
    ├── message_bus.py      ← asyncio.Queue puro
    ├── orchestrator.py     ← versión simplificada
    └── memory_store.py     ← Capa 4: mem0 + chromadb (NO está en agentic-tlm)
```

**El patrón de 3 capas que extrae este análisis:**
```
Capa de Agentes     →  BaseAgent + lógica de dominio (Claude API)
Capa de Mensajes    →  MessageBus (asyncio.Queue pub/sub)
Capa de Coordinación → AgentOrchestrator (lifecycle + health + recovery)
```

La Capa 4 (Memory Store) que falta en `agentic-tlm` se agrega con `mem0` + `chromadb`: persistencia de contexto entre sesiones del agente.

---

## Referencia Cruzada

- `docs/repositorios_agentes_financieros_contables.md` — lista completa de repos
- `Skill_financiero/PROYECTO.md` — estado actual del Financial Pulse (Capas 1-3 completas)
- Para implementar Capa 4: ver stack `mem0 + chromadb` en sección "Qué Necesitas"

---

*Análisis de código fuente directo — Mayo 2026 · Proyecto Gabriel Untiveros*
