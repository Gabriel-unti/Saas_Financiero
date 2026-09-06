---
name: dax-tesoreria
description: "Genera medidas DAX para dashboards de tesorería y flujo de caja en Power BI, adaptadas a las tablas reales del usuario. Contiene patrones reutilizables probados: multi-moneda PEN/USD con tipo de cambio, alertas de vencimiento (pagos a 7/15/30 días), flujo neto real vs. proyectado, flujo acumulado, saldo base y saldo de caja proyectado, y agregaciones por categoría/mes/banco. Activa esta skill cuando el usuario pida medidas DAX para un dashboard de tesorería, cash flow, flujo de caja, control de pagos, vencimientos o liquidez; cuando mencione 'medidas DAX', 'dashboard de tesorería', 'flujo proyectado', 'pagos a X días', 'saldo de caja', 'multi-moneda en Power BI'; o cuando suba un Excel de movimientos bancarios / proyección financiera y quiera convertirlo en un modelo de Power BI. Úsala también cuando el usuario arme un dashboard financiero nuevo para otra empresa y quiera reaprovechar la lógica del dashboard de Constructora Andina."
---

# DAX Tesorería — Librería de patrones para dashboards de cash flow

Esta skill convierte la lógica DAX ya probada en el dashboard de tesorería de
Constructora Andina SAC en una librería reutilizable. El objetivo es que, ante un
dashboard de tesorería nuevo (otra empresa, otro periodo), puedas regenerar todas
las medidas adaptadas a las tablas y columnas reales de ese proyecto, sin
reescribir la lógica desde cero.

## Qué hace

Dado un modelo de Power BI de tesorería con (mínimamente) una tabla de movimientos
reales, una tabla de proyección, una tabla de saldos y una tabla calendario, esta
skill produce el set completo de medidas DAX:

- **Base (flujo real):** Total Ingresos, Total Egresos, Flujo Neto, Saldo Final, Flujo Acumulado.
- **Proyección:** Ingresos/Egresos Proyectados, Flujo Neto Proyectado, Flujo Proyectado Acumulado.
- **Multi-moneda PEN/USD:** selector de moneda, tipo de cambio aplicado, y todas las medidas convertidas a la moneda elegida.
- **Vencimientos:** Pagos a 7/15/30 días (dinámicos con `TODAY()`).
- **Agregaciones:** Pagos por Categoría, por Mes, detalle de comprometidos.
- **Saldos:** Saldo Base Actual, Saldo Caja Proyectado.

La entrega normal es un archivo `.md` con todas las medidas listas para copiar a
Power BI, agrupadas por sección y con notas de formato — el mismo formato que el
usuario ya conoce de `medidas_dax_constructora_andina.md`.

## Cuándo usar esta skill

Úsala cuando:

- El usuario pide medidas DAX para un dashboard de tesorería / cash flow / control
  de pagos / liquidez / vencimientos.
- El usuario sube un Excel de movimientos bancarios o proyección financiera y
  quiere armarlo como modelo de Power BI.
- El usuario está replicando el dashboard de Constructora Andina para otro cliente.
- El usuario menciona patrones específicos: "pagos a X días", "flujo proyectado",
  "multi-moneda PEN/USD", "saldo de caja proyectado".

**Cuándo NO usarla:** para medidas DAX que no son de tesorería (segmentación RFM,
ventas, inventarios). Esos casos tienen lógica distinta y merecen su propia skill.

## Cómo usar la skill — flujo de trabajo

El trabajo pesado lo hace `scripts/generar_dax.py`, que auto-detecta las columnas
del Excel y genera el `.md` de medidas ya con los nombres reales. Se usa en dos
fases para que confirmes el mapeo antes de generar (un nombre de columna mal
detectado produce DAX que falla en silencio en Power BI).

### Paso 1 — Inspeccionar el Excel y obtener el mapeo sugerido

```bash
python scripts/generar_dax.py inspeccionar /mnt/user-data/uploads/<archivo>.xlsx
```

Esto imprime las hojas, sus columnas, y un **mapeo auto-detectado** en JSON. El
detector usa sinónimos comunes (`Importe`/`Monto`/`Valor`, `Tipo_Movimiento`/
`Flujo`/`Tipo`, etc.), así que acierta con nombres variados — pero cualquier campo
que no pudo resolver queda como `"REVISAR"`.

### Paso 2 — Confirmar el mapeo con el usuario

Muéstrale el mapeo sugerido al usuario y confirma especialmente:
- Los campos marcados `REVISAR` (el detector no los encontró).
- `egresos_negativos`: ¿los egresos vienen negativos en el Excel? (afecta si Flujo
  Neto suma o resta, y si los pagos usan ABS).
- `tabla_fecha` / `col_fecha_calendario`: normalmente la tabla calendario se crea
  aparte en Power BI; el default `Fecha[Date]` suele estar bien.

Guarda el mapeo confirmado como un `.json`. **No asumas los nombres** — confírmalos
antes de generar.

### Paso 3 — Generar las medidas

```bash
python scripts/generar_dax.py generar \
    /mnt/user-data/uploads/<archivo>.xlsx \
    mapeo.json \
    /mnt/user-data/outputs/medidas_dax_<empresa>.md \
    [--una-moneda] [--dias 7 15 30]
```

Banderas:
- `--una-moneda`: el proyecto usa una sola moneda. Omite todo el bloque
  multi-moneda y genera medidas más simples (sin TC ni conversión).
- `--dias 15 30 60`: horizontes de vencimiento personalizados (default `7 15 30`).

Decide estas banderas a partir de lo que viste en el Excel y de lo que el usuario
necesita (ver más abajo "Decidir qué módulos incluir").

### Paso 4 — Entregar

Preséntale el `.md` con `present_files`. Reporta brevemente: qué módulos incluiste,
si fue multi-moneda o una sola, qué horizontes de vencimiento, y recuérdale que el
orden de creación sugerido está al final del archivo.

### Decidir qué módulos incluir

- **¿Multi-moneda o una sola?** Si en el Excel todos los movimientos son de una
  moneda, usa `--una-moneda`.
- **¿Tiene proyección a futuro?** Sin tabla de proyección, los vencimientos y el
  flujo proyectado no aplican; avísale al usuario.
- **¿Qué horizontes de vencimiento?** 7/15/30 es el default; ajústalo con `--dias`.

### Si necesitas generar a mano o explicar la lógica

`references/patrones_dax.md` tiene cada patrón con su lógica explicada y sus puntos
de adaptación. Úsalo cuando el usuario pida entender o ajustar una medida puntual,
o cuando el modelo tenga una estructura tan rara que el script no la cubra.

## Reglas de oro de los patrones (no romperlas al adaptar)

Estas son las invariantes que hacen que las medidas funcionen. Al adaptar nombres,
respétalas:

1. **Patrón multi-moneda.** Toda medida "x Moneda" sigue 4 pasos: capturar
   `[Moneda Seleccionada]`, obtener `[TC Aplicado]`, calcular PEN y USD por
   separado, y convertir: `IF USD → DIVIDE(PEN, TC) + USD, ELSE → PEN + USD*TC`.
   Nunca conviertas antes de sumar; suma cada moneda en su propia variable primero.

2. **Egresos negativos.** En el modelo, los egresos se guardan negativos, por eso
   `Flujo Neto = Ingresos + Egresos` (suma, no resta) y las medidas de pagos usan
   `ABS()` para mostrarlos positivos. Si en el proyecto nuevo los egresos vienen
   positivos, ajusta el signo y avisa al usuario.

3. **Vencimientos dinámicos.** Los `Pagos a N días` usan `TODAY()` para que se
   actualicen solos. Filtran `Fecha >= hoy AND Fecha <= hoy + N`. No los
   conviertas en fechas fijas.

4. **Saldo proyectado solo a futuro.** `Saldo Caja Proyectado` solo devuelve valor
   cuando la fecha del eje es `>= hoy` (para no pisar el histórico real con
   proyección).

5. **REMOVEFILTERS en saldos.** Las medidas de saldo base ignoran filtros cruzados
   de fecha/mes con `REMOVEFILTERS`, porque el saldo es un corte puntual, no una
   agregación del periodo filtrado.

Las explicaciones completas de cada patrón están en `references/patrones_dax.md`.

## Estructura de la skill

```
dax-tesoreria/
├── SKILL.md
├── scripts/
│   └── generar_dax.py    (inspecciona el Excel y genera el .md adaptado)
└── references/
    └── patrones_dax.md   (todos los patrones con lógica y puntos de adaptación)
```
