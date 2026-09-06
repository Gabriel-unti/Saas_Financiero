# Repositorios GitHub — Agentes Financieros & Automatización Contable

**Fecha de compilación:** Mayo 2026  
**Fuente:** NotebookLM · Notebook `Financial Agent & Contabilidad — GitHub Research 2026`  
**Propósito:** Referencia técnica de repos open-source para desarrollo del proyecto de agentes contables y financieros.

---

## BLOQUE 1 — Agentes de Tesorería y Análisis Financiero

### 1. agentic-tlm — Treasury & Liquidity Management
**Link:** https://github.com/chrisshayan/agentic-tlm

**Qué hace:**  
Ecosistema de IA multi-agente diseñado para revolucionar las operaciones de tesorería en instituciones financieras. Opera como una malla de agentes (mesh architecture) donde seis agentes especializados coordinan tareas complejas de back-office a través de un orquestador central y un bus de mensajes. Automatiza desde el pronóstico de flujo de caja hasta el cumplimiento regulatorio y el análisis de mercado en tiempo real.

**Agentes especializados:** CFFA (Cash Flow Forecasting), LOA (Liquidity Optimization), MMEA (Money Market Execution), RHA (Risk & Hedging), RRA (Regulatory Reporting), TAAA (Treasury Analytics & Advisory).

**Stack técnico:**
- Python, FastAPI (servidor), Streamlit (panel interactivo)
- Modelos ML: LSTM, Transformer, Random Forest (para pronósticos)
- IA agéntica: Aprendizaje por Refuerzo Multi-agente (PPO), LangChain
- LLMs: GPT-4 Turbo, Claude 3 Sonnet
- Infraestructura: Docker, WebSocket para datos en tiempo real

**Casos de uso:**
- Gestión de liquidez y optimización de portafolios
- Pruebas de estrés (VaR)
- Generación de señales de trading
- Reportes regulatorios automáticos
- Asistencia mediante lenguaje natural (Q&A financiero)

**Relevancia para el proyecto:** El más cercano al Financial Pulse. Referencia directa para arquitectura multi-agente de tesorería y diseño de Capa 4 (Memory Store).

---

### 2. financial-ai-agent — Análisis Financiero con LangGraph
**Link:** https://github.com/lenaar/financial-ai-agent

**Qué hace:**  
Agente inteligente especializado en el análisis de datos financieros y realización de investigaciones comparativas de mercado. Automatiza flujos de trabajo procesando datos desde archivos CSV, realizando investigaciones de competidores en tiempo real y generando reportes detallados con bucles de retroalimentación interactivos.

**Stack técnico:**
- LangGraph (gestión de estados y ramificación condicional)
- LangChain (interacciones con LLM)
- Tavily Search (búsqueda de competidores en tiempo real)
- Streamlit (interfaz)
- Docker (despliegue, imagen basada en Python slim)

**Casos de uso:**
- Análisis de rendimiento financiero desde CSV
- Benchmarking de competidores automatizado
- Generación de reportes con feedback loops
- Soporte para toma de decisiones basada en datos

**Relevancia para el proyecto:** Arquitectura limpia LangGraph + CSV que se puede adaptar directamente para análisis de flujo de caja y KPIs de tesorería.

---

### 3. financial-agent — Agente LangChain + Polygon API
**Link:** https://github.com/virattt/financial-agent

**Qué hace:**  
Agente financiero ligero enfocado en la obtención de datos de mercado y valoración básica de empresas. Utiliza APIs financieras para acceder a precios actuales e históricos, noticias y datos fundamentales. Puede calcular métricas clave de inversión y realizar valoraciones sencillas por DCF.

**Stack técnico:**
- LangChain, FastAPI
- Polygon API (datos financieros de mercado)
- OpenAI API
- Poetry (gestión de dependencias)
- Docker

**Casos de uso:**
- Consulta de precios de acciones e históricos
- Análisis de noticias financieras en tiempo real
- Cálculo de métricas: ROE, ROIC, Owner Earnings
- Valoración por Flujo de Caja Descontado (DCF)

**Relevancia para el proyecto:** Código ligero y limpio ideal para estudiar integración LangChain + APIs externas. Punto de partida rápido para skills de consulta de mercado.

---

### 4. deep-research-agent-for-finance — Investigación Profunda con MCP
**Link:** https://github.com/The-AI-Alliance/deep-research-agent-for-applications

**Qué hace:**  
Aplicación de investigación profunda sobre empresas que cotizan en bolsa, con generación de reportes de inversión estructurados. Utiliza arquitectura de investigación iterativa: el LLM revisa el reporte hasta que está completo. Construido sobre el Model Context Protocol (MCP) de Anthropic.

**Stack técnico:**
- mcp-agent (basado en Model Context Protocol de Anthropic)
- OpenAI GPT-4o, Anthropic Claude, o inferencia local con Ollama (qwen3.5:35b, gpt-oss:20b)
- Servidores MCP: Yahoo Finance (yfmcp), mcp-remote
- Python 3.10+, gestor de paquetes `uv`, Makefile

**Casos de uso:**
- Análisis de rendimiento financiero de empresas cotizadas
- Resúmenes de noticias de mercado
- Evaluación de riesgos y oportunidades de inversión
- Análisis de sentimiento de inversores

**Relevancia para el proyecto:** Referencia clave para integración con MCP. Modelo de arquitectura para agentes que generan reportes iterativos y verificados.

---

## BLOQUE 2 — Automatización Contable y Procesamiento de Facturas

### 5. invoice-processing — GPT-4o + Pandas
**Link:** https://github.com/ruizguille/invoice-processing

**Qué hace:**  
Sistema de procesamiento de facturas con IA que extrae información relevante, realiza análisis financiero básico, valida los datos obtenidos y genera reportes finales en formato Excel. Maneja múltiples archivos de forma eficiente.

**Stack técnico:**
- Python, OpenAI GPT-4o, Pandas, Poetry

**Documentos que procesa:**
- Facturas en PDF (múltiples archivos en batch)

**Output:**
- Datos estructurados extraídos
- Análisis financiero básico
- Reporte final en Excel

**Relevancia para el proyecto:** El stack más directo y limpio para el Proyecto 5 (automatización contable). GPT-4o + Pandas es exactamente la combinación ya conocida. Fácil de adaptar.

---

### 6. llm-based-invoice-ocr — Vision LLM + OCR + FastAPI
**Link:** https://github.com/ShafqaatMalik/llm-based-invoice-ocr

**Qué hace:**  
Pipeline híbrido de OCR para facturas con dos modos de procesamiento: uno de pago vía API y uno open-source como respaldo. Extrae datos clave (número de factura, proveedor, fecha, ítems de línea, total) y los devuelve en formato JSON estructurado.

**Stack técnico:**
- FastAPI (backend), Gradio (frontend/interfaz)
- Tesseract OCR, pdf2image
- Together AI API con modelo Qwen2.5-VL-72B-Instruct (modo pago)
- Modo open-source como fallback

**Documentos que procesa:**
- PDFs (incluyendo multi-página)
- Imágenes de facturas

**Output:**
- JSON estructurado con campos extraídos

**Relevancia para el proyecto:** El stack más completo para facturas en imagen. FastAPI + Gradio permite montar una interfaz de demo para el piloto con Carlos Torres en horas.

---

### 7. invoice2data — Extracción con Plantillas YAML
**Link:** https://github.com/invoice-x/invoice2data

**Qué hace:**  
Herramienta de línea de comandos y librería Python para automatizar la extracción de información en procesos contables. Sistema basado en plantillas (YAML/JSON) que se adapta a diferentes diseños de facturas. Sin dependencia de LLM: puro parsing estructurado.

**Stack técnico:**
- Python
- Lectores: pdftotext, pdfminer, pdfplumber, Tesseract, Google Cloud Vision
- libyaml (mejora significativa de rendimiento)

**Documentos que procesa:**
- PDFs de facturas (principalmente)
- Adaptable a otros documentos de negocios

**Output:**
- CSV, JSON o XML con datos estructurados

**Relevancia para el proyecto:** Baseline sin costos de API. Útil para clientes con facturas de formato fijo (mismo proveedor repetido). Complementa los enfoques LLM para casos predecibles.

---

### 8. genai-invoice-processor — AWS Bedrock + Claude
**Link:** https://github.com/aws-samples/genai-invoice-processor

**Qué hace:**  
Solución AWS para procesar facturas almacenadas en S3. Extrae datos en formato clave-valor, genera resúmenes de documentos y los guarda en JSON. Incluye una aplicación Streamlit para revisar facturas y datos extraídos en paralelo.

**Stack técnico:**
- Python, Streamlit
- Amazon Bedrock, Anthropic Claude 3 Sonnet
- Amazon S3, AWS CLI

**Documentos que procesa:**
- PDFs de facturas (almacenados en S3)

**Output:**
- JSON con pares clave-valor extraídos
- Resumen del documento
- Interfaz de revisión visual

**Relevancia para el proyecto:** Referencia para cuando el piloto escale a infraestructura cloud. Arquitectura serverless con Claude ya conocido.

---

### 9. llm-rag-invoice-cpu — RAG Local sin GPU
**Link:** https://github.com/katanaml/llm-rag-invoice-cpu

**Qué hace:**  
Extracción de datos de facturas mediante RAG (Generación Aumentada por Recuperación) ejecutándose localmente en CPU. Convierte el texto de las facturas en embeddings vectoriales y permite consultas en lenguaje natural para extraer datos específicos.

**Stack técnico:**
- Python, Llama2 13B, LlamaCPP
- Haystack (framework RAG)
- Weaviate (base de datos vectorial)
- Docker

**Documentos que procesa:**
- PDFs de texto (no escaneados)

**Casos de uso:**
- Consultas: "¿Cuál es el número de factura?", "¿Cuánto es el IGV?"
- Procesamiento local sin dependencia de APIs externas
- Entornos sin conectividad o con restricciones de privacidad

**Relevancia para el proyecto:** Opción para clientes con restricciones de confidencialidad de datos. RAG sobre facturas es el patrón base para la Capa 4 del agente contable.

---

## BLOQUE 3 — Plataformas, Frameworks y Ecosistema

### 10. FinRobot — Plataforma Open-Source de Agentes Financieros
**Link:** https://github.com/AI4Finance-Foundation/FinRobot

**Qué hace:**  
Plataforma de agentes de IA de código abierto organizada en cuatro capas: agentes de IA financiera (con razonamiento Chain-of-Thought), algoritmos de LLM financieros, capas de LLMOps/DataOps y modelos base multi-fuente. Supera los enfoques de un solo modelo unificando LLM, reinforcement learning y analítica cuantitativa.

**Stack técnico:**
- GPT-4 Turbo, Claude 3 Sonnet
- Deep Learning: LSTM, Transformers
- Reinforcement Learning: PPO
- Financial Modeling Prep (FMP) API para datos

**Para qué sirve:**
- Automatizar investigación de inversiones
- Estrategias de trading algorítmico
- Evaluación de riesgos
- Asistente personal de Equity Research

**Relevancia para el proyecto:** La referencia más completa del ecosistema de agentes financieros. Estudiar su arquitectura de capas para diseñar el roadmap del Financial Pulse.

---

### 11. awesome-ai-in-finance — Lista Curada de IA Financiera
**Link:** https://github.com/georgezouq/awesome-ai-in-finance

**Qué contiene:**  
Lista curada de recursos sobre LLMs, estrategias de trading (alta frecuencia, criptomonedas, arbitraje), papers de investigación, cursos y libros. Repositorio central para investigadores y traders que usan IA para analizar y operar en mercados financieros.

**Herramientas cubiertas:**
- TA-Lib (análisis técnico)
- Zipline, Backtrader (backtesting)
- FinRL (reinforcement learning financiero)
- Frameworks de agentes y LLMs aplicados a finanzas

**Relevancia para el proyecto:** El mapa del ecosistema. Cargarlo como fuente de orientación para identificar herramientas específicas por caso de uso.

---

### 12. LLMs-in-Finance — Notebooks Prácticos con Múltiples Frameworks
**Link:** https://github.com/hananedupouy/LLMs-in-Finance

**Qué contiene:**  
Colección de Jupyter Notebooks prácticos que demuestran la aplicación de IA generativa en flujos de trabajo financieros reales. Dividido en tres áreas: Agentes de IA, RAG y modelos multimodales.

**Frameworks incluidos:**
- OpenAI Agents SDK
- AutoGen
- LlamaIndex
- CrewAI
- LangGraph
- LlamaParse (procesamiento de documentos)

**Casos de uso demostrados:**
- Análisis de reportes de ganancias (earnings reports)
- Bots de noticias financieras
- Estrategias de trading de impulso (momentum)

**Relevancia para el proyecto:** Notebooks listos para ejecutar y adaptar. La comparativa de frameworks (AutoGen vs CrewAI vs LangGraph) aplicada a finanzas reduce el tiempo de decisión de stack.

---

### 13. 500-AI-Agents-Projects — Catálogo de Casos de Uso
**Link:** https://github.com/ashishpatel26/500-AI-Agents-Projects

**Qué contiene:**  
Catálogo curado de más de 500 casos de uso y proyectos de agentes de IA organizados por industria (salud, finanzas, educación, legal, retail, etc.) con descripciones detalladas y enlaces a código fuente.

**Frameworks clasificados:**
- CrewAI
- AutoGen
- Agno (anteriormente Phidata)
- LangGraph

**Relevancia para el proyecto:** Fuente de inspiración para identificar verticales de consultoría. Buscar en la sección Finance los casos de uso más cercanos al perfil de clientes peruanos (PYMEs, contabilidad, tesorería).

---

### 14. awesome-ai-agents-2026 — Guía Completa del Stack 2026
**Link:** https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026

**Qué contiene:**  
Guía más completa y estructurada del stack tecnológico de agentes de IA para 2026, con más de 300 entradas que incluyen frameworks de orquestación, agentes de codificación, protocolos de comunicación y herramientas de infraestructura. Comparativas lado a lado y benchmarks.

**Herramientas cubiertas:**
- Protocolos: MCP (Model Context Protocol)
- Frameworks: PydanticAI, LangGraph, CrewAI
- Memoria: Mem0
- Bases de datos vectoriales: Pinecone
- Herramientas de infraestructura para producción

**Relevancia para el proyecto:** El mapa más actualizado del ecosistema. Referencia para decidir el stack de la Capa 4 (Memory Store) del Financial Pulse y para mantenerse al día con el mercado.

---

## Mapa de Decisión — Cuándo Usar Cada Repo

| Situación | Repo recomendado |
|-----------|-----------------|
| Diseñar arquitectura multi-agente de tesorería | `agentic-tlm` |
| Implementar Capa 4 Memory Store del Financial Pulse | `agentic-tlm` + `awesome-ai-agents-2026` |
| Procesar facturas PDF con LLM (piloto Proyecto 5) | `invoice-processing` (GPT-4o + Pandas) |
| Facturas en imagen o PDF escaneado | `llm-based-invoice-ocr` |
| Facturas de formato fijo, sin costo de API | `invoice2data` |
| Cliente con restricciones de privacidad/datos | `llm-rag-invoice-cpu` |
| Análisis financiero desde CSV + reportes | `financial-ai-agent` |
| Escalar infraestructura a cloud (AWS) | `genai-invoice-processor` |
| Comparar frameworks (CrewAI vs AutoGen vs LangGraph) | `LLMs-in-Finance` |
| Encontrar casos de uso por industria | `500-AI-Agents-Projects` |
| Orientación general del ecosistema IA financiero | `awesome-ai-in-finance` + `FinRobot` |

---

## NotebookLM

Todos estos repositorios están indexados en el notebook:  
**"Financial Agent & Contabilidad — GitHub Research 2026"**  
ID: `443f0d47-cc25-4ede-875f-c73979a1c138`

Para profundizar en cualquier repo, chatear directamente en NotebookLM con preguntas específicas sobre arquitectura, código o casos de uso.

---

*Compilado con notebooklm-py · Proyecto Gabriel Untiveros · Mayo 2026*
