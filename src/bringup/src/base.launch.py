import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathSubstitution, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterFile

def generate_launch_description():
    # Packages
    control_pkg = FindPackageShare("control")
    bringup_pkg = FindPackageShare("bringup")
    description_pkg = FindPackageShare("description")

    # Launch Arguments
    use_sim = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Whether to use simulation time or real time.'
    )

    use_control = DeclareLaunchArgument(
        'use_control',
        default_value='true',
        description='Whether to use ROS2 Control.'
    )

    use_mock_hardware = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='false',
        description='Whether to use mock hardware or real hardware.'
    )

    # Robot State Publisher
    robot_description_content = Command([
        "xacro",
        " ",
        description_pkg,
        "/urdf/tibble.urdf.xacro",
        " use_sim:=",
        LaunchConfiguration('use_sim'),
        " use_control:=",
        LaunchConfiguration('use_control'),
        " use_mock_hardware:=",
        LaunchConfiguration('use_mock_hardware'),
    ])

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            {"robot_description": robot_description_content, "use_sim_time": True}
        ],
    )
    controllers_config = PathJoinSubstitution([control_pkg, "config", "gamepad.yaml"])
    joy_params = control_pkg / "config" / "joystick.yaml"
    twist_mux_params = control_pkg / "config" / "twist_mux.yaml"

    foxglove_bridge = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
    )
    
    # depth_to_pointcloud = Node(
    #     package='depth_image_proc',
    #     executable='point_cloud_xyz_node',
    #     name='depth_to_pointcloud',
    #     remappings=[
    #         ('image_rect', 'camera/depth_image'),
    #         ('camera_info', 'camera/camera_info'),
    #         ('points', 'camera/points_corrected'),
    #     ],
    #     parameters=[{'use_sim_time': True}],
    # )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_cont",
            '--controller-ros-args',
            '-r /diff_cont/cmd_vel:=/cmd_vel',
             "--param-file", controllers_config
        ],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad", "--param-file", controllers_config],
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='game_controller_node',
        parameters=[joy_params]
    )

    twist_mux_node = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params],
        remappings=[('/cmd_vel_out','/cmd_vel')]
    )

    teleop_node = Node(
        package='teleop_twist_joy', 
        executable='teleop_node',
        name = 'teleop_node',
        parameters=[
            bringup_pkg
            / "config"
            / "joystick.yaml"
        ]
    )

    return LaunchDescription([
        use_sim,
        use_control,
        use_mock_hardware,
        rsp,
        foxglove_bridge,
        # depth_to_pointcloud,
        diff_drive_spawner,
        joint_broad_spawner,
        joy_node,
        twist_mux_node,
        teleop_node,
    ])
