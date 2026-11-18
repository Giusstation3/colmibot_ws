# colmibot_datos

Paquete de JuanPa para COLMIBOT. Reúne el catálogo de máquinas, la bitácora de eventos, el guardado de fotos, el registro de mantenimiento (R7), el generador de códigos de barras y la detección de sonidos anormales (R4).

## Instalación

```bash
cd ~/colmibot_ws
colcon build --symlink-install --packages-select colmibot_datos
source install/setup.bash
```

## Dependencias

En una máquina limpia hay que instalarlas antes de compilar:

```bash
sudo apt install python3-numpy python3-opencv python3-pil libportaudio2
pip install --break-system-packages python-barcode sounddevice
```

| Librería | La usa | Instalación |
|---|---|---|
| numpy | `sonido.py`, `detector_sonido.py` | apt: `python3-numpy` |
| opencv | `guardar_foto` (`registro.py`) | apt: `python3-opencv` |
| python-barcode (y Pillow) | `generar_codigos` | pip: `python-barcode`; apt: `python3-pil` |
| sounddevice (y libportaudio2) | R4 con micrófono | pip: `sounddevice`; apt: `libportaudio2` |


## Dónde se guardan los datos

Los archivos que se generan al ejecutar quedan en `~/colmibot_datos/` (fuera del repositorio). Se puede cambiar la carpeta con la variable de entorno `COLMIBOT_DATOS`.

| Archivo | Contenido |
|---|---|
| `eventos.log` | Bitácora de eventos |
| `rondas/AAAA-MM-DD_HH-MM-SS/` | Fotos de cada ronda |
| `mantenimiento.csv` | Última fecha de mantenimiento por máquina |
| `codigos/` | Imágenes de los códigos de barras |
| `linea_base_audio.json` | Línea base del ambiente para el detector de sonidos |

## Catálogo de máquinas

`datos/maquinas.csv` lista las máquinas del área de pruebas. `maquinas.py` lo lee con `cargar_maquinas()`, y lo usan el registro de mantenimiento y el generador de códigos.

```csv
codigo,nombre,ubicacion
M-01,Torno CNC,Pasillo A
```

## Bitácora de eventos

```python
from colmibot_datos.registro import registrar_evento

registrar_evento('CHOQUE', 'Golpe frontal a 0.3 m/s')
```

Agrega una línea a `eventos.log` con este formato:

```
2026-11-18 13:05:22 | CHOQUE | Golpe frontal a 0.3 m/s
```

Los tipos se escriben en mayúsculas. Los que se usan hasta ahora: `CHOQUE` (R2), `SONIDO_ANORMAL` (R4), `INICIO_RONDA` y `FIN_RONDA`.

Para ver un ejemplo con tres líneas:

```bash
ros2 run colmibot_datos ejemplo_registro
```

## Fotos y rondas

```python
from colmibot_datos.registro import iniciar_ronda, guardar_foto, finalizar_ronda

iniciar_ronda()                    # crea la carpeta de la ronda y registra INICIO_RONDA
ruta = guardar_foto(imagen, 'M-01')
finalizar_ronda()                  # registra FIN_RONDA
```

- `guardar_foto(imagen, maquina)` recibe la imagen como arreglo de OpenCV, la guarda en la carpeta de la ronda como `2026-11-18_13-05-22_M-01.jpg` y devuelve la ruta completa del archivo.
- Si dos fotos de la misma máquina caen en el mismo segundo, la segunda lleva el sufijo `_2`.
- La ronda en curso se guarda en un archivo, así que nodos distintos comparten la misma carpeta. Si no hay ninguna ronda en curso, `guardar_foto` crea una.

## Registro de mantenimiento (R7)

```bash
ros2 run colmibot_datos mantenimiento registrar M-01
ros2 run colmibot_datos mantenimiento registrar M-01 --fecha 2026-11-18
ros2 run colmibot_datos mantenimiento consultar M-01
```

- Sin `--fecha`, `registrar` guarda la fecha de hoy.
- Las fechas van en formato `AAAA-MM-DD`.
- Si el código no existe en `maquinas.csv`, o la fecha no es válida, el programa avisa y no se detiene.

Formato de `mantenimiento.csv`:

```csv
codigo,ultima_fecha
M-01,2026-11-18
```

## Códigos de barras

```bash
ros2 run colmibot_datos generar_codigos
ros2 run colmibot_datos generar_codigos --salida ~/mis_codigos
```

Genera una imagen PNG por máquina del catálogo, en `~/colmibot_datos/codigos/` (`M-01.png`, `M-02.png`, ...). Los códigos son Code 128 a 300 dpi, listos para imprimir. Se leen con librerías como `pyzbar` o `zxing-cpp`; el lector de códigos de barras de OpenCV (`cv2.barcode`) solo reconoce EAN y UPC.

## Detección de sonidos anormales (R4)

El audio se analiza en ventanas de 0.5 s. De cada ventana se miden el volumen y la energía en 6 bandas de frecuencia, y se comparan con una línea base del ambiente normal.

1. Grabar la línea base:

   ```bash
   ros2 run colmibot_datos grabar_linea_base --segundos 30
   ros2 run colmibot_datos grabar_linea_base --archivo ambiente.wav
   ```

   Con `--dispositivo` se elige el micrófono por nombre o número. Los archivos WAV deben ser de 16 bits a 16 kHz.

2. Ejecutar el detector:

   ```bash
   ros2 run colmibot_datos detector_sonido
   ros2 run colmibot_datos detector_sonido --ros-args -p fuente:=prueba.wav
   ```

Cuando una ventana se aleja de la línea base más que el umbral, el nodo publica la alerta en `/alerta_sonido` (`std_msgs/String`) y la registra con `registrar_evento('SONIDO_ANORMAL', ...)`.

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `fuente` | `micro` | `micro` o la ruta de un archivo WAV |
| `dispositivo` | vacío | Micrófono (nombre o número) |
| `linea_base` | `~/colmibot_datos/linea_base_audio.json` | Archivo de la línea base |
| `umbral` | `4.0` | Desviaciones a partir de las cuales un sonido es anormal |
| `enfriamiento_s` | `5.0` | Segundos mínimos entre dos alertas |
