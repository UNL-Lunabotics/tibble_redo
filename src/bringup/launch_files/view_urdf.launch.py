from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathSubstitution, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bringup_pkg = FindPackageShare("bringup")
    
    # Robot State Publisher
    robot_description_content = Command([
        "xacro",
        " ",
        PathSubstitution(FindPackageShare("description")),
        "/urdf/tibble.urdf.xacro",
        " use_sim:=true",
        " use_control:=true",
        " use_mock_hardware:=false",
    ])

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            {"robot_description": robot_description_content, "use_sim_time": True}
        ]
    )

    # For joint manipulation
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", PathSubstitution(bringup_pkg) / "config" / "view_urdf.rviz"],
    )

    return LaunchDescription([
        rsp,
        joint_state_publisher_gui_node,
        rviz_node
    ])