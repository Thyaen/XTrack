from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
from launch.substitutions import (
    LaunchConfiguration,
)


def generate_launch_description():

    server = Node(
        package='pcps_ros',
        executable='status_client.py',
        output='screen',
    )

    speaker = Node(
        package='pcps_ros',
        executable='speaker.py',
        output='screen',
    )

    return LaunchDescription([
        server,
        speaker
    ])
