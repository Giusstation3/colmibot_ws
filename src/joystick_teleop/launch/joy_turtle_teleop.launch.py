from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),
        Node(package='joy', executable='joy_node', name='joy_node',
             parameters=[{'deadzone': 0.05, 'autorepeat_rate': 20.0}]),
        Node(package='joystick_teleop', executable='joy_turtle_teleop',
             name='joy_turtle_teleop', output='screen',
             parameters=[{'scale_linear': 2.0, 'scale_angular': 2.0}]),
    ])
