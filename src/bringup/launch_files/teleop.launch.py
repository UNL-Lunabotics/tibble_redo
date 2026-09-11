import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathSubstitution, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    control_pkg = FindPackageShare("control")
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

    joy_params = PathSubstitution(control_pkg) / "config" / "joystick.yaml"
    twist_mux_params = PathSubstitution(control_pkg) / "config" / "twist_mux.yaml"

    # --- Nodes ---
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='game_controller_node',
        parameters=[joy_params]
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[joy_params],
        remappings={('/cmd_vel', '/cmd_vel_joy')},
    )

    twist_mux_node = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params],
            remappings=[('/cmd_vel_out','/cmd_vel')]
        )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            PathSubstitution(control_pkg) / "config" / "tibble_controller.yaml"
        ],
        output="both",
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
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
        # joy_node,
        # teleop_node,
        # twist_mux_node,
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        delay_tibble_controller_spawner,
        # rviz_node,
        # state_manager_node
    ])