# Piloto Tucano — Datos operativos extraídos

Copia de trabajo (extraída el 2026-09-06 desde `github.com/Gabriel-unti/Tucano`, commit vigente a esa fecha) de las 4 areas necesarias para continuar el piloto del SaaS sobre datos reales de Braidy Wonders SAC / Tucano Peru.

**Fuente maestra:** `github.com/Gabriel-unti/Tucano` (repo privado, produccion). Esta carpeta es una copia de trabajo, no la fuente de verdad — los archivos vivos siguen editandose en Tucano. Antes de asumir que algo aqui sigue vigente, releer `Tucano/CLAUDE.md` (clonado localmente como repo hermano en `../Tucano/`, gitignored en este repo).

## Contenido

- `BANCOS/` — Flujo de caja bancario (BBVA). Reporte final: `Flujo_Caja_Detalle.xlsx`. Ver `Tucano/DOCUMENTACION TECNICA/Flujo_Caja_Bancario.md` para arquitectura completa.
- `CONTABILIDAD/` — Libro diario y detracciones: `Libro_Diario_Braidy_Wonders.xlsx` (hojas `Registro_Compras`, `Libro_Diario`, `TC_Diario`, `Detracciones_Control`). Ver `Tucano/DOCUMENTACION TECNICA/Guia_Detracciones_SUNAT_Braidy_Wonders.md`.
- `FACTURAS_PROVEEDORES/` — Registro de facturas (`Facturas_Proveedores.xlsx`, 217 filas al 19 ago 2026) + PDFs fuente (169 archivos). Ver `Tucano/DOCUMENTACION TECNICA/Facturas_Proveedores.md`.
- `CUENTAS_POR_PAGAR/` — Deuda a proveedores: `Reporte_Pendientes.xlsx`, `reporte_proveedor.xlsx`, PDFs de solicitudes de pago (`SOL_DE_PAGO/`). Ver `Tucano/DOCUMENTACION TECNICA/Reporte_Pendientes_Documentacion_Tecnica.md`.

## Confidencialidad

Contiene datos financieros reales de Braidy Wonders SAC (montos, RUC de proveedores, cuentas bancarias). No compartir fuera de este entorno ni anonimizar sin criterio — a diferencia de `02_Piloto_P5/Cliente_CarlosTorres/`, aqui Gabriel es tesorero de la propia empresa, no un tercero, pero el repo debe seguir siendo privado.

## Uso previsto

Base de datos reales para separar, en `01_Agente_IA/` y `02_Piloto_P5/`, el motor generalizable (clasificacion, deteccion de duplicados, deteccion de detracciones SUNAT, generacion de EEFF) de lo especifico de Braidy Wonders (plan de cuentas, nombres de proveedores) — ver CLAUDE.md seccion "Generalizacion producto".
