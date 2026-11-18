"""Catalogo de maquinas: codigo, nombre, ubicacion"""
import csv
import os


def ruta_maquinas():
    """Busca maquinas.csv: variable COLMIBOT_MAQUINAS, paquete instalado o repo."""
    ruta = os.environ.get('COLMIBOT_MAQUINAS')
    if ruta:
        return ruta
    try:
        from ament_index_python.packages import get_package_share_directory
        ruta = os.path.join(get_package_share_directory('colmibot_datos'),
                            'datos', 'maquinas.csv')
        if os.path.exists(ruta):
            return ruta
    except Exception:
        pass
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raiz, 'datos', 'maquinas.csv')


def cargar_maquinas():
    """Devuelve {codigo: {'nombre': ..., 'ubicacion': ...}}."""
    maquinas = {}
    with open(ruta_maquinas(), newline='', encoding='utf-8-sig') as f:
        for fila in csv.DictReader(f):
            codigo = (fila.get('codigo') or '').strip().upper()
            if codigo:
                maquinas[codigo] = {
                    'nombre': (fila.get('nombre') or '').strip(),
                    'ubicacion': (fila.get('ubicacion') or '').strip(),
                }
    return maquinas
