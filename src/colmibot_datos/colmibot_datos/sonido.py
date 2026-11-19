"""R4: logica de audio 
    Caracteristicas, linea base y deteccion de anomalias

Grabar la linea base (ambiente normal, con el robot andando):
    ros2 run colmibot_datos grabar_linea_base --segundos 30
    ros2 run colmibot_datos grabar_linea_base --archivo ambiente.wav
"""
import argparse
import json
import os
import wave

import numpy as np

from colmibot_datos.registro import carpeta_datos

FS = 16000
VENTANA_S = 0.5
BANDAS_HZ = [(0, 250), (250, 500), (500, 1000), (1000, 2000),
             (2000, 4000), (4000, 8000)]
NOMBRES = ['volumen'] + [f'banda {lo}-{hi} Hz' for lo, hi in BANDAS_HZ]
PISO_STD_DB = 2.0  # desviacion minima supuesta, para no ser hipersensible


def ruta_linea_base():
    return os.path.join(carpeta_datos(), 'linea_base_audio.json')


def leer_wav(ruta):
    """Devuelve (audio mono float en [-1, 1], frecuencia de muestreo)."""
    with wave.open(ruta, 'rb') as w:
        fs, canales, ancho = w.getframerate(), w.getnchannels(), w.getsampwidth()
        datos = w.readframes(w.getnframes())
    if ancho != 2:
        raise ValueError('Solo se aceptan WAV de 16 bits')
    audio = np.frombuffer(datos, dtype=np.int16).astype(np.float64) / 32768.0
    if canales > 1:
        audio = audio.reshape(-1, canales).mean(axis=1)
    return audio, fs


def caracteristicas(ventana, fs=FS):
    """Vector: [volumen en dBFS, energia en dB de cada banda]."""
    x = np.asarray(ventana, dtype=np.float64)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-12
    espectro = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
    vec = [20 * np.log10(rms)]
    for lo, hi in BANDAS_HZ:
        energia = espectro[(freqs >= lo) & (freqs < hi)].sum() + 1e-12
        vec.append(10 * np.log10(energia / len(x) ** 2))
    return np.array(vec)


def ventanas(audio, fs, ventana_s=VENTANA_S):
    n = int(fs * ventana_s)
    for i in range(0, len(audio) - n + 1, n):
        yield audio[i:i + n]


def calcular_linea_base(audio, fs, ventana_s=VENTANA_S):
    """Media y desviacion de las caracteristicas del ambiente normal."""
    matriz = np.array([caracteristicas(v, fs)
                       for v in ventanas(audio, fs, ventana_s)])
    if len(matriz) < 10:
        raise ValueError('Se necesitan al menos 5 s de audio (10 ventanas)')
    return {
        'fs': int(fs),
        'ventana_s': ventana_s,
        'n_ventanas': int(len(matriz)),
        'media': matriz.mean(axis=0).tolist(),
        'std': np.maximum(matriz.std(axis=0), PISO_STD_DB).tolist(),
    }


def guardar_linea_base(base, ruta=None):
    ruta = ruta or ruta_linea_base()
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(base, f, indent=2)
    return ruta


def cargar_linea_base(ruta=None):
    with open(ruta or ruta_linea_base(), encoding='utf-8') as f:
        return json.load(f)


def puntaje(vec, base):
    """Devuelve (puntaje, indice): cuantas desviaciones se aleja lo peor."""
    z = (np.asarray(vec) - np.array(base['media'])) / np.array(base['std'])
    i = int(np.argmax(np.abs(z)))
    return float(abs(z[i])), i


def describir(vec, base, i, valor):
    sentido = 'mas fuerte' if vec[i] > base['media'][i] else 'mas debil'
    return (f'{NOMBRES[i]} {sentido} de lo normal '
            f'(puntaje {valor:.1f}, volumen {vec[0]:.1f} dBFS)')


def grabar_microfono(segundos, fs=FS, dispositivo=None):
    import sounddevice as sd  # requiere libportaudio2
    audio = sd.rec(int(segundos * fs), samplerate=fs, channels=1,
                   dtype='float32', device=dispositivo)
    sd.wait()
    return audio[:, 0].astype(np.float64)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Graba la linea base de audio')
    parser.add_argument('--segundos', type=float, default=30.0)
    parser.add_argument('--archivo', help='usar un WAV en vez del microfono')
    parser.add_argument('--dispositivo', help='nombre o numero del microfono')
    parser.add_argument('--salida', help='archivo JSON de salida')
    args = parser.parse_args(argv)
    if args.archivo:
        audio, fs = leer_wav(os.path.expanduser(args.archivo))
    else:
        dispositivo = args.dispositivo
        if dispositivo is not None and dispositivo.isdigit():
            dispositivo = int(dispositivo)
        print(f'Grabando {args.segundos:.0f} s de ambiente normal...')
        audio, fs = grabar_microfono(args.segundos, FS, dispositivo), FS
    base = calcular_linea_base(audio, fs)
    ruta = guardar_linea_base(base, args.salida)
    print(f'Linea base guardada en {ruta} ({base["n_ventanas"]} ventanas)')


if __name__ == '__main__':
    main()
