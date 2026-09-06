from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import (
    LaunchConfiguration,
)


def generate_launch_description():

    ip_address = LaunchConfiguration("ip_address", default="192.168.0.121")

    aspn = Node(
        package='aspn_vn100',
        executable='vn100_node',
        output='screen',
    )

    server = Node(
        package='pcps_ros',
        executable='server_imu.py',
        output='screen',
        parameters=[{"ip_address":ip_address}],
    )

    return LaunchDescription([
        aspn,
        server
    ])