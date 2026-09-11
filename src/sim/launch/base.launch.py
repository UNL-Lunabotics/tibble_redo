import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathSubstitution, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterFile


def generate_launch_description():
    use_gazebo_arg = DeclareLaunchArgument(
        'use_gazebo',
        default_value='false',
        description='Use Gazebo sim if true. Otherwise default to MuJoCo'
    )

    # Robot State Publisher
    robot_description_content = Command(
        [
            "xacro",
            " ",
            PathSubstitution(FindPackageShare("description")),
            "/urdf/tootles.urdf.xacro",
            " ",
            "use_gazebo:=",
            LaunchConfiguration('use_gazebo')
        ]
    )
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            {"robot_description": robot_description_content, "use_sim_time": True}
        ],
    )
    controllers_config = PathJoinSubstitution([FindPackageShare("bringup"), "config", "controllers.yaml"])

    foxglove_bridge = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
    )
    
    depth_to_pointcloud = Node(
        package='depth_image_proc',
        executable='point_cloud_xyz_node',
        name='depth_to_pointcloud',
        remappings=[
            ('image_rect', 'camera/depth_image'),
            ('camera_info', 'camera/camera_info'),
            ('points', 'camera/points_corrected'),
        ],
        parameters=[{'use_sim_time': True}],
    )

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
        parameters=[{'use_sim_time': True}],
    )

    teleop_node = Node(
        package='teleop_twist_joy', 
        executable='teleop_node',
        name = 'teleop_node',
        parameters=[
            PathSubstitution(FindPackageShare("bringup"))
            / "config"
            / "joystick.yaml"
        ]
    )

    return LaunchDescription(
        [
            use_gazebo_arg,
            rsp,
            foxglove_bridge,
            depth_to_pointcloud,
            diff_drive_spawner,
            joint_broad_spawner,
            joy_node,
            teleop_node,
        ]
    )
