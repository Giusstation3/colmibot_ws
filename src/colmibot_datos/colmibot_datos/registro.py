"""Bitacora de eventos y almacenamiento fotos de COLMIBOT

Uso desde otros nodos:
    from colmibot_datos.registro import registrar_evento, guardar_foto
"""
import os
from datetime import datetime

# Los archivos que se escriben durante la ejecucion
# Se puede cambiar con la variable de entorno COLMIBOT_DATOS


def carpeta_datos():
    base = os.environ.get('COLMIBOT_DATOS',
                          os.path.expanduser('~/colmibot_datos'))
    os.makedirs(base, exist_ok=True)
    return base


def registrar_evento(tipo, detalle):
    """Agrega una linea a eventos.log: 'AAAA-MM-DD HH:MM:SS | TIPO | detalle'."""
    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tipo = str(tipo).strip().upper()
    detalle = ' '.join(str(detalle).split())  # sin saltos de linea
    linea = f'{ahora} | {tipo} | {detalle}'
    with open(os.path.join(carpeta_datos(), 'eventos.log'), 'a',
              encoding='utf-8') as f:
        f.write(linea + '\n')
    return linea


def _archivo_ronda():
    return os.path.join(carpeta_datos(), 'ronda_actual.txt')


def _crear_carpeta_ronda():
    nombre = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    carpeta = os.path.join(carpeta_datos(), 'rondas', nombre)
    os.makedirs(carpeta, exist_ok=True)
    with open(_archivo_ronda(), 'w', encoding='utf-8') as f:
        f.write(carpeta)
    return carpeta


def carpeta_ronda():
    """Carpeta de la ronda en curso; si no hay ninguna, crea una."""
    try:
        with open(_archivo_ronda(), encoding='utf-8') as f:
            carpeta = f.read().strip()
        if carpeta and os.path.isdir(carpeta):
            return carpeta
    except FileNotFoundError:
        pass
    return _crear_carpeta_ronda()


def iniciar_ronda():
    """Crea la carpeta de una ronda nueva y registra INICIO_RONDA."""
    carpeta = _crear_carpeta_ronda()
    registrar_evento('INICIO_RONDA', carpeta)
    return carpeta


def finalizar_ronda():
    """Registra FIN_RONDA y cierra la ronda en curso."""
    registrar_evento('FIN_RONDA', carpeta_ronda())
    try:
        os.remove(_archivo_ronda())
    except FileNotFoundError:
        pass


def guardar_foto(imagen, maquina):
    """Guarda una imagen de OpenCV como AAAA-MM-DD_HH-MM-SS_MAQUINA.jpg.

    Devuelve la ruta completa del archivo.
    """
    import cv2  # se importa aqui para que registrar_evento no lo necesite

    nombre = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + f'_{maquina}'
    carpeta = carpeta_ronda()
    ruta = os.path.join(carpeta, nombre + '.jpg')
    n = 2
    while os.path.exists(ruta):  # misma maquina en el mismo segundo
        ruta = os.path.join(carpeta, f'{nombre}_{n}.jpg')
        n += 1
    if not cv2.imwrite(ruta, imagen):
        raise OSError(f'No se pudo guardar la foto en {ruta}')
    return ruta


def ejemplo():
    """Ejemplo de uso: genera 3 lineas en eventos.log."""
    registrar_evento('INICIO_RONDA', 'Ejemplo de uso')
    registrar_evento('CHOQUE', 'Golpe frontal a 0.3 m/s')
    registrar_evento('FIN_RONDA', 'Ejemplo de uso')
    print(f"Listo, revisa {os.path.join(carpeta_datos(), 'eventos.log')}")
