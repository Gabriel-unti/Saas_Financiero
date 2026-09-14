# Desglose diario — Agente Contable (Financial Pulse), semanas 1-8

## Contexto

Gabriel está construyendo "Financial Pulse", un SaaS financiero para PYMEs peruanas, en 7.5h/semana (L-V 9-10pm, sáb 3-4pm, dom 12-1pm + checkpoint dom 1-1:15pm). Ya se acordó un plan semanal de 8 semanas con el Agente Contable como prioridad #1 (registro de compras, ventas y libro diario), seguido de outreach obligatorio en la semana 5 y el Agente Tesorero como siguiente módulo.

Este documento desglosa esas 8 semanas en tareas diarias concretas (una por sesión de ~1h), para que cada bloque de calendario tenga una acción clara y ejecutable — sin necesidad de decidir "qué toca hoy" al sentarse.

**Investigación que fundamenta este desglose** (hecha por 2 agentes Explore):
- El pipeline real de facturas de su trabajo (`actualizar-facturas-proveedores`, `extraer_facturas.py`, `Libro_Diario_Braidy_Wonders.xlsx`) — de ahí se reutiliza el *patrón* de extracción (pdfplumber) y la tabla de mapeo código SPOT → cuenta de gasto (631/632/634/635/639), pero NO el enfoque Excel+COM (frágil, atado a Windows, single-tenant) ni los datos de esa empresa.
- El documento `01_Agente_IA/agente_contable_base_conocimiento.md` del repo `Saas_Financiero` — especificación completa de 9 módulos (clasificación, crédito fiscal, deducibilidad, asientos PCGE, IGV, detracciones/retenciones/percepciones, flujo operativo, cuentas PCGE, calendario). **No existe código todavía**, solo esta especificación.

**Decisiones ya confirmadas con el usuario:**
1. **Datos de prueba:** comprobantes 100% sintéticos/inventados (RUCs y montos ficticios) — nunca datos reales de su empleador (Braidy Wonders), que no son suyos para un proyecto comercial personal.
2. **Entorno:** el código se escribe en un clon local del repo `Saas_Financiero` en su laptop/PC personal, separado del entorno de Tesorería de su trabajo. El Día 1 incluye ese setup.
3. **Alcance MVP (4 semanas):** solo compras + ventas + libro diario + IGV básico (18%, sin prorrata) + detracciones (tabla SPOT ya validada). Quedan en backlog v2 (después del checkpoint de la semana 5): árbol de deducibilidad, retenciones/percepciones, notas de crédito/débito, prorrata IGV, planilla, monitor de alertas SUNAT.

## Alcance técnico del MVP (semanas 1-4)

Motor Python (no Excel+COM) que reutiliza el modelo de datos JSON del knowledge base:
- **Objeto comprobante:** tipo, RUC emisor/receptor, fecha, concepto, base imponible, IGV, total, medio de pago, aplica_detracción, tasa.
- **Objeto asiento:** debe/haber (cuenta, nombre, monto), detracción, flujo neto.
- Cuentas PCGE usadas: 60/63x (compra), 4012 (IGV crédito fiscal), 421 (CxP); 121 (CxC), 701 (ventas), 4011 (IGV débito); 104 (bancos) para pagos/cobros opcionales.
- Tabla SPOT reutilizada tal cual del pipeline de Tesorería: `026/027→631`, `022→632`, `020→634`, `019→635`, `021/024/037→639`.

## Desglose diario

### Semana 1 (14-20 sep) — Registro de Compras

| Día | Tarea (≈1h) |
|---|---|
| Lun 14 | Setup: clonar `Saas_Financiero` en la laptop personal, crear carpeta `agente_contable/` (`src/`, `data/`, `samples/`, `tests/`), entorno virtual, instalar `pdfplumber`, `openpyxl`, `pandas`. |
| Mar 15 | Crear 8-10 comprobantes de compra sintéticos cubriendo casos reales: factura gravada con detracción, factura gravada sin detracción, RHE (sin IGV), boleta. Documentar los campos esperados en un CSV de referencia. |
| Mié 16 | Adaptar el patrón de `extraer_facturas.py` (pdfplumber) a un extractor genérico y desacoplado de una sola empresa: `parse_invoice(pdf_path) -> dict` con los campos base. Probar contra 2-3 comprobantes sintéticos. |
| Jue 17 | Completar extracción para el resto del set sintético. Manejar explícitamente el caso RHE (nunca derivar `Valor_Venta` como `Total/1.18` cuando no hay IGV — regla ya aprendida en el pipeline de Tesorería). |
| Vie 18 | Clasificador de tipo de comprobante + afectación (gravado/exonerado/inafecto) y validación de formato de RUC (11 dígitos). Sin llamada a SUNAT todavía. |
| Sáb 19 | Motor de cálculo de detracción: portar la tabla SPOT→cuenta de gasto + regla de umbral (>S/700). |
| Dom 20 (12-1pm) | Generador de asiento PCGE de compra (Dr 60x/63x + Dr 4012 / Cr 421). Probar contra todo el set sintético y verificar Debe=Haber en cada asiento. |
| Dom 20 (1-1:15pm) | **Checkpoint semanal #1.** |

### Semana 2 (21-27 sep) — Registro de Ventas

| Día | Tarea |
|---|---|
| Lun 21 | Diseñar el objeto de venta (espejo del de compra: Dr 121 / Cr 701 + Cr 4011). Crear 6-8 comprobantes de venta sintéticos (facturas emitidas). |
| Mar 22 | Definir formato de entrada para ventas (¿PDF propio o CSV/formulario simple? — más simple que compras porque el dato lo genera él mismo) y construir el parser correspondiente. |
| Mié 23 | Clasificador de venta: gravada/exonerada/inafecta + cálculo de IGV débito. |
| Jue 24 | Generador de asiento PCGE de venta. Probar contra el set sintético. |
| Vie 25 | Probar casos límite: venta exonerada (sin IGV), venta al crédito vs. al contado. |
| Sáb 26 | Asientos opcionales de pago/cobro: pago a proveedor (Dr 421/Cr 104) y cobro a cliente (Dr 104/Cr 121) cuando exista fecha de pago/cobro. |
| Dom 27 (12-1pm) | Prueba de integración: correr compras + ventas sintéticas juntas, revisar consistencia de cuentas PCGE usadas. |
| Dom 27 (1-1:15pm) | **Checkpoint semanal #2.** |

### Semana 3 (28 sep-4 oct) — Libro Diario Consolidado

| Día | Tarea |
|---|---|
| Lun 28 | Diseñar la estructura del Libro Diario consolidado como DataFrame (fecha, glosa, cuenta, debe, haber, referencia al comprobante origen). |
| Mar 29 | Función que combina todos los asientos (compras+ventas) en orden cronológico dentro del Libro Diario. |
| Mié 30 | Validación de cuadre: `sum(Debe) == sum(Haber)` por asiento y en total — versión Python del check que ya usa en Tesorería (antes hecho con fórmula Excel). |
| Jue 1 oct | Control de detracciones simplificado: fecha límite (5° día hábil del mes siguiente) + columna de alerta VENCIDA/POR VENCER, mismo patrón que `Detracciones_Control`. |
| Vie 2 | Resumen de IGV del período: IGV ventas − IGV compras = IGV a pagar/saldo a favor (sin prorrata, fuera de alcance MVP). |
| Sáb 3 | Manejo de casos raros: comprobante sin fecha, RUC inválido, moneda extranjera — marcar "NO VISIBLE" en vez de inventar el dato (regla ya validada en el pipeline real). |
| Dom 4 (12-1pm) | Prueba end-to-end completa con todo el set sintético; corregir bugs encontrados. |
| Dom 4 (1-1:15pm) | **Checkpoint semanal #3.** |

### Semana 4 (5-11 oct) — Empaquetar como demo presentable

| Día | Tarea |
|---|---|
| Lun 5 | Diseñar el Excel de salida: hojas "Libro Diario", "Registro Compras", "Registro Ventas", "Resumen IGV", "Control Detracciones". |
| Mar 6 | Construir `export_to_excel(...)` con formato (encabezados, colores, anchos) vía `openpyxl`. |
| Mié 7 | Hoja de portada tipo "Financial Pulse — Reporte Contable" con métricas clave (total compras, ventas, IGV a pagar, detracciones pendientes) — lo primero que vería un prospecto. |
| Jue 8 | Pulir presentación: nombre/branding (revisar `00_Perfil_Personal/RESUMEN_Marca_Untiveros.md` y `.claude/tonalidad_voz.md` del repo para consistencia de tono). |
| Vie 9 | Grabar demo corto (2-3 min): "subes comprobantes → obtienes libro diario + resumen". Este material se usa en el outreach de la semana 5. |
| Sáb 10 | Preparar borrador del mensaje de outreach + primera lista de candidatos a prospecto (sin enviar todavía). |
| Dom 11 (12-1pm) | Repaso final: correr el demo de punta a punta, revisar que no haya bugs visibles antes del checkpoint de la semana 5. |
| Dom 11 (1-1:15pm) | **Checkpoint semanal #4.** |

### Semana 5 (12-18 oct) — Outreach (checkpoint no negociable)

| Día | Tarea |
|---|---|
| Lun 12 | Armar lista de 15-20 prospectos candidatos (LinkedIn, conocidos, grupos de contadores) — más de los 5 necesarios, para tener margen. |
| Mar 13 | Investigar cada prospecto (qué hacen, tamaño, posible dolor contable) y priorizar los 5 más prometedores. |
| Mié 14 | Escribir el mensaje de outreach (plantilla + 2-3 variantes según tipo de prospecto). |
| Jue 15 | Preparar material de apoyo: demo grabado + 1-pager de lo que resuelve el Agente Contable. |
| Vie 16 | Revisar tono del mensaje contra `.claude/tonalidad_voz.md`; ajustar. |
| Sáb 17 | Buffer — margen para cerrar pendientes atrasados de la semana. |
| Dom 18 (11:45-12pm) | **🚨 CHECKPOINT NO NEGOCIABLE: enviar el primer mensaje a los 5 prospectos.** No depende de que el producto esté "perfecto". |
| Dom 18 (1-1:15pm) | **Checkpoint semanal #5** — reportar qué pasó con el outreach. |

### Semanas 6-7 (19 oct-1 nov) — Iterar según respuestas

Estas dos semanas dependen de datos que todavía no existen (si responden o no, qué piden). En vez de tareas fijas, el marco diario es:
- **Si alguien respondió:** agendar llamada/reunión, escuchar su caso real, anotar gaps entre el MVP y lo que pide.
- **Si no respondió en 3-4 días:** enviar un segundo mensaje de seguimiento (no más de uno).
- **El resto del tiempo libre de cada semana:** ajustar el Agente Contable según el feedback recibido (priorizar sobre el backlog v2 solo lo que un prospecto real pidió).
- Si para el jueves de la semana 6 nadie respondió a los 5 originales: día de esa semana dedicado a ampliar la lista y mandar mensaje a 5 prospectos más (mismo patrón de la semana 5, sin esperar al siguiente checkpoint de revisión).

### Semana 8 (2-8 nov) — Revisión de mes 2

| Día | Tarea |
|---|---|
| Lun-Vie | Cerrar cualquier ajuste pendiente del feedback de prospectos. |
| Sáb | Documentar qué se aprendió (qué funcionó del MVP, qué faltó, qué pidieron los prospectos). |
| Dom (12-1pm) | Con datos reales (no suposiciones): decidir si el siguiente módulo es el Agente Tesorero (ya semi-construido en `01_Agente_IA/Skill_financiero/`) u otra prioridad que haya surgido del contacto con prospectos. |
| Dom (1-1:15pm) | **Checkpoint semanal #8** — cierre de los primeros 2 meses. |

## Archivos/carpetas de referencia (para reutilizar patrones, no copiar directo)
- `.claude/skills/actualizar-facturas-proveedores/SKILL.md` — reglas de extracción y registro contable ya validadas en producción.
- `FACTURAS_PROVEEDORES/extraer_facturas.py` — patrón de extracción PDF con `pdfplumber`.
- `DOCUMENTACION TECNICA/Registro_Contable_Libro_Diario.md`, `Guia_Detracciones_SUNAT_Braidy_Wonders.md` — reglas PCGE/detracciones aplicadas.
- (En el repo `Saas_Financiero`, a clonar localmente) `01_Agente_IA/agente_contable_base_conocimiento.md` — especificación completa de reglas contables/PCGE/IGV/detracciones a implementar.

## Siguiente paso tras aprobar este plan
Actualizar la descripción del bloque de trabajo L-V en el calendario (`Financial Pulse — bloque de trabajo (1h)`) y los bloques de sáb/dom para reflejar la tarea específica de cada día de las semanas 1-4, en vez del resumen semanal genérico actual.

## Verificación
No aplica ejecución de código en esta sesión (el desarrollo ocurre en el entorno local del usuario, fuera de este repo de Tesorería). La verificación es que el usuario revise el desglose y confirme que el ritmo diario es sostenible antes de empezar el lunes.
