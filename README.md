# colmibot_ws – COLMIBOT

Repositorio del equipo para el Seminario de Titulación (ITAM). Contiene los paquetes de ROS 2 Jazzy (Ubuntu 24.04) desarrollados para el robot móvil diferencial COLMIBOT: control con joystick, representación virtual en RViz y simulación en Gazebo.

**Integrantes:** Juan Pablo Cano Rubio, Giuseppe Valencia Carrillo y Xóchitl Axalli López Chavarría.

## Contenido

1. [Estructura del repositorio](#estructura-del-repositorio)
2. [Actividad 10 – Gemelo digital: COLMIBOT en Gazebo con joystick](#actividad-10--gemelo-digital-colmibot-en-gazebo-con-joystick)
3. [Actividad 9 – Representación virtual del robot en RViz](#actividad-9--representación-virtual-del-robot-en-rviz)

## Estructura del repositorio

    colmibot_ws/
    ├── README.md
    ├── docs/
    │   └── datos_fisicos.csv              # masas, centros de masa e inercias medidos en SolidWorks
    └── src/
        ├── joystick_teleop/               # control con joystick
        │   ├── joystick_teleop/
        │   │   ├── joy_turtle_teleop.py   # control de Turtlesim
        │   │   └── joy_robot_teleop.py    # control del robot (publica /cmd_vel)
        │   ├── launch/
        │   │   ├── joy_turtle_teleop.launch.py
        │   │   └── joy_robot_teleop.launch.py
        │   ├── package.xml
        │   └── setup.py
        └── robot_description/             # modelo del robot
            ├── launch/
            │   ├── display.launch.py      # RViz + sliders de las ruedas
            │   └── gazebo.launch.py       # simulación completa en Gazebo con joystick
            ├── meshes/                    # chasis, ruedas, rueda loca, cámara, IMU y ToF (.stl)
            ├── rviz/
            │   └── display.rviz
            ├── urdf/
            │   └── colmibot.urdf
            ├── package.xml
            └── setup.py

---

## Actividad 10 – Gemelo digital: COLMIBOT en Gazebo con joystick

### Video de demostración

https://drive.google.com/drive/folders/1LXp7g6m840I4MAt03XXF4Ll71zE0mhmG?usp=sharing

### Descripción

Se cargó el modelo del robot (paquete `robot_description` de la actividad anterior) en Gazebo, se le agregó lo necesario para que se comporte como un robot diferencial real (masas, inercias, colisiones, fricción y el plugin de tracción diferencial) y se controla con un joystick comercial mediante ROS 2. Todo el sistema se inicia con un solo archivo launch.

### Distribución del trabajo

| Integrante | Parte |
|---|---|
| Axalli | Nodo `joy_robot_teleop` y su launch: convierte el joystick en comandos de velocidad en `/cmd_vel` |
| JuanPa | Datos físicos medidos en SolidWorks (`docs/datos_fisicos.csv`) y URDF para Gazebo |
| Giuseppe | Integración: `gazebo.launch.py` y puente ROS 2 – Gazebo |

### Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| ROS 2 Jazzy sobre Ubuntu 24.04 | Entorno de trabajo, en máquinas virtuales (VMware y Parallels) |
| Gazebo Sim 8.15 (Harmonic) | Simulador físico |
| `ros_gz_sim` | Abre Gazebo e inserta el robot en el mundo (`create`) |
| `ros_gz_bridge` | Puente que pasa `/cmd_vel` de ROS 2 a Gazebo |
| `robot_state_publisher` | Publica el modelo del robot en `robot_description` |
| `joy` (`joy_node`) | Lee el control de Xbox (probado con Xbox 360 y Xbox Series X) |
| SolidWorks | Obtención de masas, centros de masa e inercias |

Instalación de dependencias:

    sudo apt update
    sudo apt install ros-jazzy-ros-gz ros-jazzy-joy ros-jazzy-robot-state-publisher

### Modificaciones al modelo (`src/robot_description/urdf/colmibot.urdf`)

El URDF de la actividad 9 solo tenía parte visual. Para Gazebo se agregó:

- **Inercia (`<inertial>`) en todos los links:** masa, centro de masa y tensor de inercia reales, medidos en SolidWorks (tabla completa en `docs/datos_fisicos.csv`).

| Link | Masa (kg) |
|---|---|
| `chasis_link` | 1.8204 |
| `rueda_izquierda_link` | 0.0194 |
| `rueda_derecha_link` | 0.0194 |
| `rueda_loca_link` | 0.1238 |
| `camara_link` | 0.3019 |
| `tof_link` | 0.0178 |
| `imu_link` | 0.0030 |
| **Total** | **2.3056** |

- **Colisiones (`<collision>`):** un cilindro por cada rueda motriz (radio 0.030 m, ancho 0.012 m) y dos esferas de radio 0.0135 m para la rueda loca, una adelante y otra atrás (a 0.080 m del centro). Las medidas salen de las mallas STL.
- **Fricción:** ruedas motrices con `mu1 = mu2 = 1.0`; rueda loca con `mu1 = mu2 = 0`, para que deslice sin frenar al robot.
- **Juntas de las ruedas:** tipo `continuous`, con amortiguamiento de 0.01.
- **Plugin `DiffDrive`** (`gz-sim-diff-drive-system`), que convierte `cmd_vel` en el giro de cada rueda:

| Parámetro | Valor |
|---|---|
| `left_joint` / `right_joint` | `rueda_izquierda_joint` / `rueda_derecha_joint` |
| `wheel_separation` | 0.174 m |
| `wheel_radius` | 0.030 m |
| `topic` | `cmd_vel` |
| `odom_topic` / `tf_topic` | `odom` / `/tf` |
| `frame_id` / `child_frame_id` | `odom` / `base_link` |
| `odom_publish_frequency` | 30 Hz |

- **Plugin `JointStatePublisher`** (`gz-sim-joint-state-publisher-system`): publica el ángulo de las ruedas en `joint_states`.
- **Etiqueta `preserveFixedJoint`** en `chasis_to_rueda_loca`, para que Gazebo conserve la rueda loca como link separado y le aplique su fricción.

**Convención de ejes:** en `base_link`, X es el frente del robot, Y la izquierda y Z arriba. El CAD tiene el eje vertical en Y, por eso la junta `base_to_chasis` tiene la rotación `rpy="1.5708 0 -1.5708"`.

**Valores que no salen del CAD (supuestos):** fricción de las ruedas (1.0), amortiguamiento de las juntas (0.01) y radio de las esferas de la rueda loca (0.0135 m, aproximado).

### Arquitectura de comunicación

    Control Xbox → joy_node → /joy → joy_robot_teleop → /cmd_vel → ros_gz_bridge → cmd_vel (Gazebo) → DiffDrive → ruedas

| Componente | Qué hace | Mensaje |
|---|---|---|
| `joy_node` | Lee el control y publica `/joy` | `sensor_msgs/msg/Joy` |
| `joy_robot_teleop` | Se suscribe a `/joy` y publica velocidades en `/cmd_vel` | `geometry_msgs/msg/Twist` |
| `ros_gz_bridge` (`parameter_bridge`) | Traduce `/cmd_vel` de ROS 2 al mensaje de Gazebo, en un solo sentido (ROS 2 → Gazebo) | `gz.msgs.Twist` |
| Plugin `DiffDrive` | Calcula la velocidad de cada rueda a partir de la velocidad lineal y angular | — |
| `robot_state_publisher` | Publica el modelo en `robot_description` | — |
| `ros_gz_sim create` | Inserta el robot `colmibot` en el mundo a 0.5 m de altura, leyendo `robot_description` | — |

El puente se limitó a un solo tópico (`/cmd_vel`), que es lo mínimo necesario para mover el robot.

**Controles del joystick:**

| Entrada | Efecto |
|---|---|
| Palanca izquierda arriba/abajo | Avanzar o retroceder (`linear.x`, máximo 0.3 m/s) |
| Palanca izquierda izquierda/derecha | Girar (`angular.z`, máximo 1.5 rad/s) |
| Botón 10 (RB / R1) | Turbo: multiplica las velocidades por 1.5 |

**Parámetros de `joy_robot_teleop`** (se cambian en `src/joystick_teleop/launch/joy_robot_teleop.launch.py`, sin modificar el código):

| Parámetro | Valor | Significado |
|---|---|---|
| `cmd_vel_topic` | `/cmd_vel` | Tópico donde se publican las velocidades |
| `scale_linear` | 0.3 | Velocidad lineal máxima (m/s) |
| `scale_angular` | 1.5 | Velocidad angular máxima (rad/s) |
| `axis_linear` / `axis_angular` | 1 / 0 | Ejes de la palanca izquierda |
| `button_turbo` / `turbo_factor` | 10 / 1.5 | Botón y factor del turbo |
| `deadzone` | 0.1 | Zona muerta: valores menores se toman como 0 |
| `button_enable` | -1 | -1 = siempre activo; otro número = solo se mueve con ese botón presionado |

### Cómo ejecutarlo

1. Conectar el control a la máquina virtual (en VMware: **VM → Removable Devices → (control) → Connect**) y comprobar que existe con `ls /dev/input/js*`.
2. Compilar y lanzar:

        cd ~/colmibot_ws
        colcon build
        source install/setup.bash
        QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 ros2 launch robot_description gazebo.launch.py

`gazebo.launch.py` inicia: Gazebo con un mundo vacío (`empty.sdf`, en ejecución y con el motor gráfico `ogre`), `robot_state_publisher`, la inserción del robot, el puente de `/cmd_vel` y el launch del joystick. También agrega la carpeta de los paquetes a `GZ_SIM_RESOURCE_PATH` para que Gazebo encuentre las mallas.

Las variables `QT_QPA_PLATFORM=xcb` y `LIBGL_ALWAYS_SOFTWARE=1` son necesarias en la máquina virtual; en una computadora con gráficos normales pueden no hacer falta.

Para cerrar: `Ctrl+C` en la terminal del launch y comprobar que no quedaron procesos con `pgrep -af "gz sim"` (si quedan, `pkill -f "gz sim"`).

**Comprobaciones útiles** (en otra terminal, después de `source install/setup.bash`):

    ros2 node list                    # nodos activos
    ros2 topic echo /joy              # lo que lee el control
    ros2 topic echo /cmd_vel          # velocidades que manda el joystick
    gz topic -e -t /cmd_vel           # lo que llega a Gazebo
    ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1}, angular: {z: 0.0}}"   # mover sin joystick

Para probar solo el joystick, sin Gazebo:

    ros2 launch joystick_teleop joy_robot_teleop.launch.py

### Modificaciones posibles

Después de cualquier cambio hay que volver a compilar (`colcon build`), porque los launch y el URDF se ejecutan desde la carpeta `install`.

| Cambio | Dónde | Efecto |
|---|---|---|
| Velocidad máxima de avance | `scale_linear` en `joy_robot_teleop.launch.py` | El robot avanza más lento o más rápido con la palanca al fondo |
| Velocidad máxima de giro | `scale_angular` en `joy_robot_teleop.launch.py` | El robot gira más lento o más rápido |
| Altura de aparición | `-z` en `gazebo.launch.py` | El robot aparece más alto o más bajo antes de caer al piso |
| Fricción de las ruedas | `mu1` y `mu2` en `colmibot.urdf` | Con menos fricción las ruedas patinan |
| Separación o radio de las ruedas | `wheel_separation` / `wheel_radius` del plugin `DiffDrive` (y las `<collision>` de las ruedas) | Cambia cuánto gira y avanza el robot para el mismo comando |

### Problemas encontrados y soluciones

| Problema | Causa | Solución |
|---|---|---|
| Gazebo se cerraba con `Segmentation fault` | El motor `ogre2` falla con el driver gráfico de la máquina virtual (Mesa/EGL) | Usar `--render-engine ogre` (ya está en el launch) y `QT_QPA_PLATFORM=xcb` |
| `package 'joystick_teleop' not found` | `build/` e `install/` se habían subido al repositorio con rutas de otra computadora | Borrar `build/joystick_teleop` e `install/joystick_teleop` y recompilar; `build/`, `install/` y `log/` ahora están en `.gitignore` |
| `link[base_link] has no <inertial>` / `A model must...` | Gazebo descarta un link raíz sin masa y todo lo que cuelga de él | Agregar inercias reales al chasis y a los demás links |
| La rueda loca frenaba al robot | Las `<collision>` con atributo `name` impedían que se aplicara la fricción 0 | Quitar el atributo `name`; se comprobó con `gz sdf -p` que el SDF resultante trae `mu = 0` |
| `Entity creation successful`, pero el robot no se veía | Procesos `gz server` de ejecuciones anteriores seguían vivos y atendían la creación | Cerrar con `Ctrl+C`, revisar con `pgrep -af "gz sim"` y limpiar con `pkill -f "gz sim"` |
| Gazebo no encontraba las mallas `package://...` | Gazebo no conoce las rutas de los paquetes de ROS 2 | El launch agrega esa ruta a `GZ_SIM_RESOURCE_PATH` |
| Error 404 de `protobuf` al instalar Gazebo | Lista de paquetes desactualizada | `sudo apt update` y volver a instalar |
| `joy_node` arrancaba pero no salían datos en `/joy` ni en `/cmd_vel` | VMware dejó el control conectado a Windows y no a la máquina virtual | **VM → Removable Devices → Microsoft Controller → Connect**; después `joy_node` muestra `Opened joystick` |

### Archivos nuevos o modificados

- `src/robot_description/urdf/colmibot.urdf`: inercias, colisiones, fricción y plugins de Gazebo.
- `src/robot_description/launch/gazebo.launch.py`: abre Gazebo, publica el modelo, inserta el robot, crea el puente de `/cmd_vel` e incluye el launch del joystick.
- `src/joystick_teleop/joystick_teleop/joy_robot_teleop.py`, `src/joystick_teleop/launch/joy_robot_teleop.launch.py` y `src/joystick_teleop/setup.py`: nodo y launch para controlar el robot.
- `docs/datos_fisicos.csv`: masas, centros de masa e inercias.

---

## Actividad 9 – Representación virtual del robot en RViz

Paquete `robot_description`: describe el robot con un archivo URDF y permite visualizarlo en RViz.

### Video de demostración

https://itam2-my.sharepoint.com/:v:/g/personal/giuseppe_valencia_itam_mx/IQA6RDZHgcXLRbB0pzQmZXHjAe6-heASYnYVZENMbeIJN4Q?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=er9nI1

### Procedimiento

1. **Exportar el CAD.** Los archivos del robot están hechos en SolidWorks; los abrimos y convertimos con **eDrawings** (ver "Archivos de CAD y conversión a STL"). A partir del ensamble `CLM-EnsambleColmibot.SLDASM` exportamos un STL por cada elemento que queremos ver: chasis, rueda izquierda, rueda derecha, rueda loca, cámara, IMU y sensores ToF. Cada STL conserva las coordenadas del ensamble, así que cada pieza ya está en su posición correcta respecto al origen.
2. **Crear el paquete** con `ros2 pkg create --build-type ament_python robot_description`, igual que los paquetes de actividades anteriores. Los STL se colocan en `meshes/`.
3. **Escribir el URDF a mano** (`urdf/colmibot.urdf`): cada elemento es un `<link>` con su malla STL y un `<joint>` que lo une al chasis.
4. **Crear un launch** (`display.launch.py`) que abre `joint_state_publisher_gui` y RViz con la configuración guardada.
5. **Publicar el modelo** con `robot_state_publisher` mediante `ros2 run`, pasándole el URDF como parámetro.
6. **Configurar RViz** (Fixed Frame, RobotModel y TF) y guardar la configuración en `rviz/display.rviz`.
7. **Verificar** con `check_urdf` (valida el árbol del URDF) y visualmente en RViz: orientación, frente del robot y giro de las ruedas.

### Herramientas y recursos

| Herramienta | Uso |
|---|---|
| SolidWorks | Programa en el que están hechos los archivos CAD (`.SLDPRT` y `.SLDASM`) |
| eDrawings | Visor de SolidWorks; lo usamos para abrir el ensamble, ocultar piezas y exportar los STL |
| ROS 2 Jazzy | Entorno de trabajo |
| URDF | Formato de descripción del robot |
| `robot_state_publisher` | Publica las transformadas del robot |
| `joint_state_publisher_gui` | Sliders para mover las juntas de las ruedas |
| RViz2 | Visualización del modelo |
| `check_urdf` | Validación del URDF |
| `colcon` | Compilación del workspace |

### Archivos de CAD y conversión a STL

**Archivos originales (SolidWorks).** 5 ensambles (`.SLDASM`, el principal es `CLM-EnsambleColmibot`), 22 piezas (`.SLDPRT`) como `CLM-Base`, `CLM-Body`, `CLM-Plato` y `CLM-Llanta60mmD`, y el `BOM.xlsx`. Algunas piezas (por ejemplo `CLM-RuedaLoca` y `Motorreductor 37D con encoder`) no están como archivo suelto, pero sí dentro del ensamble principal.

**Por qué fue necesario usar STL:**

- ROS 2 y RViz no pueden leer los formatos de SolidWorks (`.SLDPRT` y `.SLDASM`); un URDF solo carga mallas en formatos abiertos como STL.
- Un solo STL del ensamble completo sería una única malla fija; las ruedas necesitan ser links aparte para poder girar con una junta `continuous`.

**Cómo lo hicimos con eDrawings:**

1. Abrimos `CLM-EnsambleColmibot.SLDASM` (en `File > Open` hubo que cambiar el filtro de tipo de archivo a *SOLIDWORKS Files* o *All Files*; con el filtro por defecto no mostraba nada).
2. Abrimos el panel **Components** (abajo a la derecha) para ver el árbol de piezas del ensamble.
3. Con clic derecho sobre una pieza usamos **Hide**, **Hide Others** y **Show All** para dejar visible solo el grupo de piezas que queríamos exportar.
4. Con solo ese grupo visible, fuimos a `File > Save As` y elegimos el tipo **STL**.
5. Repetimos el proceso por cada grupo. Exportar desde el ensamble, y no desde cada `.SLDPRT` por separado, hace que cada STL conserve su posición respecto al origen del ensamble.

### Decisiones de diseño y simplificaciones

- **URDF plano, sin xacro.** Es el formato mínimo necesario para este modelo y evita agregar herramientas que no hemos visto en clase.
- **Un STL por elemento, no por cada pieza del ensamble.** El ensamble tiene muchos componentes pequeños; agrupamos en 7 links los que se ven desde fuera.
- **Chasis simplificado.** Se quitaron las piezas internas, que no se ven y no afectan la visualización.
- **Solo geometría visual.** En esta actividad el URDF solo incluía `<visual>`, porque el objetivo era visualizarlo en RViz. Las inercias y colisiones se agregaron en la actividad 10.
- **Rueda loca, cámara, IMU y ToF como juntas `fixed`.** No necesitan moverse.
- **Ruedas motrices como juntas `continuous`.** Giran sin límite, como las ruedas reales.
- **Marco de referencia.** `base_link` sigue la convención de ROS (X al frente, Z arriba). El eje vertical de SolidWorks es Y, así que la junta `base_to_chasis` aplica `rpy="1.5708 0 -1.5708"` para convertirlo. Los links que cuelgan de `chasis_link` usan las coordenadas del CAD.
- **Ruedas.** La junta de cada rueda está en el centro de la rueda (`x = ±0.087`, `y = 0.0165`, `z = 0`, en coordenadas del CAD) para que gire sobre su propio eje. Como el STL ya viene colocado en el ensamble, el `<visual>` de la rueda lleva el desplazamiento contrario.
- **Colores.** Solo para distinguir las piezas en RViz.

### Cómo ejecutarlo

Requisitos:

    sudo apt install ros-jazzy-joint-state-publisher-gui

Compilar:

    cd ~/colmibot_ws
    colcon build --packages-select robot_description
    source install/setup.bash

Terminal 1, publica el modelo:

    cd ~/colmibot_ws
    source install/setup.bash
    ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat src/robot_description/urdf/colmibot.urdf)"

Terminal 2, abre los sliders y RViz con la configuración guardada:

    cd ~/colmibot_ws
    source install/setup.bash
    LIBGL_ALWAYS_SOFTWARE=1 ros2 launch robot_description display.launch.py

`LIBGL_ALWAYS_SOFTWARE=1` solo es necesario en una máquina virtual donde RViz no dibuja; en una computadora normal basta `ros2 launch robot_description display.launch.py`.

En RViz, el Fixed Frame es `base_link`. Al mover los sliders de `rueda_izquierda_joint` y `rueda_derecha_joint` se comprueba que las ruedas giran sobre su centro.

Para validar el URDF:

    check_urdf src/robot_description/urdf/colmibot.urdf

### Problemas encontrados y soluciones

| Problema | Solución |
|---|---|
| No teníamos SolidWorks al inicio, y los archivos `.SLDPRT` no se pueden leer fuera de SolidWorks | Usamos eDrawings, que abre los archivos de SolidWorks y permite exportar a STL con `File > Save As` |
| `ros2 pkg create` falló porque `src/robot_description/` ya existía con los archivos de SolidWorks | Movimos el CAD a una carpeta fuera de `src/` y creamos el paquete limpio |
| Los primeros STL no traían las coordenadas del ensamble, así que no servían para armar el modelo | Los volvimos a exportar desde el ensamble, con sus coordenadas |
| El eje vertical de SolidWorks es Y y el de ROS es Z | Rotación `rpy="1.5708 0 -1.5708"` en la junta `base_to_chasis` |
| RViz mostraba la ventana 3D completamente negra, aunque el URDF cargaba bien | Era un problema de OpenGL en la máquina virtual; se resolvió lanzando con `LIBGL_ALWAYS_SOFTWARE=1` |
| Con `Fixed Frame = map`, RViz marcaba error porque ese marco no existe | Cambiar el Fixed Frame a `base_link` |
| Los ejes de TF eran tan grandes que tapaban el modelo | Bajar el `Marker Scale` del display TF |
| Las ruedas deben girar sobre su centro, pero los STL vienen con las coordenadas del ensamble | Ver "Ruedas" en Decisiones de diseño |
