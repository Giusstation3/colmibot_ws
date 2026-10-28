import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robot_description')
    urdf_path = os.path.join(pkg_share, 'urdf', 'colmibot.urdf')
    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    # Para que Gazebo encuentre package://robot_description/meshes/...
    resource_path = os.path.dirname(pkg_share)
    previo = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    gz_resource_path = resource_path + (os.pathsep + previo if previo else '')

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r empty.sdf',
            description='Argumentos de gz sim (mundo, motor de render, etc.)'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path),

        # 1. Gazebo con el mundo vacio
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': LaunchConfiguration('gz_args')}.items()),

        # 2. Publica el modelo y los TF
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description,
                          'use_sim_time': True}],
             output='screen'),

        # 3. Mete el robot en Gazebo
        Node(package='ros_gz_sim', executable='create',
             arguments=['-topic', 'robot_description', '-name', 'colmibot', '-z', '0.03'],
             output='screen'),

        # 4. Puente ROS 2 <-> Gazebo
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             arguments=[
                 '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                 '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                 '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                 '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                 '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
             ],
             output='screen'),

        # 5. Joystick -> /cmd_vel (paquete joystick_teleop de la Act8)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('joystick_teleop'),
                'launch', 'joy_robot_teleop.launch.py'))),
    ])
