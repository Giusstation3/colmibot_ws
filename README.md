# Colmibot – Representación virtual del robot en RViz (ROS 2 Jazzy)

Este repositorio contiene el paquete `robot_description`, que describe el robot móvil Colmibot con un archivo URDF y permite visualizarlo en RViz.

## 1. Video de demostración

https://itam2-my.sharepoint.com/:v:/g/personal/giuseppe_valencia_itam_mx/IQA6RDZHgcXLRbB0pzQmZXHjAe6-heASYnYVZENMbeIJN4Q?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=er9nI1

## 2. Procedimiento

1. **Exportar el CAD.** Los archivos del robot están hechos en SolidWorks, pero nosotros los abrimos y convertimos con **eDrawings** (ver sección 3.1). A partir del ensamble `CLM-EnsambleColmibot.SLDASM` exportamos una pieza STL por cada elemento del robot que queremos ver: chasis, rueda izquierda, rueda derecha, rueda loca, cámara, IMU y sensores ToF. Cada STL se guardó con las coordenadas del ensamble, de modo que cada pieza ya está en su posición correcta respecto al origen.
2. **Crear el paquete** con `ros2 pkg create --build-iption`, igual que los paquetes de actividadesanteriores. Los STL se colocan en `meshes/`.
3. **Escribir el URDF a mano** (`urdf/colmibot.urdf`)`<joint>` que la une al chasis. Los datos de posiciónsalen de las dimensiones de los STL, medidas en metros.
4. **Crear un launch** que abre `joint_state_publisheración guardada.
5. **Publicar el modelo** con `robot_state_publisher` mediante `ros2 run`, pasándole el URDF como parámetro.
6. **Configurar RViz** (Fixed Frame, RobotModel y TF)n `rviz/display.rviz`.
7. **Verificar** con `check_urdf` (valida el árbol del URDF) y visualmente en RViz: orientación, frente del robot y giro de las ruedas.

## 3. Herramientas y recursos

| Herramienta | Uso |
|---|---|
| SolidWorks | Programa en el que están hechos los archivos CAD (`.SLDPRT` y `.SLDASM`). No lo usamos para exportar |
| eDrawings | Visor de SolidWorks. Lo usamos para abrir el ensamble, ocultar piezas y exportar los STL |
| ROS 2 Jazzy | Entorno de trabajo |
| URDF | Formato de descripción del robot |
| `robot_state_publisher` | Publica las transformadas
| `joint_state_publisher_gui` | Sliders para mover las juntas de las ruedas |
| RViz2 | Visualización del modelo |
| `check_urdf` | Validación del URDF |
| `colcon` | Compilación del workspace |

## 3.1 Archivos de CAD, conversión a STL y por qué

**Archivos originales (SolidWorks, carpeta `OneDrive_1_10-21-2026`).** 5 ensambles (`.SLDASM`, el principal es `CLM-EnsambleColmibot`), 22 piezas (`.SLDPRT`) como `CLM-Base`, `CLM-Body`, `CLM-Plato` y `CLM-Llanta60mmD`, y el `BOM.xlsx`. Algunas piezas (por ejemplo `CLM-RuedaLoca` y `Motorreductor 37D con encoder`) no están como archivo suelto, pero sí dentro del ensamble principal.

**Archivos que convertimos a STL.**

- Ensamble completo: `CLM-EnsambleColmibot.stl`.
- Piezas sueltas: `CLM-Base.stl`, `CLM-Body.stl`, `CLM-Plato.stl`, `CLM-PisoCam.stl`, `CLM-BaseCam.stl`, `CLM-LogitechC920Montaj.stl`, `CLM-Holder3TOF.stl`.
- Grupos de piezas, uno por cada link del URDF: `chasis.stl` (con todos los componentes), `mini_chasis.stl` (versión simplificada del chasis), `rueda_izquierda.stl`, `rueda_derecha.stl`, `rueda_loca.stl`, `camara.stl`, `tof.stl` e `imu.stl`.

**Por qué fue necesario usar STL.**

- ROS 2 y RViz no pueden leer los formatos de SolidWorks (`.SLDPRT` y `.SLDASM`). Un URDF solo puede cargar mallas en formatos abiertos como STL.
- Un solo STL del ensamble completo sería una única malla fija. Las ruedas necesitan ser links aparte para poder girar con una junta `continuous`.

**Cómo lo hicimos (con eDrawings).**

1. Abrimos `CLM-EnsambleColmibot.SLDASM` en eDrawings (en `File > Open` hubo que cambiar el filtro de tipo de archivo a *SOLIDWORKS Files* o *All Files*; con el filtro por defecto no mostraba nada).
2. Abrimos el panel **Components** (abajo a la derecha) para ver el árbol de piezas del ensamble.
3. Con clic derecho sobre una pieza usamos **Hide**, **Hide Others** y **Show All** para dejar visible solo el grupo de piezas que queríamos exportar (por ejemplo, una rueda, o el chasis sin el interior).
4. Con solo ese grupo visible, fuimos a `File > Save As` y elegimos el tipo **STL**.
5. Repetimos el proceso por cada grupo. Exportar desde el ensamble, y no desde cada `.SLDPRT` abierto por separado, hace que cada STL conserve su posición respecto al origen del ensamble.

## 4. Decisiones de diseño y simplificaciones

- **URDF plano, sin xacro.** Es el formato mínimo quete para este modelo. Evitamos agregar herramientas que no hemos visto en clase.
- **Un STL por elemento, no por cada pieza del ensambomponentes pequeños; agrupamos en 7 links los que seven desde fuera.
- **Chasis simplificado.** Quitamos las piezas internas (que no se ven y no afectan la visualización). El original se conserva fuera del paquete, en `cad/`.
- **Solo geometría visual.** El URDF solo incluye `<visual>`: no tiene inercias ni colisiones, porque el objetivo del proyecto es
visualizarlo en RViz. Si más adelante se usa un simul
- **Rueda loca, cámara, IMU y ToF como juntas `fixed`.** No necesitan moverse para la visualización.
- **Ruedas motrices como juntas `continuous`.** Giranales.
- **Marco de referencia.** `base_link` es el marco del robot con la convención de ROS (X al frente, Z arriba). El eje vertical de
SolidWorks es Y, así que la junta `base_to_chasis` ap8 0 -1.5708"` para convertirlo. Los links que cuelgande `chasis_link` usan las coordenadas del CAD.
- **Ruedas.** La junta de cada rueda está en el centr`y = 0.0165`, `z = 0`, en coordenadas del CAD) paraque gire sobre su propio eje. Como el STL ya viene colocado en el ensamble, el `<visual>` de la rueda lleva el desplazamiento contrario.
- **Colores.** Solo para distinguir las piezas en RVi

## 5. Estructura del paquete

```
src/robot_description/
├── launch/
│   └── display.launch.py     # joint_state_publisher_gui + RViz con configuración
├── meshes/
│   ├── chasis.stl
│   ├── rueda_izquierda.stl
│   ├── rueda_derecha.stl
│   ├── rueda_loca.stl
│   ├── camara.stl
│   ├── imu.stl
│   └── tof.stl
├── rviz/
│   └── display.rviz          # configuración guardada de RViz
├── urdf/
│   └── colmibot.urdf         # descripción del robot
├── resource/robot_description
├── robot_description/__init__.py
├── test/
├── package.xml
├── setup.py
└── setup.cfg
```

Fuera del paquete, `cad/` guarda el `BOM.xlsx` y el Sis_big.stl`), que no se instalan.

## 6. Cómo ejecutarlo

Requisitos (ROS 2 Jazzy):

```bash
sudo apt install ros-jazzy-joint-state-publisher-gui
```

Compilar:

```bash
cd ~/colmibot_ws
colcon build --packages-select robot_description
source install/setup.bash
```

Terminal 1, publica el modelo:

```bash
cd ~/colmibot_ws
source install/setup.bash
ros2 run robot_state_publisher robot_state_publisher on:="$(cat src/robot_description/urdf/colmibot.urdf)"
```

Terminal 2, abre los sliders y RViz con la configuración guardada:

```bash
cd ~/colmibot_ws
source install/setup.bash
LIBGL_ALWAYS_SOFTWARE=1 ros2 launch robot_description
```

`LIBGL_ALWAYS_SOFTWARE=1` solo es necesario en una máquina virtual donde RViz no dibuja (ver problemas). En una computadora normal basta
`ros2 launch robot_description display.launch.py`.

En RViz, el Fixed Frame es `base_link`. Mueve los slit` y `rueda_derecha_joint` para comprobar que lasruedas giran sobre su centro.

Para validar el URDF:

```bash
check_urdf src/robot_description/urdf/colmibot.urdf
```

## 7. Problemas encontrados y soluciones

| Problema | Solución |
|---|---|
| No teníamos SolidWorks al inicio, y los archivos `.SLDPRT` no se pueden leer fuera de SolidWorks. | Usamos eDrawings, que sí abre los archivos de SolidWorks y permite exportar a STL con `File > Save As`. |
| `ros2 pkg create` falló porque `src/robot_description/` ya existía con los archivos de SolidWorks. | Movimos el CAD a una carpeta
`cad/` fuera de `src/` y creamos el paquete limpio. |
| Los primeros STL no traían coordenadas del ensamble, así que no servían para armar el modelo. | Volvimos a exportarlos con las
coordenadas del ensamble. |
| El eje vertical de SolidWorks es Y y el de ROS es Z. | Rotación `rpy="1.5708 0 -1.5708"` en la junta `base_to_chasis`. |
| RViz mostraba la ventana 3D completamente negra, si el URDF cargaba bien (los displays estaban en verde y las TF se publicaban). | Era un problema de OpenGL en la máquina virtual. Se resolvió lanzando con `LIBGL_ALWAYS_SOFTWARE=1`. |
| Con `Fixed Frame = map`, RViz marcaba error porque r el Fixed Frame a `base_link`. |
| Los ejes de TF eran tan grandes que tapaban el modelo. | Bajar el `Marker Scale` del display TF. |
| Las ruedas deben girar sobre su centro, pero el STLs del ensamble. | Detalle en la sección 4, "Ruedas". |
