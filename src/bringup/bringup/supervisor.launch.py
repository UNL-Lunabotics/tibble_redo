from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    config = PathJoinSubstitution(
        [FindPackageShare('supervisor'), 'config', 'supervisor.yaml'])

    return LaunchDescription([
        Node(
            package='tibble_supervisor',
            executable='supervisor_node',
            name='tibble_supervisor',
            parameters=[config],
            output='screen',
        ),
    ])