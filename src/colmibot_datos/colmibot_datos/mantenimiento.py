"""R7: registro de mantenimiento

Uso:
    ros2 run colmibot_datos mantenimiento registrar M-01
    ros2 run colmibot_datos mantenimiento registrar M-01 --fecha 2026-11-18
    ros2 run colmibot_datos mantenimiento consultar M-01
"""
import argparse
import csv
import os
from datetime import date, datetime

from colmibot_datos.maquinas import cargar_maquinas
from colmibot_datos.registro import carpeta_datos


def _archivo():
    return os.path.join(carpeta_datos(), 'mantenimiento.csv')


def _leer():
    datos = {}
    try:
        with open(_archivo(), newline='', encoding='utf-8') as f:
            for fila in csv.DictReader(f):
                codigo = (fila.get('codigo') or '').strip().upper()
                fecha = (fila.get('ultima_fecha') or '').strip()
                if codigo and fecha:
                    datos[codigo] = fecha
    except FileNotFoundError:
        pass
    return datos


def _escribir(datos):
    with open(_archivo(), 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(['codigo', 'ultima_fecha'])
        for codigo in sorted(datos):
            escritor.writerow([codigo, datos[codigo]])


def registrar(codigo, fecha=None):
    """Guarda la fecha de mantenimiento (hoy si no se da). Devuelve (ok, mensaje)."""
    codigo = str(codigo).strip().upper()
    if codigo not in cargar_maquinas():
        return False, f'AVISO: la maquina {codigo} no existe en maquinas.csv'
    fecha = fecha or date.today().isoformat()
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return False, f'AVISO: fecha invalida "{fecha}", usa AAAA-MM-DD'
    datos = _leer()
    datos[codigo] = fecha
    _escribir(datos)
    return True, f'{codigo}: mantenimiento registrado el {fecha}'


def consultar(codigo):
    """Devuelve (fecha o None, mensaje)"""
    codigo = str(codigo).strip().upper()
    if codigo not in cargar_maquinas():
        return None, f'AVISO: la maquina {codigo} no existe en maquinas.csv'
    fecha = _leer().get(codigo)
    if fecha is None:
        return None, f'{codigo}: sin mantenimiento registrado'
    return fecha, f'{codigo}: ultimo mantenimiento el {fecha}'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Registro de mantenimiento')
    sub = parser.add_subparsers(dest='accion', required=True)
    p_reg = sub.add_parser('registrar', help='guarda la fecha de mantenimiento')
    p_reg.add_argument('codigo')
    p_reg.add_argument('--fecha', help='AAAA-MM-DD (por defecto, hoy)')
    p_con = sub.add_parser('consultar', help='muestra la ultima fecha')
    p_con.add_argument('codigo')
    args = parser.parse_args(argv)
    if args.accion == 'registrar':
        _, mensaje = registrar(args.codigo, args.fecha)
    else:
        _, mensaje = consultar(args.codigo)
    print(mensaje)


if __name__ == '__main__':
    main()
