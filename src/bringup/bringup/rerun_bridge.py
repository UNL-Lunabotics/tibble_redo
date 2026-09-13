import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
import rerun as rr

# This is vibe coded as heck if someone wants to improve on it please do so
class RerunUrdfBridge(Node):
    def __init__(self):
        super().__init__("rerun_urdf_bridge")

        rr.init("tibble_rerun_bridge")
        server_uri = rr.serve_grpc()
        rr.serve_web_viewer(connect_to=server_uri)

        # Dictionary to track parent-child frame relationships for building the TF tree
        self.frame_parents = {}

        # --- QoS Profiles ---
        # robot_description and tf_static are published latched (transient local)
        transient_local_qos = QoSProfile(
            depth=1,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE,
        )

        # --- Subscriptions ---

        # 1. URDF
        self.create_subscription(
            String, "/robot_description", self.urdf_cb, transient_local_qos
        )

        # 2. TF & TF Static (Published by robot_state_publisher)
        self.create_subscription(
            TFMessage, "/tf_static", self.tf_cb, transient_local_qos
        )
        self.create_subscription(TFMessage, "/tf", self.tf_cb, 100)

        # 3. Odometry (Assuming your ros2_control diff_drive/controller outputs here)
        self.create_subscription(Odometry, "/tibble_controller/odom", self.odom_cb, 10)

        # 4. Joint States (Published by joint_state_broadcaster or joint_state_publisher_gui)
        self.create_subscription(JointState, "/joint_states", self.joint_state_cb, 10)

    def urdf_cb(self, msg: String):
        self.get_logger().info("Received robot_description, logging URDF to Rerun")
        rr.log_file_from_contents(
            file_path="robot.urdf",
            file_contents=msg.data.encode("utf-8"),
            entity_path_prefix="urdf",
            static=True,
        )

    def resolve_tf_path(self, frame_id):
        """Builds the full Rerun entity path by walking up the TF tree."""
        path = [frame_id]
        current = frame_id
        while current in self.frame_parents:
            current = self.frame_parents[current]
            path.insert(0, current)
        return "urdf/" + "/".join(path)

    def tf_cb(self, msg: TFMessage):
        for tf in msg.transforms:
            # Clean up frame IDs (ROS2 sometimes includes leading slashes)
            parent = tf.header.frame_id.lstrip("/")
            child = tf.child_frame_id.lstrip("/")

            # Update our internal tree
            self.frame_parents[child] = parent

            # Log the transform to the specific branch of the URDF tree
            entity_path = self.resolve_tf_path(child)

            rr.log(
                entity_path,
                rr.Transform3D(
                    translation=[
                        tf.transform.translation.x,
                        tf.transform.translation.y,
                        tf.transform.translation.z,
                    ],
                    rotation=rr.Quaternion(
                        xyzw=[
                            tf.transform.rotation.x,
                            tf.transform.rotation.y,
                            tf.transform.rotation.z,
                            tf.transform.rotation.w,
                        ]
                    ),
                ),
            )

    def odom_cb(self, msg: Odometry):
        """Logs the robot's odometry as a 3D point and orientation in the world."""
        pos = msg.pose.pose.position
        rot = msg.pose.pose.orientation

        # Log to a separate 'odometry' space outside the URDF tree
        rr.log(
            "odometry/base_link",
            rr.Transform3D(
                translation=[pos.x, pos.y, pos.z],
                rotation=rr.Quaternion(xyzw=[rot.x, rot.y, rot.z, rot.w]),
            ),
        )

    def joint_state_cb(self, msg: JointState):
        """Logs joint angles as timeseries scalars for debugging control outputs."""
        for name, position in zip(msg.name, msg.position):
            rr.log(f"telemetry/joints/{name}", rr.Scalars(position))


def main():
    rclpy.init()
    node = RerunUrdfBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
