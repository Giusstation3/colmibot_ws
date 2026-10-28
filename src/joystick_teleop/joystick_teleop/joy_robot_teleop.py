import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoyRobotTeleop(Node):
    """Convierte el joystick (/joy) en comandos de velocidad para el robot diferencial (/cmd_vel)."""

    def __init__(self):
        super().__init__('joy_robot_teleop')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('axis_linear', 1)      # palanca izquierda, arriba/abajo
        self.declare_parameter('axis_angular', 0)     # palanca izquierda, izquierda/derecha
        self.declare_parameter('button_enable', -1)   # -1 = siempre activo
        self.declare_parameter('button_turbo', 10)    # R1
        self.declare_parameter('scale_linear', 0.3)   # m/s, valor inicial a ajustar en Gazebo
        self.declare_parameter('scale_angular', 1.5)  # rad/s, valor inicial a ajustar en Gazebo
        self.declare_parameter('turbo_factor', 1.5)
        self.declare_parameter('deadzone', 0.1)
        topic = self.get_parameter('cmd_vel_topic').value
        self.pub = self.create_publisher(Twist, topic, 10)
        self.create_subscription(Joy, '/joy', self.joy_cb, 10)
        self.get_logger().info(f'Publicando velocidades en {topic}')

    def axis(self, msg, idx):
        if idx < 0 or idx >= len(msg.axes):
            return 0.0
        v = msg.axes[idx]
        return 0.0 if abs(v) < self.get_parameter('deadzone').value else v

    def button(self, msg, idx):
        return 0 <= idx < len(msg.buttons) and msg.buttons[idx] == 1

    def joy_cb(self, msg):
        p = self.get_parameter
        enable = p('button_enable').value
        cmd = Twist()
        if enable < 0 or self.button(msg, enable):
            turbo = self.button(msg, p('button_turbo').value)
            factor = p('turbo_factor').value if turbo else 1.0
            cmd.linear.x = self.axis(msg, p('axis_linear').value) * p('scale_linear').value * factor
            cmd.angular.z = self.axis(msg, p('axis_angular').value) * p('scale_angular').value * factor
        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = JoyRobotTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
