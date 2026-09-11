from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterFile

def generate_launch_description():
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='world',
        description='The scene to load in'
    )
    world = [LaunchConfiguration('world'), ".mjcf"]

    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("sim"), "launch", "base.launch.py"])
        )
    )

    mujoco_scene = PathJoinSubstitution([FindPackageShare("sim"), "worlds", world])

    mujoco_robot_description = Node(
        package="mujoco_ros2_control",
        executable="robot_description_to_mjcf.sh",
        output="both",
        arguments=[
            "--add_free_joint",
            "--scene", mujoco_scene,
            "--publish_topic", "/mujoco_robot_description",
        ],
    )

    control_node = Node(
        package="mujoco_ros2_control",
        executable="ros2_control_node",
        output="both",
        parameters=[
            {"use_sim_time": True},
            ParameterFile(PathJoinSubstitution([FindPackageShare("bringup"), "config", "controllers.yaml"])),
            ParameterFile(PathJoinSubstitution([FindPackageShare("sim"), "config", "mujoco_plugins.yaml"])),
        ],
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

    return LaunchDescription(
        [
            world_arg,
            base,
            mujoco_robot_description,
            control_node,
            depth_to_pointcloud,
        ]
    )
