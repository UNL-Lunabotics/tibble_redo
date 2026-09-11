from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='world',
        description='The world to load in'
    )
    world = [LaunchConfiguration('world'), ".sdf"]

    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("sim"), "launch", "base.launch.py"])
        ),
        launch_arguments={"use_gazebo": "true"}.items(),
    )

    # Locate the config file
    bridge_params = PathJoinSubstitution(
      [FindPackageShare("sim"), "config", "gz_bridge.yaml"]
    )

    gazebo_world = PathJoinSubstitution([FindPackageShare("sim"), "worlds", world])

    # Start environment
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
          [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
        )),
        launch_arguments={"gz_args": ["-r ", gazebo_world]}.items(),
    )

    # Bridge ROS & Gazebo
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gazebo",
        parameters=[
            {"config_file": bridge_params},
            {"publish_rate": 400.0},
            {"qos_overrides./tf_static.publisher.durability": "transient_local"},
        ],
        output="screen",
    )

    # Spawn Robot
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "tootles",
            "-z", "0.5",
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            world_arg,
            base,
            gazebo,
            gz_bridge,
            spawn_entity,
        ]
    )
