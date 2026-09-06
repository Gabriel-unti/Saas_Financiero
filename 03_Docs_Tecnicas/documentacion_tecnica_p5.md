# Proyecto 5 — Automatización Contable · Documentación Técnica

**Fecha:** 28 mayo 2026  
**Autor:** Gabriel Untiveros  
**Cliente:** CT PRIME CONSULTING SAC · RUC 20563642930 · Carlos Torres  
**Estado:** Pipeline en producción (NB01 → NB03 → NB04). Iteraciones 2–5 implementadas. NC/ND, normalización IGV, enriquecimiento cruzado y fórmulas TOTALES dinámicas resueltos.  
**Versión:** v5 (28 mayo 2026)

---

## 1. Problema de negocio

Carlos Torres (director contable) procesa facturas de forma completamente manual:

1. Recibe PDFs, JPEGs y escaneos de facturas de compra y venta
2. Transcribe manualmente los datos a Excel
3. Asigna cuentas contables según el PCGE (Plan Contable General Empresarial)
4. Genera los asientos en el Libro Diario con formato propio

El pipeline automatiza los cuatro pasos. La clasificación contable aprende con cada lote procesado, reduciendo la intervención humana en pasadas sucesivas.

---

## 2. Arquitectura general

```
facturas PDF/JPEG
       ↓
[NB01] Extracción (Claude Haiku vision)
       ↓ facturas_extraidas.json
[NB03] Clasificación contable (SQLite memory + Claude Haiku)
       ↓ facturas_clasificadas.json
[NB04] Generación asientos (openpyxl → plantilla Excel)
       ↓
Diario_{periodo}.xlsx  +  reporte_revision_{fecha}.xlsx
```

> **NB02 eliminado permanentemente del pipeline.** La API pública `api.apis.net.pe` devuelve HTTP 401 sin token de pago. NB03 lee directamente `facturas_extraidas.json`; NB04 lee `facturas_clasificadas.json`. NB02 existe en carpeta como referencia pero no se ejecuta.

**Modelos utilizados:** `claude-haiku-4-5-20251001` (extracción y clasificación)  
**Credenciales:** `ANTHROPIC_API_KEY` en `D:/Proyecto_Gabriel/Skill_financiero/.env`

---

## 3. Estructura de carpetas

```
D:\Proyecto_Gabriel\Proyecto_5\
├── Python\
│   ├── 01_extraccion_facturas.ipynb
│   ├── 02_validacion_sunat.ipynb     (no ejecutar — ver nota en sección 5)
│   ├── 03_clasificacion_contable.ipynb
│   └── 04_generacion_asientos.ipynb
├── config\
│   └── plan_contable.json             (44 cuentas PCGE de CT PRIME)
└── data\
    ├── input\compras\                 (PDFs/JPEGs proveedores)
    ├── input\ventas\                  (PDFs/JPEGs clientes)
    ├── processed\                     (JSONs intermedios)
    ├── memoria\clasificaciones.db     (SQLite — se crea en NB03)
    └── output\                        (Excel final + reporte)
```

**Template Excel:** `D:\Proyecto_Gabriel\Proyecto_contable\Data\libro_diario_piloto.xlsx`  
Sheet: `Libro_diario` · Tabla estructurada `tdiario` · Headers en fila 5 · Datos desde fila 6

**Facturas de referencia** copiadas desde:
- `D:\Proyecto_Gabriel\Proyecto_contable\facturas_proveedores\` → `data\input\compras\`
- `D:\Proyecto_Gabriel\Proyecto_contable\factuas_clientes\` → `data\input\ventas\`

---

## 4. NB01 — Extracción de facturas

**Input:** PDFs y JPEGs en `data/input/compras/` y `data/input/ventas/`  
**Output:** `data/processed/facturas_extraidas.json` + JSON individual por archivo

### Deduplicación dentro del lote

Después de consolidar `facturas_compras + facturas_ventas` y antes de escribir `facturas_extraidas.json`, se elimina cualquier duplicado por `(ruc_emisor, serie, numero)`.

> **Nota de diseño:** NB01 es completamente stateless. La deduplicación es solo dentro del batch actual. La protección contra re-procesamiento de lotes anteriores la provee NB04.

### Función clave: `archivo_a_base64(ruta)`

```python
import fitz  # PyMuPDF — sin dependencias externas

def archivo_a_base64(ruta: Path) -> tuple[str, str]:
    ext = ruta.suffix.lower()
    if ext == '.pdf':
        doc = fitz.open(str(ruta))
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72), alpha=False)
        img_bytes = pix.tobytes('jpeg')
        doc.close()
        return base64.b64encode(img_bytes).decode('utf-8'), 'image/jpeg'
    else:
        with open(ruta, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8'), 'image/jpeg'
```

> Se usa PyMuPDF (`fitz`) en lugar de `pdf2image`. Poppler no instalable en Windows — `pdftoppm.exe` no encontrado en PATH. PyMuPDF no requiere dependencias externas y produce JPEGs de 200 DPI directamente.

### Campos extraídos por Claude (JSON por factura)

```json
{
  "tipo_doc": "FACTURA | BOLETA | NOTA_CREDITO | NOTA_DEBITO | RECIBO",
  "codigo_tipo_doc": "01 | 03 | 07 | 08 | R1 | 04",
  "serie": "E001",
  "numero": "00000030",
  "fecha_emision": "2025-02-20",
  "ruc_emisor": "20563642930",
  "razon_social_emisor": "CONTACTO CREATIVO TI S.A.C.",
  "ruc_receptor": "20613742825",
  "razon_social_receptor": "MEDIA SOLUTION E.I.R.L.",
  "descripcion_servicio": "Servicio de consultoría tecnológica",
  "base_imponible": 7500.00,
  "igv": 1350.00,
  "total": 8850.00,
  "moneda": "PEN",
  "tiene_detraccion": false,
  "monto_detraccion": 0.00,
  "doc_referencia": null,
  "otorga_credito_igv": true,
  "deducible_renta": true,
  "confianza_extraccion": 0.95,
  "tipo_operacion": "VENTA",
  "archivo_origen": "ventas/FACT E001-30 MEDIA SOLUTION.pdf",
  "procesado_en": "2026-05-28T14:32:11"
}
```

### Reglas críticas del prompt (Iteración 2 en adelante)

- **`razon_social_emisor` / `razon_social_receptor`:** debe ser la denominación o razón social LEGAL de la empresa (ej: `"MEDIA SOLUTION E.I.R.L."`, `"SODIMAC PERU S.A."`). NUNCA una dirección, domicilio fiscal, ciudad o referencia geográfica. Si el documento muestra el domicilio debajo del nombre, extraer SOLO el nombre legal.
- **NC/ND — campo `numero`:** debe ser el número PROPIO de la NC/ND (ej: para `"NC E001-03"`, `numero="00000003"`), NO el número del comprobante que modifica. El comprobante modificado va únicamente en `doc_referencia`.
- **`doc_referencia`:** para tipo 07 (NC) y 08 (ND), extraer la serie-número del comprobante que modifica (ej: `"E001-00000030"`). Para otros tipos, `null`.
- **`otorga_credito_igv`:** `true` si `codigo_tipo_doc` es 01 o 04 y el IGV está discriminado. `false` para 03 (Boleta) y R1 (Honorarios). NC/ND heredan del comprobante que modifican — dejar `true` por defecto.
- **`deducible_renta`:** `true` para 01 (Factura), R1 (Honorarios) y 04 (Liquidación Compra). `false` para 03 (Boleta). NC/ND: `true` por defecto.

---

## 5. NB02 — Validación SUNAT

> **ELIMINADO DEL PIPELINE.** La API pública `api.apis.net.pe` devuelve HTTP 401 sin token de pago. En la ejecución de prueba, los 13 RUCs únicos devolvieron 401. El pipeline salta directamente de NB01 a NB03. Para producción futura, adquirir plan básico (~S/ 30–50/mes).

El archivo `02_validacion_sunat.ipynb` se conserva en la carpeta como referencia de implementación.

---

## 6. NB03 — Clasificación Contable con Memoria

**Input:** `data/processed/facturas_extraidas.json`  
**Output:** `data/processed/facturas_clasificadas.json`  
**Memoria:** `data/memoria/clasificaciones.db` (SQLite)

### Restricción de diseño crítica — regla 90/10

> El 90% de casos: mismo RUC → misma cuenta siempre.
> El 10% restante: mismo RUC → cuentas distintas según el servicio.
> Ejemplo: Sodimac puede ser `6399094` (papelería) o `33611` (equipo de cómputo).

La clave de memoria es `(ruc_proveedor, patron_descripcion)` y no solo `ruc_proveedor`.

### Schema SQLite

```sql
CREATE TABLE clasificaciones (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    ruc_proveedor         TEXT NOT NULL,
    patron_descripcion    TEXT DEFAULT '',
    cuenta_debe           TEXT NOT NULL,
    detalle_cuenta        TEXT,
    veces_usada           INTEGER DEFAULT 1,
    ultima_fecha          TEXT,
    confirmada_por_humano INTEGER DEFAULT 0
);

CREATE TABLE historial (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo_origen    TEXT,
    ruc_proveedor     TEXT,
    descripcion       TEXT,
    cuenta_sugerida   TEXT,
    cuenta_final      TEXT,
    fue_corregida     INTEGER DEFAULT 0,
    confianza_sistema REAL,
    fecha             TEXT
);
```

### Bypass NC/ND (Iteración 2)

Las Notas de Crédito y Notas de Débito no pasan por el clasificador. Se marca directamente `requiere_revision: True` y `origen_clasificacion: 'ajuste_documental'`. La generación del asiento inverso la maneja NB04.

```python
TIPOS_AJUSTE = {'NOTA_CREDITO', 'NOTA_DEBITO'}

# En el loop de compras y ventas:
if tipo_doc in TIPOS_AJUSTE:
    factura['cuenta_debe'] = None
    factura['requiere_revision'] = True
    factura['origen_clasificacion'] = 'ajuste_documental'
    facturas_clasificadas.append(factura)
    continue
```

### Flags tributarios (Iteración 2)

`agregar_flags_tributarios()` se aplica a todas las facturas antes de escribir el JSON de salida:

```python
UMBRAL_BANCARIZACION_SOLES = 2000.0
UMBRAL_BANCARIZACION_USD   = 500.0

def agregar_flags_tributarios(factura: dict) -> None:
    total   = float(factura.get('total') or 0)
    moneda  = str(factura.get('moneda', 'PEN')).upper()
    umbral  = UMBRAL_BANCARIZACION_USD if moneda == 'USD' else UMBRAL_BANCARIZACION_SOLES
    factura['requiere_bancarizacion'] = total >= umbral
    # otorga_credito_igv y deducible_renta vienen ya del JSON de NB01
```

### Lógica de clasificación — 3 niveles

```python
def clasificar(ruc, descripcion, memoria, plan_contable, claude_client):
    registros = memoria.buscar_por_ruc(ruc)

    # Nivel 1: RUC nunca visto → Claude desde cero
    if not registros:
        return clasificar_con_claude(..., confianza_base=0.65)

    # Nivel 2: RUC con una sola cuenta conocida → usar directamente
    cuentas_unicas = set(r['cuenta_debe'] for r in registros)
    if len(cuentas_unicas) == 1:
        return {"cuenta_debe": registros[0]['cuenta_debe'], "confianza": 0.97, "origen": "memoria_exacta"}

    # Nivel 3: RUC con múltiples cuentas → match por palabras clave (Jaccard)
    mejor = max(registros, key=lambda r: score_patron(r['patron_descripcion'], descripcion))
    if score_patron(mejor['patron_descripcion'], descripcion) >= 0.60:
        return {"cuenta_debe": mejor['cuenta_debe'], "confianza": 0.85, "origen": "memoria_patron"}

    # Score bajo incluso con patrones → Claude con contexto de ambigüedad
    return clasificar_con_claude(..., contexto_ambiguo=registros, confianza_base=0.70)
```

### Clasificación de ventas

Las ventas usan siempre el mismo asiento (Carlos no varía):
- Cuenta: `12121` (FACTURAS POR COBRAR) · Confianza: 1.0 · Origen: `regla_ventas`

### Flujo de aprendizaje post-corrección

Al inicio de cada nueva ejecución de NB03, se lee `reporte_revision_anterior.xlsx`. Las correcciones de Carlos (columna `CUENTA_FINAL`) se aplican a la memoria con `confirmada_por_humano = 1`. Los índices correctos de columna en `cargar_correcciones()` son: `ruc=row[0]`, `descripcion=row[2]`, `cuenta_sugerida=row[4]`, `cuenta_final=row[9]`.

---

## 7. NB04 — Generación de Asientos y Salida Excel

**Input:** `data/processed/facturas_clasificadas.json`  
**Template:** `D:\Proyecto_Gabriel\Proyecto_contable\Data\libro_diario_piloto.xlsx`  
**Output:** `data/output/Diario_{periodo}.xlsx` + `data/output/reporte_revision_{fecha}.xlsx`

### Normalización de base/IGV (Iteración 3)

Claude Haiku puede extraer valores inconsistentes (base + igv ≠ total). Todas las funciones generadoras de asiento aplican normalización antes de calcular:

```python
if abs(base + igv - total) > 0.02:
    base = round2(total / 1.18)
    igv  = round2(total - base)
```

Esta normalización se aplica en: `asiento_compra`, `asiento_venta`, `asiento_nc_venta`, `asiento_nc_compra`.

### Estructura del asiento COMPRA (5 filas)

| CUENTA  | DEBE           | HABER |
|---------|----------------|-------|
| 6XXXXXX | base_imponible | —    |
| 40111   | igv            | —    |
| 42121   | —             | total |
| 9411    | base_imponible | —    |
| 79      | —             | base_imponible |

Glosa: `"Reg. Compras {serie}-{numero}"`  
Col I (CLIENTE/PROVEEDOR): `razon_social_emisor`  
Col J (NRO. DOCUMENTO): `{serie}-{numero}`

### Estructura del asiento VENTA (3 filas)

| CUENTA | DEBE  | HABER          |
|--------|-------|----------------|
| 12121  | total | —             |
| 40111  | —    | igv            |
| 7041   | —    | base_imponible |

Glosa: `"Reg. Ventas {serie}-{numero}"`  
Col I (CLIENTE/PROVEEDOR): `razon_social_receptor`

### Estructura NC/ND — asiento inverso (Iteración 2)

**NC de venta (asiento_nc_venta — 3 filas):**

| CUENTA | DEBE           | HABER |
|--------|----------------|-------|
| 40111  | igv            | —    |
| 7041   | base_imponible | —    |
| 12121  | —             | total |

Glosa: `"NC {serie}-{numero} ref: {doc_referencia}"`

**NC de compra (asiento_nc_compra — 5 filas):**

| CUENTA  | DEBE           | HABER          |
|---------|----------------|----------------|
| 42121   | total          | —             |
| 40111   | —             | igv            |
| 6XXXXXX | —             | base_imponible |
| 79      | base_imponible | —             |
| 9411    | —             | base_imponible |

Glosa: `"NC recibida {serie}-{numero} ref: {doc_referencia}"`

### Carga del template y eliminación de hojas extra (Iteración 3)

```python
wb = openpyxl.load_workbook(str(TEMPLATE_PATH))
for hoja_extra in ['Hoja1', 'Sheet1', 'Sheet']:
    if hoja_extra in wb.sheetnames:
        del wb[hoja_extra]
ws = wb['Libro_diario']
```

El template `libro_diario_piloto.xlsx` contiene una `Hoja1` vacía heredada de Excel. Se elimina en cada ejecución.

### Pre-enriquecimiento de razon_social (Iteración 5)

Antes de generar cualquier asiento, se construye un diccionario `RUC → razon_social` usando todas las facturas del lote. Si una factura tiene `razon_social` vacío pero otra factura del mismo lote tiene el mismo RUC con nombre válido, se rellena automáticamente.

```python
ruc_to_razon = {}
for f in facturas:
    for ruc_f, nombre_f in [('ruc_receptor', 'razon_social_receptor'),
                              ('ruc_emisor',   'razon_social_emisor')]:
        ruc_val    = str(f.get(ruc_f,    '') or '').strip()
        nombre_val = str(f.get(nombre_f, '') or '').strip()
        if ruc_val and nombre_val and nombre_val.lower() not in ('null', 'none'):
            ruc_to_razon[ruc_val] = nombre_val

for f in facturas:
    for ruc_f, nombre_f in [('ruc_receptor', 'razon_social_receptor'),
                              ('ruc_emisor',   'razon_social_emisor')]:
        if not str(f.get(nombre_f, '') or '').strip():
            ruc_val = str(f.get(ruc_f, '') or '').strip()
            if ruc_val in ruc_to_razon:
                f[nombre_f] = ruc_to_razon[ruc_val]
```

Caso típico: E001-30 tenía `razon_social_receptor` vacío (Claude evitó la dirección fiscal pero no encontró el nombre). E001-31, misma factura al mismo cliente, tenía `"MEDIA SOLUTION E.I.R.L."`. El lookup rellena E001-30 sin re-ejecutar NB01.

### Deduplicación contra el Diario existente

Al cargar el template, NB04 lee todos los `nro_doc` (columna J) ya registrados. Para NC/ND se usa una clave compuesta para evitar colisión con la factura original:

```python
if tipo_doc in TIPOS_AJUSTE:
    dedup_key = f'NC_{nro_doc}_{factura.get("doc_referencia", "")}'
else:
    dedup_key = nro_doc

if dedup_key in DOCS_EXISTENTES:
    continue  # ignorar duplicado
```

> **Advertencia de diseño previa:** Si NC se extraía con `numero='00000030'` (número del comprobante referenciado en vez del propio), `nro_doc = 'E001-00000030'` colisionaba con la factura original y la NC quedaba descartada antes de llegar al routing de tipo_doc. Esto se resolvió en el prompt de NB01 (la NC ahora extrae su propio número) y con la clave compuesta de deduplicación.

El check de `tipo_doc` se realiza **antes** del check de deduplicación para garantizar el routing correcto.

### Fórmulas TOTALES dinámicas (Iteración 4)

El template usa una tabla estructurada `tdiario` con fórmulas `=SUM(tdiario[DEBE])`. Openpyxl escribe celdas fuera del rango definido de la tabla, haciendo que las fórmulas no sumen los nuevos asientos.

Solución: segunda pasada sobre el archivo ya guardado que sobreescribe G3, H3 y H2 con rangos explícitos:

```python
wb.save(str(output_path))

wb2 = openpyxl.load_workbook(str(output_path))
ws2 = wb2['Libro_diario']
ws2['G3'] = f'=SUM(G6:G{fila_actual})'
ws2['H3'] = f'=SUM(H6:H{fila_actual})'
ws2['H2'] = '=G3-H3'
wb2.save(str(output_path))
```

`fila_actual` apunta a la siguiente fila vacía después del último asiento (incluyendo separadores en blanco, que valen 0 en la suma).

### Herencia de estilos desde el template

NB04 no hardcodea fuente, bordes ni alineación. Lee los estilos de la primera fila con datos del template y los hereda en cada celda nueva:

```python
def leer_estilos_referencia(ws) -> dict:
    for row in ws.iter_rows(min_row=6):
        if any(c.value is not None for c in row):
            return {cell.column: {'font': copy(cell.font), 'border': copy(cell.border),
                                   'alignment': copy(cell.alignment),
                                   'number_format': cell.number_format}
                    for cell in row}
    header_row = list(ws.iter_rows(min_row=5, max_row=5))[0]
    return {cell.column: {'font': copy(cell.font), 'border': copy(cell.border),
                           'alignment': copy(cell.alignment),
                           'number_format': cell.number_format}
            for cell in header_row}
```

Fallback a fila de headers (fila 5) si el template está vacío — primer lote del piloto.

### Flujo de confianza y color en Excel

| Confianza       | Color celda  | Acción                              |
|-----------------|--------------|-------------------------------------|
| ≥ 0.90          | Sin color    | Auto al Excel sin cola              |
| 0.70 – 0.89     | Naranja FFD580 | Excel + reporte de revisión       |
| < 0.70          | Amarillo FFFF00 | Cola obligatoria + reporte        |
| NC/ND (cualquiera) | Naranja  | Siempre en reporte, revisión obligatoria |

### Reporte de revisión (14 columnas)

`data/output/reporte_revision_{fecha}.xlsx` incluye:
`RUC_PROVEEDOR`, `RAZON_SOCIAL`, `DESCRIPCION_SERVICIO`, `BASE_IMPONIBLE`, `CUENTA_SUGERIDA`, `DETALLE_CUENTA_SUGERIDA`, `CONFIANZA`, `ORIGEN`, `RAZON_SISTEMA`, `CUENTA_FINAL` (verde — Carlos llena), `ARCHIVO_ORIGEN`, `REQUIERE_BANCARIZACION`, `OTORGA_CREDITO_IGV`, `DOC_REFERENCIA`.

Col `OBSERVACIONES` en `Control_Facturas`: para NC/ND se pre-popula con `"Ref: {doc_referencia}"`.

---

## 8. Verificación end-to-end

Celda de verificación en NB04 comprueba Debe = Haber por cada asiento. Aplica la misma normalización que los generadores antes de comparar:

```python
for factura in compras + ventas:
    base  = round2(factura.get('base_imponible'))
    igv   = round2(factura.get('igv'))
    total = round2(factura.get('total'))

    # Misma normalización que los generadores de asiento
    if abs(base + igv - total) > 0.02:
        base = round2(total / 1.18)
        igv  = round2(total - base)

    if tipo_doc in TIPOS_AJUSTE:
        if tipo_op == 'VENTA':
            debe, haber = round2(igv + base), round2(total)
        else:
            debe, haber = round2(total + base), round2(igv + base + base)
    elif tipo_op == 'COMPRA':
        debe, haber = round2(base + igv + base), round2(total + base)
    else:
        debe, haber = round2(total), round2(igv + base)
```

> Versiones anteriores de esta celda omitían la normalización, lo que causaba falsos ❌ para facturas con base+igv≠total extraídas por Haiku. El asiento real sí cuadraba porque los generadores normalizan, pero la verificación no lo detectaba.

---

## 9. Errores encontrados y soluciones

### Error 1 — Poppler no en PATH

**Causa:** `pdf2image` requiere `pdftoppm.exe`. `winget install oschwartz10612.Poppler` no agregó el binario al PATH.  
**Solución:** Reemplazar por `PyMuPDF (fitz)`. Sin dependencias externas, produce JPEG de alta calidad directamente.

### Error 2 — API key no encontrada

**Causa:** `ANTHROPIC_API_KEY` no estaba en el entorno del kernel de Jupyter.  
**Solución:** En la celda de setup de cada NB:
```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path('D:/Proyecto_Gabriel/Skill_financiero/.env'))
```

### Error 3 — FileNotFoundError en plan_contable.json

**Causa:** `BASE_DIR = Path('../')` desde `Python/` resuelve a `Proyecto_5/`. Concatenar `'../config'` subía un nivel adicional.  
**Solución:** `BASE_DIR / 'config/plan_contable.json'` en NB03 y NB04. Mismo fix para `TEMPLATE_PATH`.

### Error 4 — SUNAT API HTTP 401

**Causa:** `api.apis.net.pe` requiere token de pago. Sin token devuelve 401.  
**Solución de diseño:** NB02 eliminado del pipeline. NB03 lee directamente el output de NB01.

### Error 5 — Formato visual roto en Diario generado

**Síntoma:** Datos correctos pero Calibri 10, sin bordes, fecha en formato incorrecto — visualmente inconsistente con el template de Carlos.  
**Solución:** Eliminar constantes hardcodeadas. `leer_estilos_referencia()` hereda estilos de la primera fila de datos del template por columna.

### Error 6 — Duplicados al correr el pipeline dos veces

**Síntoma:** Correr NB04 dos veces duplicaba todos los asientos.  
**Solución:** Deduplicación en dos niveles — NB01 (batch) por `(ruc_emisor, serie, numero)` y NB04 (Diario) por `nro_doc` en columna J.

### Error 7 — Debe ≠ Haber en asientos (Iteración 3)

**Síntoma:** Diferencias en el Diario (ej: Debe=8850, Haber=7370.93) por inconsistencia entre base+igv y total en el JSON de extracción.  
**Causa:** Claude Haiku extrajo valores que no sumaban al total (ej: base=6355.93 + igv=1350 ≠ total=8850).  
**Solución:** Bloque de normalización en todas las funciones generadoras: `if abs(base+igv-total)>0.02: base=round2(total/1.18); igv=round2(total-base)`.

### Error 8 — Hoja1 en blanco en el Excel generado (Iteración 3)

**Causa:** El template `libro_diario_piloto.xlsx` contiene una `Hoja1` vacía heredada de Excel al crear el archivo.  
**Solución:** Loop de eliminación al cargar el workbook: `for hoja_extra in ['Hoja1','Sheet1','Sheet']: del wb[hoja_extra]`.

### Error 9 — NC no aparecía en el Libro Diario (Iteración 3)

**Causa:** NB01 extraía la NC con `numero='00000030'` (número del comprobante referenciado, no el de la NC). Esto hacía que `nro_doc='E001-00000030'` colisionara con la factura original en `DOCS_EXISTENTES`, descartando la NC antes del routing de tipo_doc.  
**Solución:** Tres cambios simultáneos:
1. Prompt NB01: regla explícita — `numero` de NC = número propio de la NC, no del comprobante que modifica
2. Check de `tipo_doc` movido ANTES del check de deduplicación
3. Clave compuesta para NC/ND: `f'NC_{nro_doc}_{doc_referencia}'`

### Error 10 — razon_social muestra dirección en vez del nombre legal (Iteración 4)

**Síntoma:** Col I del Libro Diario mostraba `"120 RES. CALLE JORGE"` en vez de `"MEDIA SOLUTION E.I.R.L."`.  
**Causa:** Claude confundió el domicilio fiscal impreso debajo del nombre con la razón social del receptor.  
**Solución:** Regla explícita en el prompt de NB01: razon_social debe ser la denominación legal NUNCA una dirección o referencia geográfica.

### Error 11 — TOTALES no sumaba los nuevos asientos (Iteración 4)

**Causa:** Las celdas G3/H3 usan `=SUM(tdiario[DEBE])` que referencia la tabla estructurada `tdiario` con rango fijo. Openpyxl escribe fuera del rango definido de la tabla.  
**Solución:** Segunda pasada post-save que sobreescribe G3/H3/H2 con `=SUM(G6:G{fila_actual})`, usando el rango dinámico real de los datos escritos.

### Error 12 — CLIENTE/PROVEEDOR vacío tras re-extracción con prompt corregido (Iteración 5)

**Causa:** Al corregir el prompt (Error 10), Claude dejó `razon_social_receptor=null` para E001-30 porque el documento solo mostraba la dirección, no el nombre legal explícito. Resultado: columna I vacía en el Diario.  
**Solución:** Pre-enriquecimiento cruzado en NB04: si una factura tiene `razon_social` vacío pero otra factura del mismo lote tiene el mismo RUC con nombre válido (E001-31 tenía `"MEDIA SOLUTION E.I.R.L."`), el nombre se propaga sin re-ejecutar NB01.

---

## 10. Verificación por iteración

### Verificar formato visual (Iteración 2 → 5)

1. Correr NB04 → abrir `Diario_{periodo}.xlsx`
2. Comparar visualmente asientos existentes vs. generados: misma fuente, bordes, formato fecha `DD/MM/YYYY`, montos `#,##0.00`
3. Confirmar overlay naranja en facturas con confianza < 0.90 y en NC/ND
4. Confirmar columna TOTALES (G3/H3) suma todos los asientos. H2 debe mostrar 0.00 si cuadran

### Verificar NC/ND (Iteración 3)

5. Asiento NC debe aparecer en Libro_diario con glosa `"NC E001-X ref: E001-30"`
6. NC en ventas: 40111+7041 DEBE, 12121 HABER. Total debe = Total haber
7. NC debe aparecer en naranja en el reporte de revisión con `doc_referencia` en col N

### Verificar nombre de cliente (Iteración 4–5)

8. Col I de todos los asientos debe mostrar nombre legal (no dirección, no vacío)
9. Log del pipeline debe imprimir `"Enriquecido: FACT E001-30 ... → MEDIA SOLUTION E.I.R.L."` si el caso aplica

### Verificar deduplicación (doble ejecución)

10. Correr NB04 una segunda vez con los mismos datos → `Asientos escritos: 0`, el Excel no crece
11. Log debe mostrar `⚠️ Duplicado ignorado` para cada factura del lote anterior

### Primer lote del piloto — verificado (28 mayo 2026)

Primer output confirmado visualmente contra el Excel generado. 3 facturas de venta (CT PRIME → MEDIA SOLUTION E.I.R.L.):

| NRO | FECHA      | DOC            | TIPO    | DEBE     | HABER    |
|-----|------------|----------------|---------|----------|----------|
| 1   | 20/02/2025 | E001-00000030  | FACTURA | 8,850.00 | 8,850.00 |
| 2   | 25/02/2025 | E001-00000031  | FACTURA | 1,500.00 | 1,500.00 |
| 3   | 25/02/2025 | E001-00000003  | NC      | 7,500.00 | 7,500.00 |
| **TOTALES** | | | | **17,850.00** | **17,850.00** |

**DIFERENCIAS: 0.00** ✅

Observaciones confirmadas:
- Asiento 1: `"MEDIA SOLUTION E.I.R.L."` en col CLIENTE/PROVEEDOR (enriquecimiento cruzado funcionando)
- Asiento 2: normalización activa — Claude extrajo base=1,272.88 + igv=229.12 ≠ total=1,770 → pipeline recalculó a base=1,271.19 + igv=228.81 = 1,500.00 (factura original era de S/ 1,500 sin IGV, el total de S/ 1,770 incluía IGV)
- Asiento 3: NC genera asiento inverso correcto — 40111+7041 en DEBE, 12121 en HABER con glosa `"NC E001-00000003 ref: E001-00000030"`
- TOTALES (G3/H3): fórmulas dinámicas sumando correctamente los 3 asientos
- Hoja1 eliminada — solo aparecen `Libro_diario` y `Control_Facturas`

### Ciclo de corrección humana (pendiente con Carlos)

12. Carlos llena columna `CUENTA_FINAL` en `reporte_revision_{fecha}.xlsx`
13. Renombrar a `reporte_revision_anterior.xlsx` en `data/output/`
14. Correr NB03 → `cargar_correcciones()` actualiza SQLite con `confirmada_por_humano = 1`
15. Correr NB04 → esas facturas ya no aparecen en naranja (confianza sube a 0.97 vía `memoria_exacta`)

---

## 11. Dependencias del entorno

```
pymupdf          (PyMuPDF / fitz)
anthropic
python-dotenv
requests
pandas
openpyxl
```

**Python:** ejecutar con `python` (no `python3`) en PowerShell de Windows.  
**Instalación:** `python -m pip install <paquete>`

---

*Documento técnico interno — Proyecto Gabriel · Mayo 2026 · v5 (28 mayo 2026)*

---

# Resumen — Piloto Agente Contable
**Fecha:** Mayo 2026  
**Contexto:** Cierre de primer piloto comercial con ex jefe de Gabriel.

---

## 1. Punto de partida

Gabriel cerró reunión con su ex jefe. Resultado: piloto del agente contable a cambio de **caso de estudio + precio referencial**. Volumen del piloto: 1 mes de facturas (revisado luego a 3 meses).

> Nota de carácter: cerrar la reunión fue exactamente el tipo de exposición que el perfil identifica como su batalla más difícil. Registrado.

---

## 2. La bifurcación inicial

La pregunta "¿cómo conecto a mis clientes con el agente?" escondía dos negocios distintos:

| Opción | Qué es | Cuándo aplica |
|---|---|---|
| **Operador en la sombra** | Gabriel ejecuta el agente en su máquina; el cliente solo recibe el resultado | **Ahora — piloto y primeros 2–3 clientes** |
| **SaaS autónomo** | El cliente interactúa directo con el agente sin intermediario | Después, con datos de errores reales del piloto |

**Decisión:** Operador en la sombra. Construir SaaS antes del piloto sería el patrón del constructor que pule el escudo para una batalla que no empieza.

---

## 3. Lectura honesta del volumen

**Dato duro:** El cliente maneja menos de 50 facturas/mes. El ahorro real para él en horas-hombre es de S/ 50–150 mensuales. Eso obliga a redefinir qué se está vendiendo.

**Tres lecturas posibles del piloto:**

1. **Laboratorio barato** — el cliente real está en empresas con 200–500+ facturas/mes. El piloto sirve para aprender, no para que el ex jefe ahorre.
2. **Puerta de entrada** — el agente es el caballo de Troya para vender después dashboard de CxP, conciliación bancaria, alertas. El piloto compra acceso.
3. **Valor en precisión, no en ahorro** — vender tasa de acierto, log auditable, menos errores SUNAT. Requiere demostrarlo con números.

**Posición recomendada:** Lectura 2 + algo de Lectura 3. Encaja con la trayectoria estratégica (consultoría → retainer → producto) y con el posicionamiento triádico (tesorería + Python + BI).

---

## 4. Precio del piloto

- **Tarifa de lanzamiento:** S/ 300/mes durante 3 meses
- **Tarifa regular declarada:** S/ 600/mes (aplicable mes 4+ o nuevos clientes)
- **Duración:** 3 meses, no 1

**Cláusula sugerida por escrito:**

> *"Tarifa de lanzamiento: S/ 300 mensuales durante los 3 meses del piloto. Tarifa regular del servicio: S/ 600 mensuales, aplicable a partir del mes 4 o para nuevos clientes. Este precio incluye acceso a caso de estudio documentado al cierre del piloto."*

---

## 5. Métricas del caso de estudio (definir ANTES de empezar)

| Métrica | Cómo se mide | Lo que vende |
|---|---|---|
| Tiempo manual antes | Cronómetro sobre muestra real del asistente | Línea base creíble |
| Tiempo con el agente | Desde llegada de facturas hasta entregable | El número grande del caso |
| Tasa de acierto del agente | Facturas correctamente clasificadas sin intervención | Credibilidad técnica |
| Errores encontrados (log) | Tipo de error + frecuencia | Hoja de ruta de mejora del producto |
| Horas-hombre liberadas/mes | Tiempo antes − tiempo de revisión = ahorro real | ROI duro para el siguiente cliente |

**Métrica que más escala a clientes grandes:** Tasa de acierto + % de tiempo ahorrado. "94% acierto, 78% menos tiempo" se escala a cualquier volumen. "4 horas menos al mes" no.

---

## 6. Flujo de trabajo del piloto

- **Canal único de entrada:** correo dedicado o carpeta compartida. **No WhatsApp.**
- **Ejecución:** Gabriel pasa las facturas por el agente en su máquina.
- **Revisión humana:** Gabriel revisa cada salida. En el piloto, el valor es la garantía, no la automatización.
- **Entregable:** en el formato que el cliente ya usa.
- **Log de errores:** dos columnas mínimas — factura / qué falló. **Activo más valioso del piloto.**

---

## 7. Decisiones pendientes de Gabriel

- [ ] Redactar y enviar documento "Términos del Piloto — Agente Contable" (1 página): alcance, precio, duración, métricas, permisos caso de estudio
- [ ] Confirmar canal único de entrada (correo dedicado vs. carpeta compartida)
- [ ] Cronometrar tiempo manual real del asistente del cliente (línea base)
- [ ] Crear archivo de log de errores antes de procesar la primera factura real
- [ ] Definir qué del caso de estudio será público y qué bajo NDA
- [ ] Re-ejecutar pipeline completo NB01 → NB03 → NB04 con las 24 facturas del piloto

---

🎯 **OBJETIVO CONCRETO:** Cerrar el piloto con condiciones escritas que protejan el precio futuro, garanticen el caso de estudio y entreguen 3 meses de aprendizaje real del producto.  
⚡ **SIGUIENTE ACCIÓN:** Redactar el documento "Términos del Piloto — Agente Contable" (1 página).  
⏱️ **TIEMPO ESTIMADO:** 45 minutos.  
📈 **RESULTADO ESPERADO:** Documento firmado/aprobado por escrito que sirve como plantilla para los próximos 3–5 pilotos.
