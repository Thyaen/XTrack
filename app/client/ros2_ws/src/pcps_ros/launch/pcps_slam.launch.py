from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():

    client_scan = Node(
        package='pcps_ros',
        executable='scan_client.py',
        output='screen',
    )

    client_imu = Node(
        package='pcps_ros',
        executable='imu_client.py',
        output='screen',
    )

    static_tf_odom = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            arguments=[
                '0.0', '0.0', '0.0',  # Translation (x, y, z)
                '0.0', '0.0', '0.0',  # Rotation (roll, pitch, yaw, w) as quaternion
                'odom_lidar', 'odom_lidar_rl'  # Parent frame, child frame
            ]
        )

    scan_rotation = Node(
        package='pcps_ros',
        executable='scan_imu_rotation.py',
        output='screen',
    )

    scan_frame_rotation = Node(
        package='pcps_ros',
        executable='scan_frame_rotation.py',
        output='screen',
    )

    imu_frame_rotation= Node(
        package='pcps_ros',
        executable='imu_frame_rotation.py',
        output='screen',
    )

    imu_rl = Node(
        package='pcps_ros',
        executable='imu_robot_localization.py',
        output='screen',
    )

    odom_rl = Node(
        package='pcps_ros',
        executable='odom_robot_localization.py',
        output='screen',
    )

    scan_to_pointcloud = Node(
        package='pcps_ros',
        executable='scan_2_pointcloud.py',
        output='screen',
    )

    kiss_icp_path = get_package_share_directory('kiss_icp')

    kiss_icp = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(kiss_icp_path, 'launch', 'odometry.launch.py')
            ),
            launch_arguments={
                'topic': '/pointcloud',  # Replace with your desired topic
                'base_frame': 'base_link'       # Replace with your desired base frame
            }.items()
    )

    slam_path = get_package_share_directory('slam_toolbox')
    slam_config_path = os.path.join(get_package_share_directory('pcps_ros'), 'config', 'slam_mapping.yaml')

    slam = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_path, 'launch', 'online_async_launch.py')
            ),
            launch_arguments={
                'slam_params_file': slam_config_path,
                'use_sim_time': 'false',
            }.items()
    )

    pcps_ros_path = get_package_share_directory('pcps_ros')

    xacro_file = os.path.join(pcps_ros_path, 'robot_description', 'xtrack.urdf')

    doc = xacro.process_file(xacro_file, mappings={'use_sim' : 'false'})

    robot_desc = doc.toprettyxml(indent='  ')

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}],
        #remappings=[('/tf','tf_robot'),('/tf_static', 'tf_static_robot')]
    )

    robot_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        output='screen',
        parameters=[os.path.join(pcps_ros_path, 'config', 'ekf_params.yaml')]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        client_scan,
        client_imu,
        imu_rl,
        odom_rl,
        scan_frame_rotation,
        imu_frame_rotation,
        scan_rotation,
        scan_to_pointcloud,
        static_tf_odom,
        kiss_icp,
        robot_localization,
        slam
    ])
