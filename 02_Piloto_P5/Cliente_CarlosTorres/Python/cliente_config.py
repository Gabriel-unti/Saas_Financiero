import json
from pathlib import Path


def cargar_cliente(cliente_id: str, config_dir: Path) -> dict:
    """
    Carga la configuracion de un cliente (codigos estructurales, plan de cuentas,
    plantilla de diario, base de memoria) desde config/clientes/{cliente_id}.json.
    El plan de cuentas referenciado se resuelve y se adjunta bajo la clave 'plan'.
    """
    cliente_path = config_dir / 'clientes' / f'{cliente_id}.json'
    with open(cliente_path, encoding='utf-8') as f:
        cliente = json.load(f)

    plan_path = config_dir / 'planes' / cliente['plan_cuentas']
    with open(plan_path, encoding='utf-8') as f:
        cliente['plan'] = json.load(f)

    return cliente


def cuentas_gasto(cliente: dict) -> dict:
    """
    Subconjunto de cuentas de gasto (codigo empieza con '6') utilizables para
    clasificacion. Si el plan trae metadata de nivel (cuentas_meta), se filtra
    ademas a cuentas tipo 'Movimiento' (las unicas donde se puede contabilizar).
    """
    plan = cliente['plan']
    cuentas = plan['cuentas']
    meta = plan.get('cuentas_meta')

    resultado = {}
    for codigo, detalle in cuentas.items():
        if not codigo.startswith('6'):
            continue
        if meta and meta.get(codigo, {}).get('tipo') not in (None, 'Movimiento'):
            continue
        resultado[codigo] = detalle
    return resultado
