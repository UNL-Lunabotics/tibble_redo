from launch import LaunchDescription
from launch.substitutions import Command, PathSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

# TODO: Need to transmit other nodes/topics as they are needed.

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
                " use_mock_hardware:=true",
            ]
        ),
        value_type=str,
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
            {"robot_description": robot_description},
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", PathSubstitution(bringup_pkg) / "config" / "view_urdf.rviz"],
    )
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
                " use_mock_hardware:=true",
            ]
        ),
        value_type=str,
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
            {"robot_description": robot_description},
        ],
    )

    # rerun URL: http://localhost:9090/?url=rerun+http://localhost:9876/proxy
    rerun_node = Node(
        package="bringup",
        executable="rerun_bridge",
        name="rerun_bridge",
        output="screen",
    )

    return LaunchDescription(
        [
            robot_state_pub_node,
            joint_state_publisher_gui_node,
            rerun_node,
        ]
    )
