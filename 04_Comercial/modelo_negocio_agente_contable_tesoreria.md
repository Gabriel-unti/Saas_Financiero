# Modelo de Negocio: Agente de Automatización Contable + Integración de Tesorería

## Resumen Ejecutivo

Servicio de automatización financiera para PYMEs peruanas medianas: partimos de la automatización del ciclo contable (donde el dolor es inmediato y medible) y escalamos hacia un módulo de tesorería con predicción de cobranza y visibilidad de flujo de caja. El cliente entra por un problema concreto y barato de resolver, y se queda por un sistema que le da visión financiera que hoy no tiene.

---

## El Problema

La mayoría de PYMEs peruanas operan con Excel, sin equipo interno de automatización o análisis de datos. Consecuencias típicas:

- Cierres contables lentos y dependientes de trabajo manual repetitivo
- Cobranza reactiva: se actúa sobre la mora cuando ya es tarde, no antes
- Cero visibilidad predictiva de flujo de caja — decisiones basadas en lo que ya pasó, no en lo que viene
- Ningún sistema que cruce información contable con el estado real de tesorería

---

## La Solución: Dos Capas de Producto

### Capa 1 — Agente de Automatización Contable

Automatiza las tareas repetitivas del ciclo contable: conciliación de movimientos, clasificación de gastos/ingresos, generación de reportes periódicos, detección de inconsistencias.

**Pipeline de funcionamiento:**
1. Extracción de datos (Excel manual)
2. Limpieza y estructuración de la información (Python/Power Query)
3. Aplicación de reglas contables + modelos de IA para clasificación y detección de anomalías
4. Generación automática de reportes y alertas

### Capa 2 — Integración de Tesorería (upsell natural)

Una vez el dato contable está limpio y estructurado, se conecta a un módulo de tesorería que da:

- Visibilidad de flujo de caja proyectado
- Predicción de mora / riesgo de cobranza por cliente, usando modelos de machine learning
- Dashboard ejecutivo con priorización de cobranza (a quién llamar primero y por qué)
- Agente conversacional para consultar el estado financiero en lenguaje natural

Esta capa solo tiene sentido después de la Capa 1 — no se puede predecir sobre datos desordenados.

---

## Stack Tecnológico (herramientas que ya existen y funcionan)

| Herramienta | Uso |
|---|---|
| Python (pandas, scikit-learn, LightGBM) | Limpieza de datos y modelos predictivos de mora/cobranza |
| Power BI | Dashboards ejecutivos con storytelling visual |
| Microsoft Graph API | Automatización de flujos entre correo, Excel y Teams |
| Agente conversacional (IA) | Capa de consulta en lenguaje natural sobre datos financieros |

El portafolio ya incluye entregas reales en: dashboards de tesorería multi-moneda, segmentación de clientes, predicción de mora/churn B2B, y modelos de riesgo de cartera vencida — no es una propuesta teórica, es tecnología ya construida y probada.

---

## Target de Cliente (perfil ideal)

- PYME peruana mediana con volumen de facturación/transacciones suficiente para que la automatización genere ahorro medible
- Sectores prioritarios: construcción, agroindustria, retail, servicios financieros
- Perfil de dato: desde Excel puro hasta ERP con extracción manual — ambos casos son atendibles, cambia el esfuerzo de implementación
- Dolor identificable y verbalizable: cierres lentos, cobranza dispersa, cero visibilidad de caja
- Tamaño ideal: suficiente complejidad para justificar el servicio, pero sin equipo interno de datos que ya resuelva esto

---

## Modelo de Ingresos

- **Setup / implementación:** pago único, varía según complejidad (Excel puro vs. integración con ERP)
- **Retainer mensual:** mantenimiento, ajustes y soporte continuo
- **Upsell de tesorería:** segunda fase de contrato, ticket mensual adicional una vez la Capa 1 está funcionando
- **Filosofía comercial:** no vender el paquete completo desde el primer contacto — abrir con un diagnóstico acotado que demuestre valor numérico concreto (soles ahorrados o en riesgo) antes de escalar a contrato completo

---

## Pasos Previos para Poner en Marcha (con cualquier cliente nuevo)

1. **Diagnóstico inicial:** identificar dónde vive el dato (Excel, ERP, múltiples fuentes dispersas) y qué decisiones necesita soportar el cliente
2. **Acceso a datos de muestra:** 2-3 meses de información real (ventas, cobranzas, cartera, gastos)
3. **Piloto acotado (4-6 semanas):** entregable medible y específico — no automatización completa desde el día uno
4. **Validación del resultado:** cuantificar el hallazgo (soles en riesgo, horas ahorradas) como evidencia de valor
5. **Escalamiento:** pasar de piloto a retainer, y de retainer a la fase de integración de tesorería

---

## Diferenciador / Por Qué Ahora

- Combinación poco común en el mercado peruano: tesorería corporativa + Python + Power BI + IA + dominio de ERP
- Las consultoras grandes atienden solo empresas grandes (ticket alto, ciclos de venta largos); los freelancers sueltos no tienen profundidad técnica ni dominio financiero real
- La barrera de entrada no es la herramienta genérica — es la confianza para acceder a datos financieros sensibles y el conocimiento normativo contable local

---

## Roles Necesarios para Escalar (más allá de una sola persona)

- **Producto / tecnología:** construcción y mantenimiento de modelos, dashboards y agente
- **Validación normativa / credibilidad contable:** asegurar que las automatizaciones respeten reglas contables y tributarias peruanas
- **Desarrollo comercial:** prospección, calificación de leads, cierre y gestión de pipeline

Ningún rol reemplaza a los otros dos — el negocio escala solo si los tres funcionan en paralelo, no en serie.

---

## Riesgos a Vigilar

- Sin desarrollo comercial dedicado, el crecimiento depende de referidos puntuales y no es predecible
- La automatización puede percibirse como amenaza por quien hoy hace ese trabajo manual dentro del cliente — se gestiona esa relación, no solo se vende a la gerencia
- Escalar todo a medida (sin productizar) limita el crecimiento; el objetivo de mediano plazo es modularizar la oferta para no depender de trabajo artesanal por cliente
