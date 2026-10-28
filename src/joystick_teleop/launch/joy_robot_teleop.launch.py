from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='joy', executable='joy_node', name='joy_node',
             parameters=[{'deadzone': 0.05, 'autorepeat_rate': 20.0}]),
        Node(package='joystick_teleop', executable='joy_robot_teleop',
             name='joy_robot_teleop', output='screen',
             parameters=[{'cmd_vel_topic': '/cmd_vel',
                          'scale_linear': 0.3,
                          'scale_angular': 1.5}]),
    ])
