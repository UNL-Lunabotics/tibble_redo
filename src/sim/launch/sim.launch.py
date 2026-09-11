from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_gazebo_arg = DeclareLaunchArgument(
        'use_gazebo',
        default_value='false',
        description='Use Gazebo sim if true. Otherwise default to MuJoCo'
    )
    use_gazebo = LaunchConfiguration('use_gazebo')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='world',
        description='The scene to load in'
    )
    world = LaunchConfiguration('world')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("sim"), "launch", "gazebo.launch.py"])
        ),
        condition=IfCondition(use_gazebo),
        launch_arguments={"world": world}.items(),
    )

    mujoco = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("sim"), "launch", "mujoco.launch.py"])
        ),
        condition=UnlessCondition(use_gazebo),
        launch_arguments={"world": world}.items(),
    )

    return LaunchDescription([
        use_gazebo_arg,
        world_arg,
        gazebo,
        mujoco,
    ])
