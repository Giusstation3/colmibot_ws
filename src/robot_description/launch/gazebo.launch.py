import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_share = get_package_share_directory('robot_description')
    urdf_file = os.path.join(pkg_share, 'urdf', 'colmibot.urdf')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    return LaunchDescription([
        # Para que Gazebo encuentre las mallas package://robot_description/...
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg_share)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': 'empty.sdf -r --render-engine ogre'}.items()
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description',
                       '-name', 'colmibot',
                       '-z', '0.5'],
            output='screen'
        ),
        # Puente: /cmd_vel de ROS (joystick) -> cmd_vel de Gazebo (ruedas)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
            output='screen'
        ),
        # Joystick -> /cmd_vel
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('joystick_teleop'),
                             'launch', 'joy_robot_teleop.launch.py'))
        ),
    ])
