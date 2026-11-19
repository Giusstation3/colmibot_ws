"""Genera la imagen de codigo de barras (Code128) de cada maquina

Uso:
    ros2 run colmibot_datos generar_codigos
    ros2 run colmibot_datos generar_codigos --salida ~/mis_codigos
Las imagenes quedan en ~/colmibot_datos/codigos/M-01.png, M-02.png, ...
"""
import argparse
import os

from colmibot_datos.maquinas import cargar_maquinas
from colmibot_datos.registro import carpeta_datos

OPCIONES = {
    'dpi': 300,
    'module_width': 0.4,    # mm por barra mas angosta
    'module_height': 20.0,  # mm de alto de las barras
    'quiet_zone': 10.0,     # mm de margen blanco a los lados
    'font_size': 12,
    'text_distance': 4.0,
}


def generar(carpeta=None):
    """Crea un PNG por maquina y devuelve la lista de rutas."""
    import barcode
    from barcode.writer import ImageWriter

    carpeta = carpeta or os.path.join(carpeta_datos(), 'codigos')
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    for codigo in cargar_maquinas():
        imagen = barcode.get('code128', codigo, writer=ImageWriter())
        base = os.path.join(carpeta, codigo)
        try:
            ruta = imagen.save(base, options=OPCIONES)
        except OSError:  # no hay fuente para el texto: se guarda sin texto
            ruta = imagen.save(base, options=dict(OPCIONES, write_text=False))
        rutas.append(ruta)
    return rutas


def main(argv=None):
    parser = argparse.ArgumentParser(description='Genera codigos de barras')
    parser.add_argument('--salida', help='carpeta de salida')
    args = parser.parse_args(argv)
    salida = os.path.expanduser(args.salida) if args.salida else None
    for ruta in generar(salida):
        print(ruta)


if __name__ == '__main__':
    main()
