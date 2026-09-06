# Guía Informativa: Implementación de Agentes de IA bajo el Plan Contable General Empresarial (PCGE) 2019

## 1. Resumen Ejecutivo

El presente documento sintetiza las bases técnicas y normativas del **Plan Contable General Empresarial (PCGE) Modificado 2019**, con el objetivo de orientar el desarrollo y perfilamiento de dos agentes de Inteligencia Artificial especializados para el sector de PYMEs en Perú. 

El PCGE 2019 actúa como la herramienta fundamental para el procesamiento de información contable, armonizada con las **Normas Internacionales de Información Financiera (NIIF)** y la **NIIF para PYMES**. Su estructura permite la acumulación estandarizada de hechos económicos a través de un catálogo de cuentas desarrollado hasta cinco dígitos. Para un estudio contable, la automatización mediante agentes de IA permite pasar de un registro manual a una gestión inteligente que cumple con la dualidad de la técnica de la partida doble y la esencia económica de las transacciones, independientemente de la formalidad legal.

## 2. Análisis de Temas Clave del PCGE 2019

### A. Estructura y Codificación (Base para el Algoritmo)
El PCGE se organiza en "Elementos" que definen la naturaleza de las cuentas. Para la lógica de programación de los agentes de IA, se deben considerar las siguientes categorías:

| Elemento | Descripción | Aplicabilidad del Agente |
| :--- | :--- | :--- |
| **1, 2, 3** | Activo (Disponible, Realizable, Inmovilizado) | Control de liquidez y existencias. |
| **4** | Pasivo (Obligaciones con terceros) | Gestión de cuentas por pagar y tributos. |
| **5** | Patrimonio Neto | Estructura de capital y resultados acumulados. |
| **6** | Gastos por Naturaleza | Clasificación de compras y servicios. |
| **7** | Ingresos | Registro de ventas y ganancias financieras. |
| **8** | Saldos Intermediarios | Determinación del resultado del periodo. |
| **9** | Contabilidad Analítica | Costos de producción y gastos por función. |

### B. Esencia Económica sobre Forma Legal
Un principio crítico para la IA es que el registro contable no depende exclusivamente de un documento formal. Según el numeral 2.2 de las Disposiciones Generales: *"En los casos en que la esencia de la operación se haya efectuado... corresponde efectuar el registro contable correspondiente, así no exista comprobante de sustento suficiente"*. Esto faculta a los agentes a realizar provisiones o devengos basados en contratos o flujos detectados.

### C. La Relación Contable-Tributaria
El PCGE es una herramienta contable, no tributaria. No obstante, incluye subcuentas para distinguir componentes con validez tributaria. Los agentes deben estar programados para priorizar las NIIF en caso de conflicto, manteniendo la integridad de la información financiera.

---

## 3. Perfilamiento de Agentes de IA

Basándose en la dinámica y el catálogo de cuentas del PCGE 2019, se definen los requerimientos técnicos para los dos agentes propuestos:

### (1) Agente Contable: Procesamiento y Registro
Este agente se enfoca en el flujo operativo de facturación y cumplimiento normativo.

*   **Procesamiento de Facturas Electrónicas:** Debe identificar y clasificar comprobantes usando las subcuentas **121** (Facturas por cobrar) y **421** (Facturas por pagar).
*   **Generación de Asientos PCGE:**
    *   **Ventas:** Utilización de la cuenta **70** (Ventas) contra la **12** (Cuentas por cobrar), desglosando el IGV en la cuenta **4011**.
    *   **Compras:** Registro en la cuenta **60** (Compras) o **63** (Servicios prestados por terceros), activando la dinámica de la cuenta **20** (Mercaderías) a través de la cuenta **61** (Variación de inventarios).
*   **Armado de Registros:** Debe construir los registros de Ventas y Compras asegurando que los saldos deudores y acreedores mantengan el balance de la partida doble.
*   **Gestión de Devengos:** Según el concepto de acumulación o devengo (Capítulo 1, Sección D), el agente debe reconocer los efectos de las transacciones independientemente del pago.

### (2) Agente Tesorero: Liquidez y Flujo de Caja
Este agente se enfoca en el Elemento 1 (Activo Disponible) y la proyección de obligaciones financieras.

*   **Flujo de Caja en Tiempo Real:** Monitoreo de la cuenta **10** (Efectivo y Equivalentes). Debe distinguir entre efectivo en caja (**101**), cuentas corrientes (**104**) y fondos sujetos a restricción (**107**).
*   **Gestión de Liquidez:** Análisis de la cuenta **11** (Inversiones Financieras) para excedentes y las cuentas **42** y **45** (Obligaciones Financieras) para compromisos de pago.
*   **Proyección de Posición de Caja:** 
    *   Uso de las subcuentas de "Cuentas por cobrar" (**12, 13, 14, 16**) para ingresos proyectados.
    *   Uso de "Cuentas por pagar" (**41, 42, 43, 44, 45, 46**) para egresos programados.
*   **Tratamiento de Moneda Extranjera:** El agente debe aplicar el tipo de cambio de cierre para expresar saldos en moneda nacional, conforme a la NIC 21 referenciada en la dinámica de la cuenta 10.

---

## 4. Citas Importantes y Contexto Operativo

> *"La contabilidad de las entidades se debe encontrar suficientemente detallada para facilitar la exposición de los hechos económicos... Las operaciones se deben registrar en las cuentas que corresponden a su naturaleza."* (Capítulo I, 1.1 y 1.2)

**Contexto:** Esta directriz justifica que el Agente Contable no solo registre el monto total, sino que clasifique detalladamente (hasta 5 dígitos) según la naturaleza de la transacción (ej. diferenciar entre mercaderías manufacturadas o servicios).

> *"La contabilidad basada en el concepto del devengo, representa los efectos de las transacciones y otros eventos... independientemente de la oportunidad de su pago."* (Capítulo I, Sección D, Marco Conceptual)

**Contexto:** Es la base para que el Agente Tesorero proyecte el flujo de caja; debe ser capaz de separar el momento del registro contable (devengo) del momento del movimiento de efectivo (percibido).

> *"El Plan se encuentra desarrollado hasta un nivel de cinco dígitos... Las entidades pueden incorporar dígitos adicionales, según les sea necesario."* (Capítulo I, Estructura de Cuentas)

**Contexto:** Permite que los agentes de IA se adapten a las necesidades específicas de cada PYME, añadiendo niveles de detalle por zona geográfica o línea de negocio sin romper la estructura básica.

---

## 5. Insights Accionables para el Estudio Contable

1.  **Automatización del "Match" Factura-Asiento:** El Agente Contable puede utilizar la dinámica de la **Cuenta 12** y **Cuenta 42** para conciliar automáticamente facturas con letras por cobrar/pagar, reduciendo el error humano en el canje de documentos.
2.  **Alertas de Cobranza Dudosa:** Mediante el análisis de la **Cuenta 19** (Estimación de cuentas de cobranza dudosa), la IA puede alertar preventivamente sobre clientes que están deteriorando su perfil de pago, impactando la proyección de caja del Agente Tesorero.
3.  **Optimización del IGV:** El Agente Contable debe supervisar la **Subcuenta 167** (Tributos por acreditar) para asegurar que el crédito fiscal del IGV por compras o servicios de no domiciliados sea compensado oportunamente en la **Cuenta 4011**.
4.  **Control de Activos Aptos:** Para PYMEs industriales, el agente debe identificar "activos aptos" según la NIC 23 para capitalizar costos de financiación en las cuentas de **Elementos 2 y 3**, algo que el PCGE 2019 permite explícitamente pero la NIIF PYMES restringe (un punto de control crítico para la IA).
5.  **Visibilidad de Arrendamientos:** Con la incorporación de la **Cuenta 32** (Activos por derecho de uso), el Agente Tesorero puede proyectar con precisión las salidas de caja por contratos de arrendamiento operativo de largo plazo, anteriormente tratados solo como gasto.