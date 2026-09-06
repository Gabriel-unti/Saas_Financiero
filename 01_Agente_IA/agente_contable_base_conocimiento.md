# Base de Conocimiento — Agente Contable
**Versión:** 1.0 | **Fecha:** Mayo 2026  
**Uso:** Referencia operativa para el Agente Contable (clasificación, validación, asientos, IGV, detracciones)  
**Fuentes:** PCGE 2019, TUO D.S. 055-99-EF, D. Leg. 1529, Ley 28194, R.S. 183-2004/SUNAT  

---

## MÓDULO 1 — Clasificación de Comprobantes de Pago

### 1.1 Tabla Maestra de Clasificación

| TIPO_DOCUMENTO | EMISOR_VÁLIDO | OTORGA_CRÉDITO_FISCAL | DEDUCIBLE_RENTA | REQUIERE_BANCARIZACIÓN | OBSERVACIONES |
|---|---|---|---|---|---|
| **Factura (01)** | RER, RMT, Régimen General | **SÍ** (si discrimina IGV) | **SÍ** (si cumple causalidad) | SÍ (≥ S/ 2,000 o $500) | CPE obligatorio desde día 1 para nuevos inscritos en RMT/RG (desde 01/06/2026) |
| **Boleta de Venta (03)** | NRUS, RER, RMT, Régimen General | **NO** | **NO** (regla general) | SÍ (≥ S/ 2,000 o $500) | Solo para consumidor final; no sustenta crédito fiscal |
| **Recibo por Honorarios (R1)** | Personas Naturales (4ta categoría) | **NO** (no gravado con IGV) | **SÍ** | SÍ (siempre, sin umbral mínimo) | Sujeto a retención de renta si supera tope legal |
| **Liquidación de Compra (04)** | PJ que compra a personas naturales sin RUC | **SÍ** (si el comprador retiene/paga IGV) | **SÍ** | SÍ (≥ S/ 2,000 o $500) | Para productos primarios, artesanía, desperdicios |
| **Tickets / Cintas** | Máquinas registradoras autorizadas | **SÍ** (si identifica RUC y desglosa IGV) | **SÍ** (si identifica al adquirente) | SÍ (≥ S/ 2,000 o $500) | Sin identificación del usuario: equivale a boleta (sin crédito/gasto) |
| **Nota de Crédito (07)** | El mismo emisor del comprobante original | **AJUSTA (resta)** crédito/débito | **AJUSTA (resta)** gasto/ingreso | SÍ (si el reembolso supera topes) | Obligatorio consignar serie y número del documento que modifica |
| **Nota de Débito (08)** | El mismo emisor del comprobante original | **AJUSTA (suma)** crédito/débito | **AJUSTA (suma)** gasto/ingreso | SÍ (si el nuevo total supera topes) | Para intereses por mora o recuperación de gastos incurridos |
| **Guía de Remisión (09/31)** | Remitente o Transportista | **NO** (documento de control) | **NO** (pero sustenta fehaciencia) | N/A | Obligatorio para traslado físico de bienes; evita comiso |
| **Comprobante de Retención** | Agente de Retención designado por SUNAT | **SÍ** (pago anticipado 3%) | N/A | N/A | Deduce contra IGV por pagar del periodo (Cta. 40114) |
| **Comprobante de Percepción** | Agente de Percepción designado por SUNAT | **SÍ** (pago anticipado 1%–10%) | N/A | N/A | El cliente lo usa como crédito contra su IGV (Cta. 40113) |

### 1.2 Regla de Bancarización (D. Leg. 1529 + Ley 28194)

| Escenario | Umbral S/ | Umbral USD | Norma |
|---|---|---|---|
| Operaciones generales | S/ 2,000 | USD 500 | D. Leg. 1529 (desde 01/04/2022) |
| Vehículos / Inmuebles / Capital | ≥ 1 UIT (S/ 5,300 en 2026) | Según T/C | Aplica incluso para pagos parciales |
| Remuneraciones / Beneficios | S/ 0.01 | — | D. Leg. 1499 (sin umbral mínimo) |

**Medios de pago admitidos:**
- MP01: Depósitos en cuenta
- MP02: Giros o transferencias de fondos
- MP03: Órdenes de pago
- MP04: Tarjetas de débito y crédito emitidas en el país
- MP05: Cheques con cláusula "no negociable" o "intransferible"

**Consecuencia del incumplimiento:** Pérdida irreversible del crédito fiscal IGV + pérdida de deducibilidad del gasto en IR, aunque la operación sea real.

---

## MÓDULO 2 — Validación de Crédito Fiscal (Art. 18 y 19 LGV)

### 2.1 Checklist Binario — Aprobación del Crédito Fiscal

Para que una factura otorgue crédito fiscal, deben cumplirse **todos** los criterios:

| Nivel | ID | Criterio | Referencia |
|---|---|---|---|
| **Sustancial (Art. 18)** | S1 | ¿El gasto es necesario para producir renta o mantener su fuente? (Causalidad) | Art. 18 num. 1 |
| **Sustancial (Art. 18)** | S2 | ¿La adquisición está destinada a operaciones gravadas con IGV? | Art. 18 num. 2 |
| **Formal (Art. 19)** | F1 | ¿El IGV está discriminado (detallado) en el comprobante? | Art. 19 |
| **Formal (Art. 19)** | F2 | ¿Contiene RUC, nombre/razón social del emisor y del adquirente? | Art. 19 |
| **Formal (Art. 19)** | F3 | ¿El emisor estaba "Activo" y "Habido" a la fecha de emisión? | Art. 19 |
| **Formal (Art. 19)** | F4 | ¿El documento cuenta con autorización de impresión o es CPE válido? | Art. 19 |
| **Formal (Art. 19)** | F5 | ¿Está anotado en el Registro de Compras (SIRE/RCE) dentro del plazo legal? | Art. 19 |

**Resultado:** Si algún criterio es 0 → crédito fiscal **RECHAZADO**.

### 2.2 Causales de Pérdida del Crédito Fiscal

Incluso con checklist positivo, el crédito se pierde si:

1. **Incumplimiento de bancarización:** Operación ≥ S/ 2,000 o $500 pagada en efectivo (Art. 3 y 4, Ley 28194)
2. **Operación no fehaciente:** No se puede acreditar que la operación ocurrió realmente (guías, contratos, entregables)
3. **Emisor no habido:** RUC con condición de domicilio "No Habido" al momento de la emisión
4. **No discriminación del IGV:** El emisor incluyó el IGV en el precio total sin separarlo
5. **Registro extemporáneo:** La anotación en el Registro de Compras se realizó después de una notificación de SUNAT
6. **Servicio de renta 5ta disfrazada:** SUNAT determina que la prestación genera renta de quinta categoría, no tercera
7. **Error en autorización de impresión:** Salvo que el pago total se haya bancarizado

---

## MÓDULO 3 — Deducibilidad de Gastos (Árbol de Decisión)

### 3.1 Algoritmo de Validación

```
PASO 1: ¿Es comprobante autorizado por SUNAT?
  └── NO → RECHAZO: Documento no válido
  └── SÍ → PASO 2

PASO 2: ¿Emisor Activo y Habido en SUNAT?
  └── NO → RECHAZO: Gasto no deducible
  └── SÍ → PASO 3

PASO 3: ¿Cumple Principio de Causalidad? (gasto necesario para producir/mantener renta)
  └── NO → RECHAZO: Gasto ajeno al negocio
  └── SÍ → PASO 4

PASO 4: ¿Monto ≥ S/ 2,000 o $500?
  └── SÍ → PASO 5
  └── NO → PASO 6

PASO 5: ¿Se usó Medio de Pago bancarizado?
  └── NO → RECHAZO: Incumplimiento Ley 28194 (pérdida de costo/gasto y crédito fiscal)
  └── SÍ → PASO 6

PASO 6: ¿El tipo de gasto tiene límite de deducibilidad?
  └── Gasto general (sin tope) → APROBADO: Deducible 100%
  └── Gasto con tope → PASO 7

PASO 7: ¿Excede el límite legal?
  └── SÍ → APROBADO PARCIAL: Deducible hasta el tope; reparar el exceso
  └── NO → APROBADO: Deducible 100%
```

### 3.2 Topes de Deducibilidad por Tipo de Gasto (PCGE)

| Cuenta PCGE | Tipo de Gasto | Límite |
|---|---|---|
| **62x** | Gastos recreativos (personal) | 0.5% de Ingresos Netos (tope en UIT) |
| **62x** | Aguinaldos / Bonificaciones | Deducible si se paga antes del plazo de DJ anual |
| **63x** | Asesoría / Consultoría | 100% si se acredita el servicio (entregables) |
| **63x** | Gastos de viaje (alojamiento/alimentación) | Límites por día según escala SUNAT |
| **65x** | Donaciones | Solo a entidades receptoras inscritas; límite 10% de Renta Neta |
| **64x** | Multas e intereses moratorios | **NO deducibles** — reparar en Cuenta 88 |

### 3.3 Matriz de Salida de Clasificación

| Resultado | Acción Contable PCGE | Acción Tributaria |
|---|---|---|
| **Aprobado** | Registro en Cta. 6x correspondiente | Deducción 100% en Renta |
| **Reparable (temporal)** | Cta. 6x + Activo Diferido (Cta. 37) | Adición este ejercicio; deducción futura |
| **Rechazado (permanente)** | Cta. 6x (gasto no deducible) | Adición permanente en DJ anual |

---

## MÓDULO 4 — Asientos Contables PCGE Típicos

### 4.1 Compra de Mercadería con Factura (a crédito, con IGV)

```
DEBE:
  601  Compras – Mercaderías              X
  4012 IGV – Crédito fiscal              X × 18%
HABER:
  421  Cuentas por pagar – Proveedores   X × 1.18
```
*Ajuste de existencias simultáneo:*
```
DEBE:
  20  Mercaderías                        X
HABER:
  611  Variación de existencias          X
```

### 4.2 Venta de Mercadería con Factura

```
DEBE:
  121  Cuentas por cobrar – Clientes     X × 1.18
HABER:
  701  Ventas – Mercaderías              X
  4011 IGV – Cuenta propia              X × 18%
```

### 4.3 Pago a Proveedor con Transferencia Bancaria

```
DEBE:
  421  Cuentas por pagar – Proveedores   X
HABER:
  104  Cuentas corrientes               X
```

### 4.4 Planilla Mensual

```
DEBE:
  621  Remuneraciones                    X bruto
HABER:
  411  Remuneraciones por pagar         X neto
  4032 ONP por retener                  13% de afecto
  4031 ESSALUD empresa                  9% (cargo empresa)
```

### 4.5 Nota de Crédito — Devolución de Mercadería

```
DEBE:
  4011 IGV – Cuenta propia             (-)  IGV devuelto
  709  Devoluciones sobre ventas           Valor devuelto
HABER:
  121  Cuentas por cobrar – Clientes   (-)  Total nota de crédito
```
*Para el receptor (comprador que devuelve):*
```
DEBE:
  421  Cuentas por pagar – Proveedores (-)  Total nota de crédito
HABER:
  4012 IGV – Crédito fiscal           (-)  IGV de la devolución
  601  Compras – Mercaderías          (-)  Valor devuelto
```

### 4.6 Nota de Crédito — Descuento Posterior a Emisión

```
DEBE:
  4011 IGV – Cuenta propia             IGV del descuento
  741  Descuentos concedidos           Monto del descuento
HABER:
  121  Cuentas por cobrar – Clientes   Total nota de crédito
```

### 4.7 Nota de Débito — Intereses por Mora

```
DEBE:
  121  Cuentas por cobrar – Clientes   Total nota de débito
HABER:
  4011 IGV – Cuenta propia             IGV de intereses
  772  Rendimientos financieros        Intereses netos
```

### 4.8 Impacto de Notas de Crédito/Débito en IGV

| Documento | Efecto IGV Emisor | Efecto IGV Receptor | Efecto IR Emisor | Efecto IR Receptor |
|---|---|---|---|---|
| **Nota de Crédito** | Disminuye débito fiscal | Disminuye crédito fiscal (obligatorio) | Reduce ingreso bruto/neto | Reduce costo/gasto deducible |
| **Nota de Débito** | Aumenta débito fiscal | Aumenta crédito fiscal | Aumenta ingreso gravable | Aumenta gasto deducible |

---

## MÓDULO 5 — IGV: Cálculo, Crédito y Clasificación de Operaciones

### 5.1 Datos Base

| Concepto | Valor |
|---|---|
| Tasa IGV | 16% |
| Tasa IPM (Impuesto de Promoción Municipal) | 2% |
| **Tasa combinada efectiva** | **18%** |
| Fórmula precio de venta | Base imponible × 1.18 |
| Base legal | TUO D.S. 055-99-EF y modificatorias |

### 5.2 Cálculo Mensual del IGV a Pagar

```
IGV de ventas (débito fiscal)          S/ X
(-) IGV de compras (crédito fiscal)    S/ Y
(-) Saldo a favor mes anterior         S/ Z
= IGV a pagar (o saldo a favor)        S/ resultado
```
Si resultado < 0 → saldo a favor del período siguiente.

### 5.3 Clasificación de Operaciones

| Tipo | Operaciones Comunes | Tasa | Impacto en Crédito Fiscal |
|---|---|---|---|
| **Gravadas** | Venta de bienes muebles, prestación de servicios en el país, construcción, primera venta de inmuebles, importación | 18% | IGV de compras → crédito fiscal |
| **Exoneradas** | Insumos agrícolas, hortalizas, frutas, libros, transporte público de pasajeros, espectáculos culturales | 0% | IGV de compras → gasto (Cta. 6411) o costo del activo |
| **Inafectas** | Indemnizaciones laborales, intereses entre empresas no financieras, transferencias por reorganización, exportaciones | No sujeto | IGV de compras → gasto o costo; exportaciones SÍ recuperan saldo a favor |

### 5.4 Diferencia Contable: Exoneradas vs. Inafectas

| Criterio | Exonerada | Inafecta |
|---|---|---|
| Naturaleza | Dentro del ámbito del IGV, pero liberada por ley | Fuera del ámbito del IGV (no incide) |
| Derecho al crédito fiscal | **No otorga** — el IGV de compras no se recupera | **No otorga** — salvo exportaciones (caso especial) |
| Tratamiento del IGV de compras | Se registra como gasto (Cta. 64) o costo del bien | Se registra como gasto o costo |
| Anotación SIRE | Columna de adquisiciones no gravadas | Columna de adquisiciones no gravadas |

### 5.5 Prorrata IGV — Operaciones Mixtas

Cuando la empresa realiza ventas gravadas **y** no gravadas:
```
Coeficiente = Ventas gravadas del periodo / Total ventas del periodo

IGV de compras × Coeficiente = Crédito fiscal (Cta. 1673 / 40111)
IGV de compras × (1 - Coeficiente) = Gasto o costo (Cta. 6411)
```

---

## MÓDULO 6 — Detracciones, Retenciones y Percepciones

### 6.1 Sistema de Detracciones (SPOT) — R.S. 183-2004/SUNAT

**Definición:** El comprador descuenta un porcentaje del pago total y lo deposita en la cuenta del Banco de la Nación del proveedor. Solo puede usarse para pagar tributos a SUNAT.

**Límite mínimo:** Solo aplica cuando la operación supera S/ 700.

#### Servicios sujetos a detracción (Anexo 3):

| Servicio | Tasa |
|---|---|
| Contratos de construcción | 4% |
| Transporte de carga por vía terrestre | 4% |
| Arrendamiento de bienes inmuebles | 10% |
| Arrendamiento de bienes muebles | 10% |
| Mantenimiento y reparación de bienes muebles | 10% |
| Comisión mercantil | 10% |
| Fabricación de bienes por encargo | 10% |
| Servicio de seguridad | 10% |
| Servicios empresariales (contabilidad, legal, consultoría) | 10% |
| Otros servicios empresariales | 10% |

#### Bienes sujetos a detracción (Anexo 2):

| Bien | Tasa |
|---|---|
| Recursos hidrobiológicos | 4% |
| Madera | 4% |
| Arena y piedra | 10% |
| Residuos, subproductos, desechos | 15% |
| Oro gravado con IGV | 10% |

#### Obligados y plazos:

| Obligado | Plazo |
|---|---|
| Adquirente / comprador (principal) | Hasta la fecha de pago al proveedor; sin pago en efectivo: hasta el 5to día hábil del mes siguiente de anotar en Registro de Compras |
| Proveedor (si el comprador no lo hizo) | Hasta el 5to día hábil del mes siguiente de anotar en Registro de Ventas |

#### Ejemplo de cálculo (servicio de construcción S/ 100,000 + IGV):

```
Valor neto:              S/ 100,000
IGV (18%):               S/  18,000
Total factura:           S/ 118,000

Detracción (4%):         S/   4,720  → Banco de la Nación (solo tributos)
Pago neto al proveedor:  S/ 113,280  → Cuenta corriente

Indicador de gestión: % fondos inmovilizados = Saldo detracciones / Ingresos del periodo
  Alerta si ratio > 5–8% (exceso de fondos sin liberar)
```

#### Liberación de fondos:
- Solicitar a SUNAT al final de 3 meses consecutivos si no hay deudas tributarias exigibles
- Plazo de resolución SUNAT: 30 días hábiles

### 6.2 Sistema de Retenciones del IGV

| Concepto | Detalle |
|---|---|
| Quién ejecuta | El **cliente** (Agente de Retención designado por SUNAT) |
| Umbral | Operaciones > S/ 700 |
| Tasa | **3%** del importe total |
| Documento | Comprobante de Retención |
| Clasificación contable (proveedor/receptor) | **Cta. 40114** (Retenciones acumuladas) o **Cta. 1673** (IGV por acreditar) |
| Uso | El proveedor compensa contra IGV por pagar del periodo |

### 6.3 Sistema de Percepciones del IGV

| Escenario | Tasa | Quién percibe | Clasificación contable (receptor) |
|---|---|---|---|
| Venta de combustible | 1% | Proveedor (grifo/distribuidor) | Cta. 40113 o Cta. 1673 |
| Ventas internas de bienes específicos | 2% | Proveedor designado | Cta. 40113 o Cta. 1673 |
| Importación (general) | 3.5% | SUNAT Aduanas | Cta. 40113 o Cta. 1673 |
| Importación (1ra vez) | 10% | SUNAT Aduanas | Cta. 40113 o Cta. 1673 |
| Importación (bienes usados) | 5% | SUNAT Aduanas | Cta. 40113 o Cta. 1673 |

**Clasificación contable del receptor:**
- Uso inmediato → Cta. 40114 (Retenciones) / Cta. 40113 (Percepciones)
- Pendiente de aplicación → Cta. 1673 (IGV por acreditar en compras)
- Ambas compensan automáticamente contra IGV por pagar (Cta. 4011)

---

## MÓDULO 7 — Flujo de Análisis de Comprobante (Algoritmo Operativo)

```
INPUT: {
  tipo_comprobante, ruc_emisor, ruc_receptor,
  fecha_emision, concepto, base_imponible, igv, total,
  medio_de_pago (si aplica)
}

PASOS DE VALIDACIÓN:
  1. Verificar tipo de comprobante → determinar qué registro contable aplica (ver Módulo 1)
  2. Verificar RUC del emisor → estado "Activo" y condición "Habido" en SUNAT (API consulta)
  3. Determinar si el IGV es crédito fiscal válido → aplicar checklist Módulo 2
  4. Determinar si aplica detracción → consultar Anexo 3 por tipo de servicio (ver Módulo 6.1)
  5. Clasificar el gasto/ingreso en cuenta PCGE → usar tablas Módulos 3 y 8
  6. Generar el asiento contable sugerido → usar plantillas Módulo 4
  7. Calcular el impacto en flujo de caja neto (descontando detracción si aplica)

OUTPUT: {
  asiento_debe:    {cuenta: "6XX", nombre: "...", monto: X},
  asiento_haber:   {cuenta: "42X", nombre: "...", monto: X × 1.18},
  credito_fiscal:  {aplica: true/false, monto: X × 0.18, condicion: "..."},
  detraccion:      {aplica: true/false, tasa: 0.04/0.10, monto: X × 1.18 × tasa},
  flujo_neto:      total - detraccion_si_aplica,
  alertas:         ["lista de observaciones"]
}
```

---

## MÓDULO 8 — Cuentas PCGE de Referencia Rápida

### Elemento 1 — Activo Disponible y Exigible

| Cuenta | Nombre | Sub-cuentas principales |
|---|---|---|
| **10** | Efectivo y equivalentes | 101 Caja, 104 Cuentas corrientes, 106 Depósitos instituciones financieras |
| **12** | CxC comerciales – Terceros | 121 Facturas por cobrar, 122 Anticipos de clientes |
| **13** | CxC comerciales – Relacionadas | 131 Facturas, 132 Anticipos |
| **14** | CxC al personal | 141 Préstamos, 142 Anticipos, 143 Entregas a rendir cuenta |
| **16** | CxC diversas – Terceros | 161 Préstamos a terceros, 165 Venta de activo inmovilizado |
| **18** | Servicios pagados por anticipado | 181 Costos prepagados, 182 Intereses por devengar |
| **19** | Estimación cobranza dudosa | 191 CxC comerciales – Terceros |

### Elemento 4 — Pasivo

| Cuenta | Nombre | Sub-cuentas clave |
|---|---|---|
| **40** | Tributos y aportes por pagar | Ver detalle abajo |
| **41** | Remuneraciones y participaciones | 411 Remuneraciones, 413 Participaciones, 415 Beneficios sociales |
| **42** | CxP comerciales – Terceros | 421 Facturas de proveedores, 422 Anticipos a proveedores |
| **44** | CxP accionistas/socios | 441 Accionistas, 444 Dividendos |
| **45** | Obligaciones financieras | 451 Préstamos bancarios, 452 Leasing |
| **46** | CxP diversas – Terceros | 469 Otras cuentas por pagar |
| **49** | Pasivo diferido | 491 IGV diferido |

#### Cuenta 40 — Detalle de Tributos

| Sub-cuenta | Nombre | Uso |
|---|---|---|
| **4011** | IGV – Cuenta propia | IGV de ventas a pagar a SUNAT |
| **4012** | IGV – Crédito fiscal (compras) | Deducción contra 4011 |
| **4013** | IGV – Percepciones acumuladas | Crédito de percepciones recibidas |
| **4014** | IGV en liquidación | IGV de importaciones |
| **4017** | Impuesto a la Renta | Pagos a cuenta mensuales |
| **4031** | ESSALUD | 9% de remuneraciones (cargo empresa) |
| **4032** | ONP | 13% de remuneraciones (retención trabajador) |
| **4071** | Detracciones | Fondos detraídos de cobros |
| **40114** | Retenciones IGV acumuladas | 3% retenido por agente |

### Elementos 6 y 7 — Gastos e Ingresos

#### Elemento 6: Gastos por Naturaleza

| Cuenta | Nombre | Sub-cuentas frecuentes |
|---|---|---|
| **60** | Compras | 601 Mercaderías, 603 Materiales auxiliares, 604 Envases |
| **61** | Variación de existencias | 611 Mercaderías (contrapartida de compras) |
| **62** | Gastos de personal | 621 Remuneraciones, 627 Seguridad y previsión social |
| **63** | Servicios prestados por terceros | 631 Transporte, 632 Asesoría, 636 Servicios básicos, 637 Publicidad |
| **64** | Gastos por tributos | 641 Gobierno central, 642 Gobierno local |
| **65** | Otros gastos de gestión | 651 Seguros, 655 Suscripciones |
| **67** | Gastos financieros | 671 Intereses bancarios, 677 Diferencia de cambio |
| **68** | Valuación y deterioro | 681 Depreciación acumulada |

#### Elemento 7: Ingresos

| Cuenta | Nombre | Sub-cuentas frecuentes |
|---|---|---|
| **70** | Ventas | 701 Mercaderías, 704 Prestación de servicios, 706 Otros |
| **75** | Otros ingresos de gestión | 751 Alquileres, 759 Otros |
| **77** | Ingresos financieros | 771 Intereses, 776 Diferencia de cambio |
| **709** | Devoluciones sobre ventas | Contra-cuenta para NC por devolución |
| **741** | Descuentos concedidos | Contra-cuenta para NC por descuentos |

### Cuenta 16/167 — IGV por Acreditar

| Sub-cuenta | Uso |
|---|---|
| **1673** | IGV de compras pendiente de aplicar como crédito fiscal |
| Traslado a 4012 | Al momento del devengo/uso |

---

## MÓDULO 9 — Calendario de Obligaciones y Señales de Alerta

### 9.1 Obligaciones Tributarias 2026

| Obligación | Periodicidad | Formulario | Observación |
|---|---|---|---|
| IGV + pagos a cuenta IR | Mensual | PDT 621 | Según cronograma SUNAT por último dígito RUC |
| Declaración Anual IR | Anual | PDT 710 | Marzo–abril del año siguiente |
| PLAME (planilla electrónica) | Mensual | PDT 601 | Solo si tiene empleados |
| Libros electrónicos (PLE/SIRE) | Mensual | PLE SUNAT | Obligatorio si ingresos > 75 UIT (S/ 397,500) |
| ITAN | Anual | PDT 648 | Solo Régimen General, activos netos > S/ 1M |

**Cronograma de vencimientos 2026 — ejemplo RUC terminado en 4:**

| Mes declarado | Fecha de vencimiento |
|---|---|
| Enero | 18 de febrero |
| Febrero | 18 de marzo |
| Marzo | 17 de abril |

> Ver cronograma completo vigente en: `https://www.sunat.gob.pe/orientacion/mipet/cronograma.html`

### 9.2 Libros Contables Obligatorios por Nivel de Ingresos (RMT)

| Ingresos brutos anuales | Libros obligatorios |
|---|---|
| Hasta 300 UIT (S/ 1,590,000) | Registro de Ventas, Registro de Compras, Libro Diario Simplificado |
| 300 UIT a 500 UIT | + Libro Diario y Libro Mayor |
| Más de 500 UIT (S/ 2,650,000) | Contabilidad completa + Libro de Inventarios y Balances, Caja y Bancos |

### 9.3 Señales de Alerta para PYMEs

| Alerta | Umbral | Acción recomendada |
|---|---|---|
| IGV a pagar supera 10% de ventas brutas | > 10% ventas | Revisar crédito fiscal no utilizado o aplicado incorrectamente |
| Saldo de detracciones > 2 meses de tributos | Más de 60 días acumulado | Solicitar liberación de fondos a SUNAT |
| Pago a proveedor sin bancarización ≥ S/ 2,000 | Cualquier caso | Riesgo de perder crédito fiscal y deducción del gasto |
| Más de 15 UIT de utilidad gravable en RMT | > S/ 79,500 utilidad neta | Exceso paga 29.5%; evaluar planificación tributaria |
| Comprobante de proveedor con RUC no habido | Cualquier caso | No usar como crédito fiscal — riesgo de fiscalización |
| Facturas sin anotar en SIRE antes de requerimiento SUNAT | Cualquier caso | Pérdida del crédito fiscal aunque el documento sea válido |

---

## REFERENCIAS NORMATIVAS

| Norma | Contenido |
|---|---|
| TUO D.S. 055-99-EF | Ley del IGV (Arts. 1, 2, 5, 18, 19) |
| D. Leg. 1269 + Ley 32353 | Régimen MYPE Tributario (RMT) |
| Ley 28194 + D. Leg. 1529 | Bancarización — umbral S/ 2,000 / $500 |
| R.S. 007-99/SUNAT | Reglamento de Comprobantes de Pago |
| R.S. 183-2004/SUNAT | Reglamento del SPOT (Detracciones) |
| PCGE 2019 (CNC, vigente desde enero 2020) | Plan Contable General Empresarial |
| TUO del Código Tributario | Sanciones, infracciones, prescripción (4 años) |
| D. Leg. 1499 | Bancarización de remuneraciones (sin umbral mínimo) |

---

*Documento de uso interno — Agente Contable / Consultoría Untiveros*  
*Actualizar cuando SUNAT modifique tasas, plazos o reglamentos.*  
*UIT 2026 = S/ 5,300 | Última verificación normativa: Mayo 2026*
