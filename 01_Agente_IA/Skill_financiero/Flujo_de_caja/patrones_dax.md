# Patrones DAX de Tesorería — Referencia completa

Cada patrón aparece con: (a) la medida lista, (b) qué hace, (c) los **puntos de
adaptación** que debes reemplazar con los nombres reales del proyecto.

Convención de placeholders en esta referencia:
- `T_REAL` = tabla de flujo real (ej. `FLUJO_REAL1`)
- `T_PROY` = tabla de flujo proyectado (ej. `FLUJO_PROYECTADO2`)
- `T_SALDOS` = tabla de saldos por banco (ej. `Saldos3`)
- `T_FECHA` = tabla calendario (ej. `Fecha`, columna `Date`)
- `T_TC` = tabla tipo de cambio (ej. `Tipo_Cambio`)
- `T_SELECTOR` = tabla selector de moneda (ej. `'Selector Moneda'`)
- `[Importe]`, `[Tipo_Movimiento]`, `[Moneda]`, `[Saldo]`, `[Fecha]` = columnas

Al generar el entregable, reemplaza TODOS los placeholders por los nombres reales.

---

## Tabla de contenidos
1. Medidas base (flujo real)
2. Medidas proyectadas
3. Multi-moneda PEN/USD
4. Vencimientos (alertas de pago)
5. Agregaciones por dimensión
6. Saldos
7. Notas de implementación + orden de creación

---

## 1. Medidas base (flujo real)

**Total Ingresos / Total Egresos** — suman movimientos por tipo. Adaptación:
`T_REAL`, `[Importe]`, `[Tipo_Movimiento]` y los valores `"INGRESO"`/`"EGRESO"`.
```dax
Total Ingresos = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "INGRESO" )
Total Egresos  = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "EGRESO" )
```

**Flujo Neto** — suma (no resta) porque los egresos van negativos. Si en el
proyecto nuevo los egresos vienen positivos, cambia a resta y avisa.
```dax
Flujo Neto = [Total Ingresos] + [Total Egresos]
```

**Saldo Final** — último saldo registrado vía `LASTNONBLANK`. Adaptación: `[Saldo]`, `[Fecha]`.
```dax
Saldo Final = CALCULATE ( SUM ( T_REAL[Saldo] ), LASTNONBLANK ( T_REAL[Fecha], CALCULATE ( SUM ( T_REAL[Saldo] ) ) ) )
```

**Flujo Acumulado** — suma acumulativa hasta la fecha del eje. Adaptación: `T_FECHA[Date]`.
```dax
Flujo Acumulado = CALCULATE ( [Flujo Neto], FILTER ( ALL ( T_FECHA[Date] ), T_FECHA[Date] <= MAX ( T_FECHA[Date] ) ) )
```

---

## 2. Medidas proyectadas

Mismo patrón que las base pero sobre `T_PROY`.
```dax
Ingresos Proyectados   = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "INGRESO" )
Egresos Proyectados    = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "EGRESO" )
Flujo Neto Proyectado  = [Ingresos Proyectados] + [Egresos Proyectados]
```

**Flujo Proyectado Acumulado** — acumula desde HOY hasta la fecha del eje, ya
convertido a la moneda seleccionada. Usa el patrón multi-moneda (sección 3).
```dax
Flujo Proyectado Acumulado =
VAR _m = [Moneda Seleccionada]
VAR _tc = [TC Aplicado]
VAR _hoy = TODAY ()
VAR _hastaFecha = MAX ( T_FECHA[Date] )
VAR _pen = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Moneda] = "PEN", FILTER ( ALL ( T_FECHA[Date] ), T_FECHA[Date] >= _hoy && T_FECHA[Date] <= _hastaFecha ) )
VAR _usd = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Moneda] = "USD", FILTER ( ALL ( T_FECHA[Date] ), T_FECHA[Date] >= _hoy && T_FECHA[Date] <= _hastaFecha ) )
RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )
```

---

## 3. Multi-moneda PEN/USD

> Si el proyecto es de UNA sola moneda, omite todo este bloque y usa las medidas
> base directamente. Este bloque solo aplica cuando hay PEN y USD mezclados.

**Moneda Seleccionada** — lee el slicer; default PEN. Adaptación: `T_SELECTOR`.
```dax
Moneda Seleccionada = SELECTEDVALUE ( T_SELECTOR[Moneda], "PEN" )
```

**TC Aplicado** — promedio compra/venta del TC más reciente. Adaptación: `T_TC` y
sus columnas de fecha, compra y venta.
```dax
TC Aplicado =
VAR _ult = CALCULATE ( MAX ( T_TC[Fecha] ), ALL ( T_TC ) )
VAR _compra = CALCULATE ( MAX ( T_TC[TC - COMPRA] ), ALL ( T_TC ), T_TC[Fecha] = _ult )
VAR _venta  = CALCULATE ( MAX ( T_TC[TC - VENTA] ),  ALL ( T_TC ), T_TC[Fecha] = _ult )
RETURN DIVIDE ( _compra + _venta, 2 )
```

**Patrón de conversión (memorízalo, se repite en todas las "x Moneda"):**
1. `VAR _m = [Moneda Seleccionada]` · `VAR _tc = [TC Aplicado]`
2. Calcula `_pen` y `_usd` por separado, cada uno con su filtro `[Moneda] = "..."`
3. `RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )`

```dax
Ingresos x Moneda =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _pen = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "INGRESO", T_REAL[Moneda] = "PEN" )
VAR _usd = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "INGRESO", T_REAL[Moneda] = "USD" )
RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )

Egresos x Moneda =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _pen = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "EGRESO", T_REAL[Moneda] = "PEN" )
VAR _usd = CALCULATE ( SUM ( T_REAL[Importe] ), T_REAL[Tipo_Movimiento] = "EGRESO", T_REAL[Moneda] = "USD" )
RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )

Flujo Neto x Moneda = [Ingresos x Moneda] + [Egresos x Moneda]

Saldo Final x Moneda =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _pen = CALCULATE ( SUM ( T_REAL[Saldo] ), T_REAL[Moneda] = "PEN", LASTNONBLANK ( T_REAL[Fecha], CALCULATE ( SUM ( T_REAL[Saldo] ) ) ) )
VAR _usd = CALCULATE ( SUM ( T_REAL[Saldo] ), T_REAL[Moneda] = "USD", LASTNONBLANK ( T_REAL[Fecha], CALCULATE ( SUM ( T_REAL[Saldo] ) ) ) )
RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )
```

---

## 4. Vencimientos (alertas de pago)

Patrón único parametrizado por N días. Egresos proyectados entre hoy y hoy+N,
en valor absoluto. Para generar 7/15/30, solo cambia `_hasta = _hoy + N` y el
nombre. Adaptación: `T_PROY`, `[Importe]`, `[Tipo_Movimiento]`, `[Moneda]`, `[Fecha]`.

```dax
Pagos N dias =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _hoy = TODAY () VAR _hasta = _hoy + N
VAR _pen = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "EGRESO", T_PROY[Moneda] = "PEN", T_PROY[Fecha] >= _hoy, T_PROY[Fecha] <= _hasta )
VAR _usd = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "EGRESO", T_PROY[Moneda] = "USD", T_PROY[Fecha] >= _hoy, T_PROY[Fecha] <= _hasta )
RETURN ABS ( IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc ) )
```
Genera `Pagos 7 dias`, `Pagos 15 dias`, `Pagos 30 dias` con N = 7, 15, 30. Si el
usuario quiere otros horizontes (ej. 60/90), úsalos en su lugar.

---

## 5. Agregaciones por dimensión

`Pagos por Categoria`, `Pagos por Mes` y `Detalle Pagos Comprometidos` comparten
exactamente la misma fórmula: total de egresos proyectados convertidos a moneda y
en valor absoluto. La diferencia es solo en qué campo las pones (categoría, mes,
etc.) en el visual — el contexto del visual hace el resto. Por eso las tres miden
lo mismo:

```dax
Pagos por Categoria =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _pen = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "EGRESO", T_PROY[Moneda] = "PEN" )
VAR _usd = CALCULATE ( SUM ( T_PROY[Importe] ), T_PROY[Tipo_Movimiento] = "EGRESO", T_PROY[Moneda] = "USD" )
RETURN ABS ( IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc ) )
```
`Pagos por Mes` y `Detalle Pagos Comprometidos` = misma fórmula, distinto nombre.
(Podrías usar una sola medida y reutilizarla; se dejan tres por claridad en el
panel de campos, que es como el usuario ya las tiene.)

---

## 6. Saldos

**Saldo Base Actual** — último saldo de bancos, ignorando filtros de fecha/mes con
`REMOVEFILTERS`. Adaptación: `T_SALDOS` y sus columnas de fecha, saldo soles, saldo
dólares y mes de reporte.
```dax
Saldo Base Actual =
VAR _m = [Moneda Seleccionada] VAR _tc = [TC Aplicado]
VAR _ultFecha = CALCULATE ( MAX ( T_SALDOS[Fecha] ), ALL ( T_SALDOS ) )
VAR _pen = CALCULATE ( SUM ( T_SALDOS[Saldo Soles] ),   T_SALDOS[Fecha] = _ultFecha, REMOVEFILTERS ( T_SALDOS[Mes_Reporte] ), REMOVEFILTERS ( T_FECHA ) )
VAR _usd = CALCULATE ( SUM ( T_SALDOS[Saldo Dólares] ), T_SALDOS[Fecha] = _ultFecha, REMOVEFILTERS ( T_SALDOS[Mes_Reporte] ), REMOVEFILTERS ( T_FECHA ) )
RETURN IF ( _m = "USD", DIVIDE ( _pen, _tc ) + _usd, _pen + _usd * _tc )
```

**Saldo Caja Proyectado** — saldo base + flujo proyectado acumulado, solo a futuro.
```dax
Saldo Caja Proyectado =
VAR _hoy = TODAY () VAR _fechaEje = MAX ( T_FECHA[Date] )
RETURN IF ( _fechaEje >= _hoy, [Saldo Base Actual] + [Flujo Proyectado Acumulado] )
```

---

## 7. Notas de implementación + orden de creación

**Formato recomendado por medida:**
- Moneda: `"S/ "#,##0` o `"$ "#,##0` según selector (o `#,##0` y deja el símbolo al visual).
- Saldos / pagos: `#,##0` sin decimales para KPI cards grandes.
- Acumulados y flujos: `#,##0`.

**Orden de creación sugerido (replica este checklist en el entregable):**
1. Conectar el Excel (todas las hojas) y verificar tipos en Power Query.
2. Crear tabla `_Medidas` vacía (`Inicio → Especificar datos`).
3. Crear `Moneda Seleccionada` y `TC Aplicado` (todo lo multi-moneda depende de ellas).
4. Crear medidas base (Total Ingresos/Egresos, Flujo Neto, Saldo Final, Flujo Acumulado).
5. Crear medidas proyectadas.
6. Crear medidas "x Moneda".
7. Crear vencimientos (Pagos 7/15/30).
8. Crear agregaciones y saldos.
9. Construir visuales: KPI cards → flujo de caja → donut categorías → barras por mes → tabla detalle.
10. Slicers: Banco, Categoría, Centro de Costo, Moneda.

**Recordatorio de invariantes** (ver "Reglas de oro" en SKILL.md): egresos
negativos → suma + ABS; conversión por separado antes de sumar; vencimientos con
`TODAY()`; saldo proyectado solo a futuro; `REMOVEFILTERS` en saldos.
