from launch import LaunchDescription
from launch.substitutions import Command, PathSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    description_pkg = FindPackageShare("description")
    bringup_pkg = FindPackageShare("bringup")

    robot_description_content = ParameterValue(
        Command(
            [
                "xacro ",
                PathSubstitution(description_pkg) / "urdf" / "tibble.urdf.xacro",
                " use_sim:=false",
                " use_control:=true",
                " use_mock_hardware:=true"
            ]
        ),
        value_type=str
    )
    robot_description = {"robot_description": robot_description_content}

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
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
        robot_state_pub_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])