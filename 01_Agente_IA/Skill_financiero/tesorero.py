#!/usr/bin/env python3
"""
tesorero.py — Agente de Tesorería con memoria persistente
Gabriel Untiveros | Skill_financiero

Uso:
    python tesorero.py
    python tesorero.py --reset-memory     # borra el historial y empieza fresco
    python tesorero.py --db otro.db       # usa una base de datos diferente

Comandos en la sesión:
    /historial          — ver últimas sesiones
    /pendientes         — ver acciones pendientes
    /hecho KEY VALOR    — guardar configuración del cliente
    /completar N        — marcar acción pendiente N como completada
    /reset              — borrar memoria (pide confirmación)
    /salir              — terminar la sesión
    /ayuda              — mostrar esta lista
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

# ── Dependencia opcional: anthropic ──────────────────────────────────────────
try:
    import anthropic
except ImportError:
    print("ERROR: El paquete 'anthropic' no está instalado.")
    print("       Activa el venv: .venv\\Scripts\\activate")
    print("       Luego: pip install anthropic")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────

BASE        = Path(__file__).parent.resolve()
SKILLS_BASE = BASE / '.claude' / 'skills'
DATA_DIR    = BASE / 'data'
MEMORY_DIR  = DATA_DIR / 'memory'
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

MODEL = 'claude-sonnet-4-6'

# Cargar API key desde .env
_env_file = BASE / '.env'
if _env_file.exists():
    for _line in _env_file.read_text(encoding='utf-8').splitlines():
        if '=' in _line and not _line.startswith('#'):
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

_api_key = os.environ.get('ANTHROPIC_API_KEY', '')
if not _api_key.startswith('sk-ant-'):
    print("ERROR: ANTHROPIC_API_KEY no encontrada.")
    print(f"       Crea {BASE / '.env'} con: ANTHROPIC_API_KEY=sk-ant-...")
    sys.exit(1)

client = anthropic.Anthropic(api_key=_api_key)

# ─────────────────────────────────────────────────────────────────────────────
#  TOOL DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DEFS = [
    {
        'name': 'bash_execute',
        'description': (
            'Ejecuta un script Python de los skills de tesoreria. '
            'Usa esto para: forecast de caja (batch_dias_de_caja.py), '
            'forecast individual (rolling_mean_cashflow.py CUENTA-ID 14), '
            'reporte semanal (generar_reporte.py). '
            'El comando DEBE ser una lista Python de strings, no un string JSON.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'command': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Lista de strings. Ej: ["python", "ruta/script.py"]'
                }
            },
            'required': ['command']
        }
    },
    {
        'name': 'read_skill',
        'description': (
            'Lee el contenido de un SKILL.md para cargar la politica bajo demanda. '
            'Skills disponibles: forecast-cashflow/SKILL.md, '
            'alerta-tesoreria/SKILL.md, reporte-semanal/SKILL.md.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'skill_name': {
                    'type': 'string',
                    'description': 'Nombre del skill. Ej: alerta-tesoreria/SKILL.md'
                }
            },
            'required': ['skill_name']
        }
    }
]

SYSTEM_PROMPT_BASE = f"""
Eres un agente de tesoreria financiero con memoria de sesiones previas.
Cuando el historial del cliente esté disponible (sección HISTORIAL DEL CLIENTE),
úsalo para dar contexto comparativo: qué cambió, qué se resolvió, qué sigue pendiente.

HERRAMIENTAS:
- bash_execute: ejecuta scripts Python de los skills (command DEBE ser lista Python)
- read_skill: lee un SKILL.md para cargar la politica cuando la necesitas

SCRIPTS DISPONIBLES (usar con bash_execute):
  Todas las cuentas:  ["{sys.executable}", "{(SKILLS_BASE / 'forecast-cashflow' / 'batch_dias_de_caja.py').as_posix()}"]
  Cuenta individual:  ["{sys.executable}", "{(SKILLS_BASE / 'forecast-cashflow' / 'rolling_mean_cashflow.py').as_posix()}", "CUENTA-ID", "14"]
  Reporte semanal:    ["{sys.executable}", "{(SKILLS_BASE / 'reporte-semanal' / 'generar_reporte.py').as_posix()}"]

SKILLS (cargar con read_skill cuando la tarea lo requiera):
  forecast-cashflow/SKILL.md  -> cuando pidan forecast o proyeccion
  alerta-tesoreria/SKILL.md   -> cuando pidan alertas o revision de liquidez
  reporte-semanal/SKILL.md    -> cuando pidan el reporte semanal

REGLA PRINCIPAL: Usa UN script para procesar datos de todas las cuentas.
No hagas llamadas individuales por cuenta — ese es el anti-patron.
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
#  MEMORY STORE
# ─────────────────────────────────────────────────────────────────────────────

class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id          TEXT PRIMARY KEY,
                    fecha       TEXT NOT NULL,
                    query       TEXT NOT NULL,
                    summary     TEXT,
                    turns       INTEGER,
                    tokens_in   INTEGER,
                    tokens_out  INTEGER
                );
                CREATE TABLE IF NOT EXISTS alertas (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id   TEXT    NOT NULL,
                    cuenta_id    TEXT    NOT NULL,
                    nivel        TEXT    NOT NULL,
                    saldo_actual REAL,
                    dias_de_caja REAL,
                    flujo_neto   REAL,
                    fecha        TEXT    NOT NULL
                );
                CREATE TABLE IF NOT EXISTS client_facts (
                    key        TEXT PRIMARY KEY,
                    value      TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pending_actions (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    accion     TEXT NOT NULL,
                    cuenta_id  TEXT,
                    completed  INTEGER DEFAULT 0,
                    created_at TEXT    NOT NULL
                );
            """)

    # ── WRITE ────────────────────────────────────────────────────────────────

    def save_session(self, session_id: str, query: str, result: dict) -> None:
        summary = (result.get('final_text') or '')[:300].replace('\n', ' ')
        fecha   = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO sessions VALUES (?,?,?,?,?,?,?)',
                (session_id, fecha, query, summary,
                 result.get('turns'), result.get('tokens_in'), result.get('tokens_out'))
            )

    def save_alertas(self, session_id: str, states: list) -> None:
        fecha = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            for s in states:
                conn.execute(
                    'INSERT INTO alertas '
                    '(session_id, cuenta_id, nivel, saldo_actual, dias_de_caja, flujo_neto, fecha) '
                    'VALUES (?,?,?,?,?,?,?)',
                    (session_id, s.get('cuenta_id', ''), s.get('nivel', 'OK'),
                     s.get('saldo_actual'), s.get('dias_de_caja'), s.get('flujo_neto_dia'), fecha)
                )

    def save_fact(self, key: str, value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO client_facts VALUES (?,?,?)',
                (key, value, datetime.utcnow().isoformat())
            )

    def save_pending_action(self, session_id: str, accion: str, cuenta_id: str = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO pending_actions (session_id, accion, cuenta_id, created_at) VALUES (?,?,?,?)',
                (session_id, accion, cuenta_id, datetime.utcnow().isoformat())
            )

    def mark_completed(self, action_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute('UPDATE pending_actions SET completed=1 WHERE id=?', (action_id,))
            return cur.rowcount > 0

    def reset(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                DELETE FROM sessions;
                DELETE FROM alertas;
                DELETE FROM client_facts;
                DELETE FROM pending_actions;
            """)

    # ── READ ─────────────────────────────────────────────────────────────────

    def get_recent_sessions(self, n: int = 3) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM sessions ORDER BY fecha DESC LIMIT ?', (n,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_last_state_per_account(self) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT a.* FROM alertas a
                INNER JOIN (
                    SELECT cuenta_id, MAX(fecha) AS max_fecha
                    FROM alertas GROUP BY cuenta_id
                ) latest ON a.cuenta_id = latest.cuenta_id
                         AND a.fecha    = latest.max_fecha
                ORDER BY a.nivel DESC, a.cuenta_id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_pending_actions(self) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM pending_actions WHERE completed=0 ORDER BY created_at DESC'
            ).fetchall()
            return [dict(r) for r in rows]

    def get_client_facts(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('SELECT key, value FROM client_facts').fetchall()
            return {r[0]: r[1] for r in rows}

    def count_sessions(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]

    def build_context_block(self) -> str:
        sessions = self.get_recent_sessions(3)
        if not sessions:
            return ''

        states  = self.get_last_state_per_account()
        pending = self.get_pending_actions()
        facts   = self.get_client_facts()

        lines = [
            '',
            '## HISTORIAL DEL CLIENTE (referencia interna — no citar textualmente al usuario)',
            '',
            '### Sesiones recientes:',
        ]
        for s in sessions:
            fecha_str = s['fecha'][:10]
            summary   = (s['summary'] or '')[:150].replace('\n', ' ')
            lines.append(f'- [{fecha_str}] "{s["query"]}" → {summary}')

        if states:
            lines.append('')
            lines.append('### Último estado conocido por cuenta:')
            nivel_emoji = {'CRITICO': '🔴', 'ALTO': '🟠', 'MEDIO': '🟡', 'OK': '🟢'}
            for a in states:
                emoji  = nivel_emoji.get(a['nivel'], '⚪')
                flujo  = a['flujo_neto'] or 0.0
                saldo  = a['saldo_actual'] or 0.0
                lines.append(
                    f"  {a['cuenta_id']}: {emoji} {a['nivel']} | "
                    f"Saldo: {saldo:,.0f} | "
                    f"Flujo/día: {flujo:+.0f} | "
                    f"Registrado: {a['fecha'][:10]}"
                )

        if pending:
            lines.append('')
            lines.append('### Acciones pendientes (recomendadas, no completadas):')
            for p in pending:
                cuenta_str = f" [{p['cuenta_id']}]" if p['cuenta_id'] else ''
                lines.append(f"  [{p['id']}] {p['accion']}{cuenta_str} (desde: {p['created_at'][:10]})")

        if facts:
            lines.append('')
            lines.append('### Configuración del cliente:')
            for k, v in facts.items():
                lines.append(f'  - {k}: {v}')

        lines.append('')
        return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  DISPATCH + EXTRACCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def dispatch(tool_name: str, tool_input: dict) -> str:
    if tool_name == 'bash_execute':
        command = tool_input['command']
        if isinstance(command, str):
            try:
                command = json.loads(command)
            except json.JSONDecodeError:
                command = command.split()
        result = subprocess.run(
            command, capture_output=True, text=True, cwd=str(BASE), timeout=30
        )
        return result.stdout.strip() if result.returncode == 0 else \
               f'ERROR (exit {result.returncode}): {result.stderr.strip()}'

    elif tool_name == 'read_skill':
        skill_path = SKILLS_BASE / tool_input['skill_name']
        return skill_path.read_text(encoding='utf-8') if skill_path.exists() else \
               f'ERROR: Skill no encontrado: {skill_path}'

    return f'ERROR: Tool desconocida: {tool_name}'


def extract_account_state(tool_log: list) -> list:
    states, seen = [], set()
    for entry in tool_log:
        if entry.get('tool') != 'bash_execute':
            continue
        output = entry.get('output', '')
        if not output or output.startswith('ERROR'):
            continue
        try:
            data = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict) or 'cuenta_id' not in item:
                continue
            cid = item['cuenta_id']
            if cid in seen:
                continue
            seen.add(cid)
            dias        = item.get('dias_de_caja', 999)
            requiere_at = item.get('requiere_atencion', False)
            if not requiere_at or dias == 999:
                nivel = 'OK'
            elif dias < 5:
                nivel = 'CRITICO'
            elif dias < 10:
                nivel = 'ALTO'
            elif dias < 20:
                nivel = 'MEDIO'
            else:
                nivel = 'OK'
            states.append({
                'cuenta_id'     : cid,
                'nivel'         : nivel,
                'saldo_actual'  : item.get('saldo_actual', 0.0),
                'dias_de_caja'  : dias,
                'flujo_neto_dia': item.get('flujo_neto_dia', 0.0),
            })
    return states


# ─────────────────────────────────────────────────────────────────────────────
#  AGENT LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(prompt: str, memory: MemoryStore, max_turns: int = 10) -> dict:
    context_block = memory.build_context_block()
    system_prompt = SYSTEM_PROMPT_BASE + ('\n\n' + context_block if context_block else '')

    session_id = str(uuid.uuid4())[:8]
    messages   = [{'role': 'user', 'content': prompt}]
    tokens_in  = tokens_out = turns = 0
    final_text = ''
    tool_log   = []

    while turns < max_turns:
        turns += 1
        resp = client.messages.create(
            model      = MODEL,
            max_tokens = 4096,
            system     = system_prompt,
            tools      = TOOL_DEFS,
            messages   = messages,
        )
        tokens_in  += resp.usage.input_tokens
        tokens_out += resp.usage.output_tokens

        if resp.stop_reason == 'end_turn':
            final_text = ''.join(b.text for b in resp.content if b.type == 'text')
            break

        tool_results = []
        for block in resp.content:
            if block.type == 'tool_use':
                try:
                    output = dispatch(block.name, block.input)
                except Exception as e:
                    output = f'ERROR: {e}'
                tool_log.append({'turn': turns, 'tool': block.name,
                                 'input': block.input, 'output': output})
                tool_results.append({
                    'type': 'tool_result', 'tool_use_id': block.id, 'content': str(output)
                })

        if not tool_results:
            final_text = ''.join(b.text for b in resp.content if b.type == 'text')
            break

        messages.append({'role': 'assistant', 'content': resp.content})
        messages.append({'role': 'user',      'content': tool_results})

    result = {
        'session_id': session_id,
        'final_text': final_text,
        'turns'     : turns,
        'tokens_in' : tokens_in,
        'tokens_out': tokens_out,
        'tool_log'  : tool_log,
    }

    memory.save_session(session_id, prompt, result)
    states = extract_account_state(tool_log)
    if states:
        memory.save_alertas(session_id, states)

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  COMANDOS DE SESIÓN
# ─────────────────────────────────────────────────────────────────────────────

HELP_TEXT = """
Comandos disponibles:
  /historial          — ver las últimas 5 sesiones
  /pendientes         — ver acciones pendientes
  /hecho KEY VALOR    — guardar configuración del cliente
  /completar N        — marcar acción N como completada
  /reset              — borrar toda la memoria (pide confirmación)
  /salir              — terminar la sesión
  /ayuda              — mostrar esta lista
"""

NIVEL_EMOJI = {'CRITICO': '🔴', 'ALTO': '🟠', 'MEDIO': '🟡', 'OK': '🟢'}


def cmd_historial(memory: MemoryStore) -> None:
    sessions = memory.get_recent_sessions(5)
    if not sessions:
        print("  Sin historial.\n")
        return
    print(f"\n  Últimas {len(sessions)} sesiones:\n")
    for s in sessions:
        tokens = (s['tokens_in'] or 0) + (s['tokens_out'] or 0)
        print(f"  [{s['fecha'][:16]}] {s['query'][:60]}")
        print(f"   Turns: {s['turns']} | Tokens: {tokens:,}")
        if s['summary']:
            print(f"   {s['summary'][:100]}...")
        print()


def cmd_pendientes(memory: MemoryStore) -> None:
    pending = memory.get_pending_actions()
    if not pending:
        print("  Sin acciones pendientes.\n")
        return
    print(f"\n  Acciones pendientes ({len(pending)}):\n")
    for p in pending:
        cuenta = f" [{p['cuenta_id']}]" if p['cuenta_id'] else ''
        print(f"  [{p['id']}]{cuenta} {p['accion']}")
        print(f"       Registrado: {p['created_at'][:10]}")
    print()


def cmd_estado(memory: MemoryStore) -> None:
    """Muestra el estado resumido al inicio de sesión."""
    n_sessions = memory.count_sessions()
    states     = memory.get_last_state_per_account()
    pending    = memory.get_pending_actions()

    print(f"\n  Historial: {n_sessions} sesión(es) guardada(s)")
    if states:
        print("  Cuentas (último estado conocido):")
        for a in states:
            emoji = NIVEL_EMOJI.get(a['nivel'], '⚪')
            print(f"    {a['cuenta_id']}: {emoji} {a['nivel']} | "
                  f"Saldo: {a['saldo_actual']:,.0f} | "
                  f"Flujo/día: {a['flujo_neto']:+.0f}")
    if pending:
        print(f"  Acciones pendientes: {len(pending)} (usa /pendientes para ver)")
    print()


def handle_command(line: str, memory: MemoryStore, last_session_id: list) -> bool:
    """
    Maneja comandos /. Retorna True si fue un comando válido, False si no lo fue.
    """
    parts = line.strip().split(maxsplit=2)
    cmd   = parts[0].lower()

    if cmd == '/salir':
        print("\n  Hasta la próxima.\n")
        sys.exit(0)

    elif cmd == '/ayuda':
        print(HELP_TEXT)
        return True

    elif cmd == '/historial':
        cmd_historial(memory)
        return True

    elif cmd == '/pendientes':
        cmd_pendientes(memory)
        return True

    elif cmd == '/hecho':
        if len(parts) < 3:
            print("  Uso: /hecho CLAVE VALOR\n  Ej:  /hecho CUENTA-002.alerta Revisar día 15\n")
        else:
            memory.save_fact(parts[1], parts[2])
            print(f"  Guardado: {parts[1]} = {parts[2]}\n")
        return True

    elif cmd == '/completar':
        if len(parts) < 2 or not parts[1].isdigit():
            print("  Uso: /completar N   (N es el número de la acción)\n")
        else:
            ok = memory.mark_completed(int(parts[1]))
            print(f"  {'Acción marcada como completada.' if ok else 'No se encontró esa acción.'}\n")
        return True

    elif cmd == '/pendiente':
        # Alias para guardar una acción manualmente
        if len(parts) < 2:
            print("  Uso: /pendiente DESCRIPCIÓN [CUENTA-ID]\n")
        else:
            accion    = parts[1] if len(parts) == 2 else f"{parts[1]} {parts[2]}"
            cuenta_id = None
            if last_session_id:
                memory.save_pending_action(last_session_id[0], accion, cuenta_id)
                print(f"  Acción registrada: {accion}\n")
            else:
                print("  No hay sesión activa. Haz una consulta primero.\n")
        return True

    elif cmd == '/reset':
        confirm = input("  ¿Seguro? Esto borra todo el historial. (escribe 'sí'): ").strip()
        if confirm.lower() in ('sí', 'si', 'yes', 'y'):
            memory.reset()
            print("  Memoria borrada.\n")
        else:
            print("  Cancelado.\n")
        return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Agente de Tesorería — CFO Interno')
    parser.add_argument('--db',           default=str(MEMORY_DIR / 'agente_tesoreria.db'),
                        help='Ruta a la base de datos SQLite de memoria')
    parser.add_argument('--reset-memory', action='store_true',
                        help='Borrar la memoria antes de iniciar')
    args = parser.parse_args()

    db_path = Path(args.db)
    memory  = MemoryStore(db_path)

    if args.reset_memory:
        memory.reset()
        print(f"Memoria borrada: {db_path.name}")

    # ── Banner ────────────────────────────────────────────────────────────────
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║   AGENTE DE TESORERÍA — Gabriel Untiveros        ║")
    print("  ║   CFO Interno | claude-sonnet-4-6                ║")
    print(f"  ║   DB: {db_path.name:<43}║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

    # Estado de memoria al inicio
    cmd_estado(memory)

    # Hint si hay memoria
    if memory.count_sessions() > 0:
        print("  El agente tiene historial de sesiones previas.")
        print("  Puedes preguntarle directamente qué cambió o qué está pendiente.")
    else:
        print("  Primera sesión — sin historial previo.")
    print("  Escribe /ayuda para ver los comandos disponibles.")
    print()

    # ── Loop principal ────────────────────────────────────────────────────────
    last_session_id: list = []   # se actualiza tras cada consulta

    while True:
        try:
            line = input("  Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Hasta la próxima.\n")
            break

        if not line:
            continue

        # Comandos /
        if line.startswith('/'):
            handle_command(line, memory, last_session_id)
            continue

        # Consulta al agente
        print()
        print("  Pensando...", end='', flush=True)

        try:
            result = run_agent(line, memory)
        except anthropic.APIError as e:
            print(f"\r  ERROR API: {e}\n")
            continue
        except Exception as e:
            print(f"\r  ERROR: {e}\n")
            continue

        print('\r', end='')  # limpiar "Pensando..."

        # Respuesta
        print()
        print("  Agente:")
        print()
        for text_line in (result['final_text'] or '(sin respuesta)').splitlines():
            print(f"  {text_line}")
        print()

        # Métricas compactas
        tokens_total = result['tokens_in'] + result['tokens_out']
        costo_usd    = result['tokens_in'] * 3e-6 + result['tokens_out'] * 15e-6
        tools_usados = [t['tool'] for t in result['tool_log']]
        print(f"  ── Turns: {result['turns']} | Tokens: {tokens_total:,} | "
              f"USD ${costo_usd:.4f} | Tools: {tools_usados}")
        print()

        last_session_id[:] = [result['session_id']]


if __name__ == '__main__':
    main()
