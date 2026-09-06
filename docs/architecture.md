# System Architecture

## Description
The system architecture consists of 4 Docker containers, the XTrack Hub Git repository and an interface to read camera data to guarantee the communication between Raspberry Pi and client. The communication methods consist of UDP and ROS Topics mainly for sensor data and ROS Nodes communication and TCP to control the XTrack.

## Overviews
- [Description](#description)
- [Components](#components)
- [ROS 2 Nodes](#ros2-nodes)

## Components
<img src="docs/charts/system_architecture.svg" alt="System Architecture" width="600"/><br>

**Docker IMU**: Contains aspn_v100 package to read the raw imu data and convert it to ROS 2 format.

**Docker LiDAR**: Contains rplidar_ros package to read the raw lidar data and a node to send the data via UDP Connection to the client.

**Xtrack Hub**: Contains scripts for ESC Handling to control the XTrack

**Read Camera Data**: Node interface to read the camera data and send it via TCP connection to the GUI

**Docker ROS**: Contains ROS 2 workspace for SLAM and Navigation. A detailed description of the worflow inside the container can be found in the [ROS 2 architecture section](#ros-2-architecture-without-imu)

**Docker GUI**: Contains GUI to visualize camera data

## ROS2

#### ROS 2 Architecture without IMU
<img src="docs/charts/ros2_arch_without_imu.png" alt="ROS 2 Architecture without IMU" width="600"/><br>

**rplidar_ros**: Takes the raw Lidar data from the S2e Lidar and converts it into a LaserScan message for ROS compatibility and publishes it via the /scan topic.

**scan_to_pointcloud**: Listens to the /scan topic to convert the Lidar data from LaserScan to a PointCloud2 message. It publishes the new point cloud via the /pointcloud topic. This step is necessary because the kiss-ICP Package is only compatible with PointCloud2 Messages.

**kiss-ICP**: Listens to the /pointcloud topic and creates odometry data which gets published in the /kiss/odometry topic but also frame transformations (odom_lidar -> base_link) as TFMessage via the /tf topic. 

**slam_toolbox**: Listens to the /scan topic and /tf topic to create und update the SLAM map. This Map gets then published via the /map topic.

**Rviz2**: GUI interface to visualize the SLAM map and several other components like lidar data. It is also used to publish 2d goal poses via the /goal_pose topic.

**nav2_bringup**: Navigation package that gets the SLAM map via the /map topic and goal poses via the /goal_pose topic to create costmaps and goal paths. It publishes the needed velocities to acomplish the goal as Twist Messages.

**motor_control_node**: Listens to the /cmd_vel topic from the nav2_bringup package and transforms it into usable motor commands [1,-1] for the left and right chain of the XTrack. It also contains fail safe methods if the connection to the controllers fail.

#### ROS 2 Architecture with IMU
In the current state of the project the only source for odometry calculations is the lidar, however it is planned to implement the IMU into the architecture structure to rotate the lidar data when the XTrack rotates to avoid calculation problems in the SLAM algorithm but also to improve the XTrack's odometry. The ROS 2 Architecture can be extended with the IMU as follows:

<img src="docs/charts/ros2_arch_with_imu.png" alt="ROS 2 Architecture with IMU" width="600"/><br>

**aspn_v100**: Takes the raw IMU data from the VN-100 and converts it into an IMU message for ROS compatibility and publishes it via the /imu_meas topic.

**transform_scan**: Listens to the /imu_meas and /scan topic to rotate the lidar data with the yaw angle determined from the imu data and publishes the rotated lidar data via the /corrected_scan topic.

**robot_localization**: Merges lidar odometry and imu data to calculate a combined odometry being published via the /tf topic. The odometry data is being published from the kiss-ICP package via the /kiss/odometry topic and the imu data via the /imu_meas topic. 

