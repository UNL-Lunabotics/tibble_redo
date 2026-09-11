import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    control_pkg = FindPackageShare("control")
    description_pkg = FindPackageShare("description")
    bringup_pkg = FindPackageShare("bringup")

    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("bringup"), "launch_files", "base.launch.py"])
        )
    )

    tibble_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["tibble_controller", "--controller-manager", "/controller_manager"],
    )

    delay_tibble_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[tibble_controller_spawner],
        )
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", PathSubstitution(bringup_pkg) / "config" / "teleop.rviz"],
        condition=IfCondition(LaunchConfiguration("gui")),
    )

    # state_manager_node = Node(
    #     package='control',
    #     executable='state_manager_node',
    #     name='state_manager_node',
    #     output='screen'
    # )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="false"),
        base,
        control_node,
        joint_state_broadcaster_spawner,
        delay_tibble_controller_spawner,
    ])