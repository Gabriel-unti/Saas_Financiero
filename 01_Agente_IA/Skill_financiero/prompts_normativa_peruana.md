# Prompts — Notebook: Normativa Peruana Tributaria y Contable

**Notebook ID:** `c2cc7763-294c-4b9e-869c-4d5d66caa6ca`  
**Fecha creación:** 2026-05-29  
**Fuentes:** ~50 fuentes (SUNAT, MEF, orientacion.sunat, CPE, regulación MYPE)

---

## BLOQUE 1 — Clasificación Contable (PCGE)

### Prompt 1.1 — Clasificar un asiento por descripción
```
Dada esta descripción de transacción: "[DESCRIPCIÓN]"
¿Qué cuenta PCGE corresponde al débito y cuál al crédito?
Indica el código de cuenta (4 dígitos mínimo), el nombre de la cuenta, y si corresponde a activo, pasivo, patrimonio, ingreso o gasto.
Responde en formato: DEBE: [código] [nombre] / HABER: [código] [nombre]
```

### Prompt 1.2 — Validar un asiento contable
```
Tengo el siguiente asiento contable:
DEBE: [código] [monto]
HABER: [código] [monto]
Concepto: [descripción]

¿Es correcto según el PCGE 2019? Si hay error, indica qué cuenta debería usarse y por qué.
```

### Prompt 1.3 — Listar sub-cuentas de una cuenta madre
```
¿Cuáles son las sub-cuentas del PCGE 2019 que pertenecen a la cuenta [número]?
Lista código, nombre y descripción breve de cada sub-cuenta.
```

### Prompt 1.4 — Clasificar múltiples facturas
```
Tengo las siguientes facturas de proveedores:
[lista de facturas con proveedor, monto, concepto]

Para cada una, indica:
1. Cuenta PCGE de gasto o activo (débito)
2. Cuenta PCGE de IGV por pagar o crédito fiscal (si aplica)
3. Cuenta PCGE del proveedor (haber)
```

---

## BLOQUE 2 — IGV y Crédito Fiscal

### Prompt 2.1 — Verificar si procede crédito fiscal
```
Una empresa en Régimen MYPE Tributario recibió la siguiente factura:
Proveedor: [nombre]
RUC: [número]
Concepto: [descripción]
Monto: S/ [X] + IGV S/ [Y]

¿Puede usar el IGV de esta factura como crédito fiscal? ¿Qué condiciones debe cumplir?
```

### Prompt 2.2 — Calcular IGV a pagar en el período
```
En el mes de [mes/año] tengo:
- Ventas gravadas con IGV: S/ [X]
- Compras con derecho a crédito fiscal: S/ [Y]
- Saldo a favor del mes anterior: S/ [Z]

¿Cuánto IGV debo pagar a SUNAT? Muestra el cálculo paso a paso.
```

### Prompt 2.3 — Operaciones no gravadas con IGV
```
¿Las siguientes operaciones están gravadas con IGV en Perú?
1. [operación 1]
2. [operación 2]
3. [operación 3]

Para cada una indica: gravada / no gravada / exonerada / inafecta, con la base legal.
```

---

## BLOQUE 3 — Régimen MYPE Tributario

### Prompt 3.1 — Calcular pago a cuenta mensual
```
Una empresa en RMT tuvo los siguientes ingresos netos en [mes]:
Ingresos: S/ [X]
Utilidad acumulada al mes anterior: S/ [Y]
¿Cuánto debe pagar a cuenta del Impuesto a la Renta este mes?
¿Aplica el coeficiente o el 1%? Explica la regla.
```

### Prompt 3.2 — Obligaciones contables según el RMT
```
Una empresa en Régimen MYPE Tributario con ingresos de S/ [X] anuales:
¿Qué libros contables está obligada a llevar?
¿Cuáles son electrónicos (PLE)?
¿Cuál es el plazo máximo de atraso permitido para cada libro?
```

### Prompt 3.3 — Comparar RMT vs Régimen General
```
Una empresa con ingresos proyectados de S/ [X] anuales:
¿Le conviene más el RMT o el Régimen General?
Considera: tasa efectiva del IR, obligaciones formales, acceso a beneficios, y restricciones de cada régimen.
```

---

## BLOQUE 4 — Comprobantes Electrónicos

### Prompt 4.1 — Cuándo emitir cada tipo de comprobante
```
¿Qué tipo de comprobante electrónico corresponde en cada caso?
1. Venta a empresa con RUC por S/ 5,000
2. Venta a persona natural sin RUC por S/ 800
3. Anulación parcial de una factura ya emitida
4. Devolución de mercadería de un cliente corporativo
5. Cobro de anticipo/adelanto a un cliente
```

### Prompt 4.2 — Plazos de envío de comprobantes
```
¿Cuáles son los plazos máximos para enviar a SUNAT los siguientes comprobantes electrónicos?
- Factura electrónica
- Boleta de venta electrónica
- Nota de crédito electrónica
- Guía de remisión electrónica
¿Qué sanción aplica si se envía fuera de plazo?
```

### Prompt 4.3 — Códigos de error al validar un XML
```
Al intentar validar un comprobante electrónico en SUNAT, recibo el siguiente código de error: [código]
¿Qué significa este error? ¿Cómo se corrige? ¿Es un error que invalida el comprobante o solo una observación?
```

---

## BLOQUE 5 — Detracciones y Retenciones

### Prompt 5.1 — Verificar si aplica detracción
```
Una empresa va a cobrar por los siguientes servicios/bienes:
1. [servicio/bien 1] por S/ [X]
2. [servicio/bien 2] por S/ [Y]

¿Alguno de estos está sujeto al Sistema de Detracciones (SPOT)?
Si sí: ¿cuál es el porcentaje de detracción? ¿Quién la deposita? ¿En qué plazo?
```

### Prompt 5.2 — Impacto de detracciones en flujo de caja
```
Una MYPE de construcción tiene proyectadas las siguientes cobranzas para el trimestre:
[lista de facturas con montos y conceptos]

Calcula:
1. Monto total de detracciones que los clientes retendrán
2. Monto neto disponible en cuenta corriente
3. Monto disponible en cuenta de detracciones (para qué puede usarse)
4. Impacto en días de cobertura de caja
```

### Prompt 5.3 — Liberar fondos de cuenta de detracciones
```
Una empresa tiene S/ [X] acumulados en su cuenta de detracciones del Banco de la Nación.
¿Bajo qué condiciones puede solicitar la liberación de estos fondos?
¿Cuál es el procedimiento? ¿Cuánto tiempo toma?
```

---

## BLOQUE 6 — Consultas de Agente (Uso Programático)

### Prompt 6.1 — Análisis de comprobante completo
```
Analiza el siguiente comprobante:
Tipo: [factura/boleta/nota crédito]
Emisor RUC: [número]
Receptor RUC: [número]
Fecha emisión: [fecha]
Concepto: [descripción]
Base imponible: S/ [X]
IGV: S/ [Y]
Total: S/ [Z]

Indica:
1. ¿Es válido según la normativa SUNAT vigente?
2. ¿El receptor puede usar el IGV como crédito fiscal?
3. ¿Aplica detracción? ¿Cuánto?
4. ¿Qué asiento contable PCGE corresponde para el receptor?
```

### Prompt 6.2 — Alerta de obligaciones del mes
```
Hoy es [fecha]. La empresa [nombre] tiene RUC terminado en [último dígito].
¿Cuáles son las declaraciones y pagos que vencen este mes?
Lista: obligación, fecha de vencimiento, formulario SUNAT.
```

### Prompt 6.3 — Diagnóstico tributario rápido
```
Una empresa presenta este perfil:
- Régimen: [RMT/General/RER/NRUS]
- Sector: [construcción/retail/servicios]
- Ingresos anuales: S/ [X]
- Empleados: [N]
- Opera con: [clientes con RUC / consumidores finales / ambos]

¿Cuáles son los 3 principales riesgos tributarios que debería revisar?
¿Qué oportunidades de optimización fiscal tiene disponibles?
```
