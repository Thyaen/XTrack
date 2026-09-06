cmake_minimum_required(VERSION 3.8)
project(pcps_ros)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

install(DIRECTORY launch scripts config maps robot_description
  DESTINATION share/${PROJECT_NAME}/)

install(PROGRAMS scripts/scan_client.py
                 scripts/scan_frame_rotation.py 
                 scripts/scan_imu_rotation.py
                 scripts/scan_2_pointcloud.py 
                 scripts/imu_client.py  
                 scripts/imu_frame_rotation.py 
                 scripts/imu_robot_localization.py 
                 scripts/odom_robot_localization.py
                 scripts/motor_control_node.py 
                 scripts/status_server.py
        DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS launch/pcps_slam.launch.py
                 launch/pcps_navigation.launch.py
        DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
