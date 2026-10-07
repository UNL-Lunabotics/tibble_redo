import rclpy
from rclpy.node import Node
from rclpy.qos import QoSPresetProfiles

from sensor_msgs.msg import Joy
from geometry_msgs.msg import TwistStamped
from interfaces.msg import TibbleCommand


def _age_seconds(node: Node, stamp_time: rclpy.time.Time) -> float:
    return (node.get_clock().now() - stamp_time).nanoseconds / 1e9


class Supervisor(Node):

    def __init__(self):
        super().__init__('tibble_supervisor')

        # Topic names
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('joy_topic', '/joy')
        self.declare_parameter('command_topic', '/tibble_command')

        # Timing
        self.declare_parameter('publish_rate', 30.0)       # Hz, how often /tibble_command goes out
        self.declare_parameter('cmd_vel_timeout', 0.5)     # s
        self.declare_parameter('joy_timeout', 0.5)         # s

        # Button/axis indices. Defaults are placeholders
        self.declare_parameter('panic_button', 6)
        self.declare_parameter('mode_manual_button', 7)
        self.declare_parameter('mode_autonomy_button', 8)
        self.declare_parameter('la_extend_button', 0)
        self.declare_parameter('la_retract_button', 3)
        self.declare_parameter('latch_toggle_button', 2)
        self.declare_parameter('vibe_toggle_button', 1)
        self.declare_parameter('drum_axis', 5)
        self.declare_parameter('drum_axis_deadzone', 0.05)

        p = self.get_parameter
        self._cmd_vel_topic = p('cmd_vel_topic').value
        self._joy_topic = p('joy_topic').value
        self._command_topic = p('command_topic').value
        self._publish_rate = p('publish_rate').value
        self._cmd_vel_timeout = p('cmd_vel_timeout').value
        self._joy_timeout = p('joy_timeout').value

        self._panic_btn = p('panic_button').value
        self._mode_manual_btn = p('mode_manual_button').value
        self._mode_autonomy_btn = p('mode_autonomy_button').value
        self._la_extend_btn = p('la_extend_button').value
        self._la_retract_btn = p('la_retract_button').value
        self._latch_btn = p('latch_toggle_button').value
        self._vibe_btn = p('vibe_toggle_button').value
        self._drum_axis = p('drum_axis').value
        self._drum_deadzone = p('drum_axis_deadzone').value

        # Level state for the toggles. These are what actually get published; the joy callback
        # only flips them on a RISING edge
        self._latch_state = False
        self._vibe_state = False
        self._prev_buttons = []  # previous /joy .buttons, for edge detection

        self._mode = TibbleCommand.MODE_DISABLED

        # Latest received messages + when we received them to detect stale commands
        self._last_joy: Joy | None = None
        self._last_joy_time = None
        self._last_cmd_vel: TwistStamped | None = None
        self._last_cmd_vel_time = None

        self._joy_sub = self.create_subscription(
            Joy, self._joy_topic, self._joy_callback, QoSPresetProfiles.SENSOR_DATA.value)
        self._cmd_vel_sub = self.create_subscription(
            TwistStamped, self._cmd_vel_topic, self._cmd_vel_callback, 10)
        self._command_pub = self.create_publisher(TibbleCommand, self._command_topic, 10)

        period = 1.0 / self._publish_rate
        self._timer = self.create_timer(period, self._command_loop)

        self.get_logger().info(
            f'tibble_supervisor up. Publishing {self._command_topic} at {self._publish_rate} Hz. '
            f'Starting in MODE_DISABLED -- press mode_manual_button or mode_autonomy_button to '
            f'engage.')

    def _joy_callback(self, msg: Joy):
        buttons = msg.buttons

        def pressed(index):
            return 0 <= index < len(buttons) and buttons[index] == 1

        # Rising edge just means if you press and release, it changes on the release.
        # Prevents mode switching if you just hold the button down
        def rising_edge(index):
            was = 0 <= index < len(self._prev_buttons) and self._prev_buttons[index] == 1
            return pressed(index) and not was

        # Mode switches
        if pressed(self._mode_manual_btn):
            if self._mode != TibbleCommand.MODE_MANUAL:
                self.get_logger().info('Mode -> MANUAL')
            self._mode = TibbleCommand.MODE_MANUAL
        elif pressed(self._mode_autonomy_btn):
            if self._mode != TibbleCommand.MODE_AUTONOMY:
                self.get_logger().info('Mode -> AUTONOMY')
            self._mode = TibbleCommand.MODE_AUTONOMY

        if rising_edge(self._latch_btn):
            self._latch_state = not self._latch_state
            self.get_logger().info(f'Latch -> {self._latch_state}')
        if rising_edge(self._vibe_btn):
            self._vibe_state = not self._vibe_state
            self.get_logger().info(f'Vibe -> {self._vibe_state}')

        self._prev_buttons = list(buttons)
        self._last_joy = msg
        self._last_joy_time = self.get_clock().now()

    def _cmd_vel_callback(self, msg: TwistStamped):
        self._last_cmd_vel = msg
        self._last_cmd_vel_time = self.get_clock().now()

    def _command_loop(self):
        out = TibbleCommand()
        out.header.stamp = self.get_clock().now().to_msg()
        out.mode = self._mode

        if self._last_cmd_vel is not None and \
                _age_seconds(self, self._last_cmd_vel_time) <= self._cmd_vel_timeout:
            out.linear_x = self._last_cmd_vel.twist.linear.x
            out.angular_z = self._last_cmd_vel.twist.angular.z
        else:
            out.linear_x = 0.0
            out.angular_z = 0.0
            if self._last_cmd_vel is not None:  # only warn once we've seen at least one message
                self.get_logger().warn(
                    f'{self._cmd_vel_topic} is stale; commanding zero drive.',
                    throttle_duration_sec=1.0)

        is_joy_fresh = self._last_joy is not None and \
            _age_seconds(self, self._last_joy_time) <= self._joy_timeout

        if is_joy_fresh:
            buttons = self._last_joy.buttons
            axes = self._last_joy.axes

            out.panic = 0 <= self._panic_btn < len(buttons) and buttons[self._panic_btn] == 1

            la_extend = 0 <= self._la_extend_btn < len(buttons) and buttons[self._la_extend_btn] == 1
            la_retract = 0 <= self._la_retract_btn < len(buttons) and buttons[self._la_retract_btn] == 1
            if la_extend and not la_retract:
                out.la_cmd = 1.0
            elif la_retract and not la_extend:
                out.la_cmd = -1.0
            else:
                out.la_cmd = 0.0  # both or neither pressed -> stop, never guess a direction

            drum_axis_val = 0.0
            if 0 <= self._drum_axis < len(axes):
                drum_axis_val = axes[self._drum_axis]
            if abs(drum_axis_val) < self._drum_deadzone:
                drum_axis_val = 0.0
            out.drum_cmd = drum_axis_val

            out.latch = self._latch_state
            out.vibe = self._vibe_state
        else:
            # Stale joystick, zero everything but keep latch/vibe states in their last ones
            out.panic = False
            out.la_cmd = 0.0
            out.drum_cmd = 0.0
            out.latch = self._latch_state
            out.vibe = self._vibe_state
            if self._last_joy is not None:
                self.get_logger().warn(
                    f'{self._joy_topic} is stale, zeroing output.',
                    throttle_duration_sec=1.0)

        # TODO: who knows at this point
        if out.mode == TibbleCommand.MODE_AUTONOMY:
            out.drum_cmd = 0.0
            out.la_cmd = 0.0

        self._command_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = Supervisor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()