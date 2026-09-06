# Error Guide

## Description
This Error Guide provides a concise overview of the most common issues you may encounter and offers practical steps to resolve them.
Use it as a quick reference to troubleshoot problems efficiently and keep your application running smoothly.  
**Please note that this error guide is primarily designed for [manual startup](docs/manual_start.md)  and may not be fully compatible with the quick-start procedure.**  

## Overview
- [Motor Control](#motor-control)  
- [Docker Container](#docker-container)  
- [LiDAR](#lidar)  
- [RVIZ](#rviz)  

## Motor Control
The initial reversing of the XTrack comes with a very small delay which is normal because of time_sleep.

To do a clean rotation the values for motor1 and motor2 are not as you think. 
For example you might think he needs values "motor1: 0.3, motor2: -0.3" to do a clean rotation to the right.
But he needs "motor1: 0.3, motor2: -0.4" to do a clean rotation to the right.
This is because the power in reverse is only estimated 50% compared to forward.

## Docker Container
If you lack permission to start or build docker containers without sudo, please see [here](https://docs.docker.com/engine/install/linux-postinstall/) for help.

## LiDAR
### the pcps_lidar package does not start on the raspberry pi
In the ros2_humble_pcps_host container, try:
```
ping 192.168.11.2
```
If that doesn't work try setting the eth0 ip address, by typing in the pi terminal (Not inside the container):
```
sudo ifconfig eth0 192.168.11.4
```
Retry pinging the lidar.  
If it still doesn't work, please try disconnecting the lidar from power by disconnecting these cables:  
<img src="docs/img/lidar_power.jpg" alt="LiDAR power connection" width="600"/><br>
Loop this until it works.  

If you can ping the LiDAR but the launch file gives the following error, please try disconnecting and reconnecting the ethernet cable.  

```
[rplidar_node-1] [ERROR] [1751133463.749540965] [rplidar_node]: Error, operation time out. SL_RESULT_OPERATION_TIMEOUT!
[ERROR] [rplidar_node-1]: process has died [pid 165, exit code 255, cmd '/pcps/slam_ws/ros2_ws/install/rplidar_ros/lib/rplidar_ros/rplidar_node --ros-args -r __node:=rplidar_node --params-file /tmp/launch_params_w76zvb59'].
```

### LiDAR stops sending data

If the lidar stops sending data, simply terminate the communication process with Ctrl + C and restart the launch file with the following command:  
```
ros2 launch pcps_lidar pcps_lidar.launch.py
```



## RVIZ
If RVIZ is empty upon starting, it is usually caused by a lack of LiDAR data. Please look up the 'LiDAR stops sending data' chapter of this Error Guide.  
If map is faulty or incorrect, restart the process starting from mapping the surroundings again and saving the map.  
**Do NOT start the autonomous navigation if the map is faulty!**
