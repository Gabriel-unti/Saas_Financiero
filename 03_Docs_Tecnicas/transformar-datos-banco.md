# Transformar Datos Bancarios Reales
**Cómo convertir el extracto de tu banco al formato del agente**

---

## Formato objetivo

El agente necesita este CSV exacto en `Skill_financiero/data/movimientos_diarios.csv`:

```
cuenta_id,fecha,saldo_cierre,ingresos_dia,egresos_dia,moneda
CUENTA-001,2026-02-24,254544.34,19738.50,15194.16,PEN
```

| Columna | Descripción |
|---|---|
| `cuenta_id` | Tu código interno (ej: `BCP-OP-01`) |
| `fecha` | YYYY-MM-DD |
| `saldo_cierre` | Saldo al cierre del día |
| `ingresos_dia` | Suma de abonos del día |
| `egresos_dia` | Suma de cargos del día (valor positivo) |
| `moneda` | `PEN` o `USD` |

---

## Paso 1 — Exportar desde el banco

### BCP (Banco de Crédito del Perú)

1. Ingresa a **viabcp.com** → Banca por Internet
2. Menú: **Cuentas** → selecciona la cuenta
3. Pestaña **Movimientos**
4. Selecciona rango de fechas: **últimos 90 días**
5. Clic en **Exportar** → formato **Excel (.xlsx)**
6. El archivo tendrá columnas: `Fecha`, `Descripción`, `Cargo`, `Abono`, `Saldo`

### BBVA Perú

1. Ingresa a **bbva.pe** → Banca Online
2. Menú: **Mis Cuentas** → selecciona la cuenta
3. Clic en **Movimientos**
4. Selecciona rango: **últimos 90 días**
5. Clic en **Descargar** → **CSV**
6. El archivo tendrá columnas: `Fecha operación`, `Concepto`, `Importe`, `Saldo`

### Interbank

1. Ingresa a **interbank.pe**
2. Menú: **Cuentas** → **Historial de movimientos**
3. Selecciona la cuenta y rango de fechas
4. Clic en **Exportar a Excel**
5. El archivo tendrá columnas: `Fecha`, `Descripción`, `Débito`, `Crédito`, `Saldo`

### Scotiabank

1. Ingresa a **scotiabank.com.pe**
2. Menú: **Cuentas** → **Estado de cuenta**
3. Selecciona período
4. Clic en **Descargar** → **CSV**

---

## Paso 2 — Transformar con Python

Guarda el archivo del banco en `Skill_financiero/data/raw/` y ejecuta el script correspondiente.

### Script universal (`transformar_banco.py`)

```python
"""
transformar_banco.py — Convierte extracto bancario al formato del agente

Uso:
    python transformar_banco.py --banco bcp --archivo extracto_bcp.xlsx --cuenta BCP-OP-01 --moneda PEN
    python transformar_banco.py --banco bbva --archivo extracto_bbva.csv --cuenta BBVA-OP-01 --moneda PEN
    python transformar_banco.py --banco interbank --archivo extracto_ibank.xlsx --cuenta IBK-USD-01 --moneda USD
"""

import argparse
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / 'Skill_financiero' / 'data'


def transformar_bcp(archivo: str, cuenta_id: str, moneda: str) -> pd.DataFrame:
    """
    Formato BCP Excel:
    Columnas: Fecha | Descripción | N° Operación | Cargo | Abono | Saldo
    """
    df = pd.read_excel(archivo, skiprows=4)   # BCP tiene encabezados en las primeras filas
    df.columns = df.columns.str.strip()

    # Normalizar nombres de columna (pueden variar ligeramente según el tipo de cuenta)
    col_map = {
        'Fecha'   : 'fecha',
        'Cargo'   : 'cargo',
        'Abono'   : 'abono',
        'Saldo'   : 'saldo_cierre',
    }
    df = df.rename(columns=col_map)

    # Limpiar y convertir
    df['fecha']        = pd.to_datetime(df['fecha'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['cargo']        = pd.to_numeric(df['cargo'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['abono']        = pd.to_numeric(df['abono'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['saldo_cierre'] = pd.to_numeric(df['saldo_cierre'].astype(str).str.replace(',', ''), errors='coerce')

    # Agregar por día (puede haber múltiples movimientos por día)
    df_dia = df.groupby('fecha').agg(
        saldo_cierre = ('saldo_cierre', 'last'),   # saldo al cierre del día
        ingresos_dia = ('abono', 'sum'),
        egresos_dia  = ('cargo', 'sum'),
    ).reset_index()

    df_dia['cuenta_id'] = cuenta_id
    df_dia['moneda']    = moneda

    return df_dia[['cuenta_id', 'fecha', 'saldo_cierre', 'ingresos_dia', 'egresos_dia', 'moneda']]


def transformar_bbva(archivo: str, cuenta_id: str, moneda: str) -> pd.DataFrame:
    """
    Formato BBVA CSV:
    Columnas: Fecha operación | Fecha valor | Concepto | Importe | Saldo
    El importe es positivo para abonos, negativo para cargos.
    """
    df = pd.read_csv(archivo, sep=';', encoding='latin-1')
    df.columns = df.columns.str.strip()

    df['fecha']   = pd.to_datetime(df['Fecha operación'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['importe'] = pd.to_numeric(
        df['Importe'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce'
    ).fillna(0)
    df['saldo'] = pd.to_numeric(
        df['Saldo'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce'
    )

    df['abono'] = df['importe'].clip(lower=0)
    df['cargo'] = (-df['importe']).clip(lower=0)

    df_dia = df.groupby('fecha').agg(
        saldo_cierre = ('saldo',  'last'),
        ingresos_dia = ('abono',  'sum'),
        egresos_dia  = ('cargo',  'sum'),
    ).reset_index()

    df_dia['cuenta_id'] = cuenta_id
    df_dia['moneda']    = moneda

    return df_dia[['cuenta_id', 'fecha', 'saldo_cierre', 'ingresos_dia', 'egresos_dia', 'moneda']]


def transformar_interbank(archivo: str, cuenta_id: str, moneda: str) -> pd.DataFrame:
    """
    Formato Interbank Excel:
    Columnas: Fecha | Descripción | Débito | Crédito | Saldo
    """
    df = pd.read_excel(archivo, skiprows=2)
    df.columns = df.columns.str.strip()

    df['fecha']  = pd.to_datetime(df['Fecha'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['debito'] = pd.to_numeric(df['Débito'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['credito']= pd.to_numeric(df['Crédito'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['saldo']  = pd.to_numeric(df['Saldo'].astype(str).str.replace(',', ''), errors='coerce')

    df_dia = df.groupby('fecha').agg(
        saldo_cierre = ('saldo',   'last'),
        ingresos_dia = ('credito', 'sum'),
        egresos_dia  = ('debito',  'sum'),
    ).reset_index()

    df_dia['cuenta_id'] = cuenta_id
    df_dia['moneda']    = moneda

    return df_dia[['cuenta_id', 'fecha', 'saldo_cierre', 'ingresos_dia', 'egresos_dia', 'moneda']]


TRANSFORMADORES = {
    'bcp'      : transformar_bcp,
    'bbva'     : transformar_bbva,
    'interbank': transformar_interbank,
}


def main():
    parser = argparse.ArgumentParser(description='Transforma extracto bancario al formato del agente')
    parser.add_argument('--banco',   required=True, choices=TRANSFORMADORES.keys(),
                        help='Banco: bcp, bbva, interbank')
    parser.add_argument('--archivo', required=True, help='Ruta al extracto exportado del banco')
    parser.add_argument('--cuenta',  required=True,
                        help='Identificador de la cuenta (ej: BCP-OP-01)')
    parser.add_argument('--moneda',  default='PEN', choices=['PEN', 'USD'],
                        help='Moneda: PEN o USD')
    parser.add_argument('--output',  default=None,
                        help='Ruta de salida (por defecto: agrega/reemplaza en movimientos_diarios.csv)')
    parser.add_argument('--modo',    default='agregar', choices=['agregar', 'reemplazar'],
                        help='agregar: añade esta cuenta al CSV existente | reemplazar: crea nuevo CSV')
    args = parser.parse_args()

    print(f'Banco: {args.banco} | Cuenta: {args.cuenta} | Moneda: {args.moneda}')
    print(f'Archivo fuente: {args.archivo}')

    # Transformar
    fn = TRANSFORMADORES[args.banco]
    df_nuevo = fn(args.archivo, args.cuenta, args.moneda)
    df_nuevo = df_nuevo.sort_values('fecha').reset_index(drop=True)

    print(f'Filas transformadas: {len(df_nuevo)}')
    print(f'Rango de fechas: {df_nuevo["fecha"].min()} → {df_nuevo["fecha"].max()}')
    print(f'Saldo inicial: {df_nuevo["saldo_cierre"].iloc[0]:,.2f}')
    print(f'Saldo final:   {df_nuevo["saldo_cierre"].iloc[-1]:,.2f}')

    # Guardar
    output_path = Path(args.output) if args.output else (BASE_DIR / 'movimientos_diarios.csv')

    if args.modo == 'agregar' and output_path.exists():
        df_existente = pd.read_csv(output_path)
        # Eliminar registros anteriores de esta cuenta (para no duplicar)
        df_existente = df_existente[df_existente['cuenta_id'] != args.cuenta]
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_final = df_final.sort_values(['cuenta_id', 'fecha'])
        print(f'Modo: agregar | Total cuentas en el CSV: {df_final["cuenta_id"].nunique()}')
    else:
        df_final = df_nuevo
        print(f'Modo: reemplazar | CSV nuevo con 1 cuenta')

    df_final.to_csv(output_path, index=False)
    print(f'\nGuardado en: {output_path}')
    print('Listo. Puedes ejecutar tesorero.py con los datos reales.')


if __name__ == '__main__':
    main()
```

---

## Paso 3 — Ejecutar la transformación

```bash
# Activar entorno
D:\Proyecto_Gabriel\.venv\Scripts\activate
cd D:\Proyecto_Gabriel\docs

# BCP — primera cuenta
python transformar_banco.py --banco bcp --archivo extracto_bcp_90dias.xlsx --cuenta BCP-OP-01 --moneda PEN

# BBVA — segunda cuenta (agregar al mismo CSV)
python transformar_banco.py --banco bbva --archivo extracto_bbva.csv --cuenta BBVA-OP-01 --moneda PEN --modo agregar

# Interbank USD — tercera cuenta
python transformar_banco.py --banco interbank --archivo extracto_ibank.xlsx --cuenta IBK-USD-01 --moneda USD --modo agregar
```

---

## Paso 4 — Verificar antes de ejecutar el agente

```bash
# Verificar el CSV resultante
python -c "
import pandas as pd
df = pd.read_csv('D:/Proyecto_Gabriel/Skill_financiero/data/movimientos_diarios.csv')
print('Cuentas:', df['cuenta_id'].unique().tolist())
print('Filas:', len(df))
print('Rango:', df['fecha'].min(), '->', df['fecha'].max())
print('Nulos:', df.isnull().sum().to_dict())
"
```

El CSV está listo cuando:
- Al menos 60 días por cuenta
- Sin valores nulos en `saldo_cierre`
- `ingresos_dia` y `egresos_dia` son positivos

---

## Posibles ajustes al script

Los extractos bancarios cambian de formato con las actualizaciones del banco. Si el script falla:

1. Abre el Excel/CSV del banco manualmente
2. Identifica las columnas reales (pueden tener nombres ligeramente distintos)
3. Ajusta el diccionario `col_map` en la función correspondiente
4. El objetivo es siempre llegar a: `fecha`, `saldo_cierre`, `ingresos_dia`, `egresos_dia`

---

*Ver también: `docs/agente-tesoreria.md` — documentación técnica completa del agente*
