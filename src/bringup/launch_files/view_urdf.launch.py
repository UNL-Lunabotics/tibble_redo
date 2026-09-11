from launch import LaunchDescription
from launch.substitutions import Command, PathSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    description_pkg = FindPackageShare("description")
    bringup_pkg = FindPackageShare("bringup")

    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("bringup"), "launch_files", "base.launch.py"])
        )
    )

    # For joint manipulation
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description
            },
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", PathSubstitution(bringup_pkg) / "config" / "view_urdf.rviz"],
    )

    return LaunchDescription([
        base,
        joint_state_publisher_gui_node,
        rviz_node,
    ])