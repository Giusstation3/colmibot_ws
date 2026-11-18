"""R4: nodo que vigila el audio y avisa de sonidos anormales

Publica la alerta en /alerta_sonido (std_msgs/String) y la registra con
registrar_evento('SONIDO_ANORMAL', ...). Necesita una linea base previa:
    ros2 run colmibot_datos grabar_linea_base --segundos 30
Uso con microfono:
    ros2 run colmibot_datos detector_sonido
Uso con un archivo WAV (para pruebas sin microfono):
    ros2 run colmibot_datos detector_sonido --ros-args -p fuente:=prueba.wav
"""
import os
import queue
import time

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from colmibot_datos import sonido
from colmibot_datos.registro import registrar_evento


class DetectorSonido(Node):

    def __init__(self):
        super().__init__('detector_sonido')
        self.declare_parameter('fuente', 'micro')  # 'micro' o ruta de un WAV
        self.declare_parameter('dispositivo', '')
        self.declare_parameter('linea_base', '')
        self.declare_parameter('umbral', 4.0)
        self.declare_parameter('enfriamiento_s', 5.0)

        ruta_base = (self.get_parameter('linea_base').value
                     or sonido.ruta_linea_base())
        try:
            self.base = sonido.cargar_linea_base(ruta_base)
        except FileNotFoundError:
            raise RuntimeError(
                f'No hay linea base en {ruta_base}. Primero corre: '
                'ros2 run colmibot_datos grabar_linea_base')
        self.fs = self.base['fs']
        self.ventana_s = self.base['ventana_s']
        self.umbral = float(self.get_parameter('umbral').value)
        self.enfriamiento = float(self.get_parameter('enfriamiento_s').value)
        self.ultima_alerta = -1e9
        self.pub = self.create_publisher(String, '/alerta_sonido', 10)
        self.cola = queue.Queue(maxsize=20)
        self.stream = None

        fuente = self.get_parameter('fuente').value
        if fuente == 'micro':
            self._abrir_microfono()
            self.timer = self.create_timer(0.1, self._procesar_cola)
        else:
            audio, fs = sonido.leer_wav(os.path.expanduser(fuente))
            if fs != self.fs:
                raise RuntimeError(
                    f'El WAV es de {fs} Hz y la linea base de {self.fs} Hz')
            self.ventanas = sonido.ventanas(audio, fs, self.ventana_s)
            self.timer = self.create_timer(self.ventana_s, self._siguiente)
        self.get_logger().info(
            f'Vigilando audio (fuente: {fuente}, umbral: {self.umbral})')

    def _abrir_microfono(self):
        import sounddevice as sd  # requiere libportaudio2
        dispositivo = self.get_parameter('dispositivo').value or None
        if dispositivo and dispositivo.isdigit():
            dispositivo = int(dispositivo)

        def llegada(datos, cuadros, tiempo, estado):
            try:
                self.cola.put_nowait(datos[:, 0].astype(np.float64).copy())
            except queue.Full:
                pass

        self.stream = sd.InputStream(
            samplerate=self.fs, channels=1, dtype='float32',
            blocksize=int(self.fs * self.ventana_s), device=dispositivo,
            callback=llegada)
        self.stream.start()

    def _procesar_cola(self):
        while not self.cola.empty():
            self._analizar(self.cola.get_nowait())

    def _siguiente(self):
        try:
            ventana = next(self.ventanas)
        except StopIteration:
            self.get_logger().info('Fin del archivo de audio')
            self.timer.cancel()
            return
        self._analizar(ventana)

    def _analizar(self, ventana):
        vec = sonido.caracteristicas(ventana, self.fs)
        valor, i = sonido.puntaje(vec, self.base)
        if valor <= self.umbral:
            return
        ahora = time.monotonic()
        if ahora - self.ultima_alerta < self.enfriamiento:
            return
        self.ultima_alerta = ahora
        detalle = sonido.describir(vec, self.base, i, valor)
        self.pub.publish(String(data=detalle))
        registrar_evento('SONIDO_ANORMAL', detalle)
        self.get_logger().warn(f'Sonido anormal: {detalle}')

    def destroy_node(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    try:
        nodo = DetectorSonido()
    except RuntimeError as error:
        print(f'ERROR: {error}')
        rclpy.shutdown()
        return
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
