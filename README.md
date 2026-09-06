# SaaS Financiero para PYMEs — Contabilidad + Tesorería

SaaS financiero para PYMEs peruanas: planes de contabilidad, tesorería, flujo de caja y EEFF automatizados, con IA (Claude) como motor de clasificación y generación de asientos.

Nace de la fusión de dos líneas de trabajo:

- **P5 Automatización Contable** — piloto de extracción/clasificación de facturas y generación de libros contables (notebooks Python).
- **Financial Pulse** — agente de tesorería construido sobre patrones de Anthropic CWC (dataset, forecast, skills, loop agéntico, memory store).

**Piloto en curso:** Tucano Perú (razón social Braidy Wonders SAC, DMC turismo receptivo de lujo). Gabriel es el tesorero en planilla y usa esa posición como validación real del producto antes de venderlo a terceros.

## Estructura

```
00_Perfil_Personal/  CV, perfil, resumen de marca
01_Agente_IA/         Financial Pulse + workshops CWC + Skill_financiero (agente tesorería)
02_Piloto_P5/         Notebooks Python del piloto de automatización contable (demo + cliente real)
03_Docs_Tecnicas/     Normativa SUNAT/PCGE, documentación técnica, workflow GitHub
04_Comercial/         Modelo de negocio del SaaS
05_Piloto_Tucano/     Datos operativos reales extraídos de Tucano (flujo de caja, libro diario, facturas, cuentas por pagar)
Tucano/               Repo hermano clonado localmente (no versionado aquí) — código de producción del piloto
```

## Estado

| Componente | Estado |
|---|---|
| P5 Automatización Contable (piloto demo) | Base técnica del SaaS |
| Financial Pulse — Agente Tesorería | Capas 1-5 completas, Capa 6 (interfaz cliente) pendiente |
| Piloto Tucano Perú / Braidy Wonders | Activo en producción — código en `Tucano/`, datos operativos en `05_Piloto_Tucano/` |

## Confidencialidad

Este repositorio es **privado**. Varias carpetas contienen datos financieros reales de clientes y de la empresa piloto (montos, RUC, proveedores, cuentas bancarias) — no compartir su contenido fuera de este entorno.

Detalle completo de roles, formato de trabajo con Claude y contexto estratégico: ver `CLAUDE.md`.

Marca visual: `#0A1A3F` / `#C9A227`
