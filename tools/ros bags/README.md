## ROS 2 Bags
In `ros2_sensor_data` you can find recorded lidar and imu data to test the current or your modified configuration without requiring direct communication to the hardware. In the recorded data the XTrack is positioned in room F322 and after 20 seconds it gets rotated 90° to the right and 180° to the left afterwards. It also gets moved forward and backward after the rotation process is done.

To play the ros bag simply follow these steps:
```
cd tools/ros bags
ros2 bag play ros2_sensor_data
```
Then you should be able to see the `/scan` and `/imu_meas` topics in the topic list.