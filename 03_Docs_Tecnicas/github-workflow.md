# Workflow de GitHub desde Claude Code

**Versión:** 1.0 | **Uso:** Importar en `CLAUDE.md` raíz vía `@docs/github-workflow.md`
**Lector doble:** las **directivas en imperativo** son órdenes que Claude Code ejecuta. La **prosa breve** es el porqué — referencia para Gabriel cuando dude.

> El control de versiones no es burocracia. Es la red que te deja arriesgar sin caer. Cada commit es un punto al que puedes volver. Trabaja como quien sabe que puede deshacer.

---

## 0. Principio rector

Git existe para que ningún trabajo se pierda y para que cada cambio tenga una razón legible meses después. Todo lo que sigue se deriva de eso: si una regla no protege el trabajo o no aclara el porqué, sobra.

**Regla cero:** antes de cualquier operación destructiva o irreversible (borrar, reescribir historia, push forzado), el estado actual debe estar commiteado. Lo commiteado no se pierde.

---

## 1. Ciclo de trabajo por sesión

Claude Code sigue este orden en cada sesión de trabajo:

```
explorar  →  planificar  →  programar  →  commitear
```

**Directivas:**

- AL INICIAR una tarea, ejecutar `git status` para conocer el estado del árbol antes de tocar nada.
- NO mezclar exploración con cambios: leer y entender primero, escribir después.
- Para una feature grande, ANTES de programar, entrevistar a Gabriel y escribir un `SPEC.md` con el alcance acordado.
- AL TERMINAR un cambio lógico completo, commitearlo. No acumular cambios sin relación en el árbol de trabajo.

*Por qué:* el árbol de trabajo sucio (muchos cambios sin commitear, de tareas distintas) es donde se pierde trabajo y se mezclan cosas que luego no se pueden separar. Commitear cierra el ciclo y libera la cabeza para lo siguiente.

---

## 2. Commits

Un commit es una foto del cambio con una nota que explica **qué** y **por qué**.

**Directivas para Claude Code:**

- ESCRIBIR mensajes con verbo en infinitivo: `Agregar medida DAX de saldo proyectado`, `Eliminar bitácoras obsoletas del P3`, `Corregir cálculo de flujo neto multi-moneda`.
- HACER commits atómicos: un cambio lógico por commit. Si el mensaje necesita un "y" para describir dos cosas no relacionadas, son dos commits.
- ANTES de confirmar un commit, MOSTRAR a Gabriel el mensaje propuesto y el resumen de archivos incluidos. No commitear en silencio.
- USAR `git add <archivo>` específico por defecto. Reservar `git add .` solo cuando todos los cambios pendientes pertenecen al mismo commit lógico.

**Ciclo manual de referencia:**

```bash
git status                          # ver qué cambió
git add archivo1.md archivo2.py     # preparar archivos específicos
git commit -m "Mensaje en infinitivo, qué y por qué"
git push                            # subir a GitHub
```

*Por qué:* el commit atómico es lo que hace reversible un error. Si un cambio rompe algo, se revierte ese commit sin arrastrar trabajo bueno. El mensaje en infinitivo es convención —legible, consistente, te dice qué hace el commit si lo aplicas.

---

## 3. Push directo vs. rama + Pull Request

Gabriel trabaja solo. Eso define la regla base.

**Directiva — caso normal:**

- Trabajando solo y en cambios cotidianos, COMMITEAR directo a `main` y hacer push. NO crear ramas ni PRs por defecto.

**Directiva — cuándo SÍ usar rama + PR.** Crear una rama aparte y abrir un PR solo si se cumple uno de estos tres casos:

1. **Trabajo grande y arriesgado** que conviene aislar de `main` hasta verificar que funciona. Ejemplo concreto: la **Capa 4 / Memory Store del agente de tesorería**. Rama dedicada, commits ahí, vista consolidada antes de fusionar.
2. **Dejar documentado el porqué** de un bloque de trabajo importante — el PR es el lugar donde queda escrito el razonamiento de una decisión técnica grande.
3. **Entra alguien más al proyecto.** En cuanto el repo deja de ser de una sola persona, el PR pasa a ser la norma, no la excepción.

**Flujo con rama + PR (instrucción a Claude Code):**

```text
Crea una rama capa-4-memory-store, haz los commits ahí,
súbela a GitHub y abre un pull request con gh.
```

*Por qué:* el PR trabajando solo casi siempre es ceremonia vacía —te revisas a ti mismo. Pero en trabajo grande y arriesgado, la rama te da un lugar seguro para romper cosas sin tocar `main`, y el PR te da una vista consolidada de todo el bloque antes de integrarlo. Es la misma lógica de la red de seguridad: aíslas el riesgo.

---

## 4. Seguridad antes de push y PR

**Directivas — NO negociables:**

- ANTES de cada `push` o de abrir un PR, REVISAR el diff completo.
- NO incluir nunca en un commit: claves, tokens, credenciales de API, datos de clientes, rutas con información sensible.
- Si Claude Code detecta algo que parece una credencial o dato de cliente en el diff, DETENERSE y avisar a Gabriel antes de continuar. No commitear "por si acaso".
- VERIFICAR que `CLAUDE.local.md`, archivos `.env` y cualquier dato local estén en `.gitignore` y fuera del commit.

*Por qué:* lo que entra a GitHub queda en el historial aunque lo borres después —reescribir historia para sacar un secreto es costoso y a veces imposible si ya se clonó. La revisión del diff es la última puerta antes de que algo sea permanente.

---

## 5. Operaciones destructivas

**Directivas:**

- ANTES de borrar archivos, reescribir historia, hacer `git reset --hard` o `push --force`, CONFIRMAR que el estado previo está commiteado (red de seguridad de la Regla cero).
- Para eliminar bitácoras u obsoletos del repo, USAR `git rm <archivo>` y hacerlo en un **commit aparte**, separado de la reorganización. Ejemplo: `git rm docs/INSTRUCCIONES_PROYECTO_3.md`.
- NUNCA hacer `push --force` a `main`. Si una rama necesita force-push, confirmarlo explícitamente con Gabriel primero.
- ANTES de borrar archivos dudosos o posibles duplicados, COMPARARLOS y confirmar que no se pierde nada único. Precedente real: se verificó que las skills `Flujo_de_caja/` y `forecast-cashflow/` **eran diferentes** y se conservaron ambas. La verificación va antes del borrado, siempre.

*Por qué:* lo destructivo en Git casi siempre es recuperable **si hay un commit detrás**. Sin él, no. La separación de borrados en su propio commit es lo que te deja revertir "quité esto" sin revertir "reorganicé aquello".

---

## 6. Relación con los archivos `.md` del proyecto

Esto conecta el workflow de Git con la limpieza de documentación ya acordada.

| Categoría | Destino | Va a Git |
|-----------|---------|----------|
| **Instrucciones** (cómo trabaja Claude) | `CLAUDE.md` | Sí, versionado |
| **Documentación vigente** | `docs/` | Sí, versionado |
| **Bitácoras / avances** | El historial de Git **es** la bitácora | No como `.md` manual |
| **Operativos `.claude/`** (estilo, `SKILL.md`) | `.claude/` | Sí — son código activo, NO se tocan |

**Directiva clave:** los avances y la bitácora del proyecto NO se mantienen como archivos `.md` manuales. El historial de commits es la bitácora. Un mensaje de commit bien escrito reemplaza una entrada de log.

*Por qué:* duplicar la historia en un `.md` manual y en Git garantiza que ambos se desincronicen. Una sola fuente de verdad. El `git log` ya responde "qué se hizo y cuándo" mejor que cualquier archivo que actualices a mano.

---

## 7. Checklist operativo — pegar mentalmente antes de cerrar sesión

- [ ] `git status` — ¿el árbol está limpio o hay cambios sin commitear?
- [ ] ¿Cada commit pendiente es atómico y tiene mensaje en infinitivo?
- [ ] ¿Revisé el diff? ¿Hay algo sensible (claves, tokens, datos)?
- [ ] ¿Esto es trabajo normal (push a `main`) o de los tres casos de PR?
- [ ] Si borré algo: ¿está en commit aparte y verifiqué que no era único?
- [ ] `git push` — subido y respaldado en GitHub.

---

*Documento de uso interno — Proyecto Gabriel / Claude Code.*
*Actualizar cuando cambie el flujo de trabajo o entre alguien más al repositorio.*
