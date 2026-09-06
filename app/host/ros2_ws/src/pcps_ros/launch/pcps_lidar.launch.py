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

    ip_address = LaunchConfiguration("ip_address", default="192.168.0.121")

    rplidar_ros_path = get_package_share_directory('rplidar_ros')

    rplidar = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(rplidar_ros_path, 'launch', 'rplidar_s2e_launch.py')
            ),
            launch_arguments={
                'frame_id': 'base_link',
            }.items()
    )

    server = Node(
        package='pcps_ros',
        executable='server_scan.py',
        output='screen',
        parameters=[{"ip_address":ip_address}],
    )

    server_client = Node(
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
        rplidar,
        server,
        server_client,
        speaker,
    ])
