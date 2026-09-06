# Open TODOs


## fix odometry when integrating IMU

When integrating the IMU by rotating the LiDAR scan, the LiDAR odometry which kiss-icp will put out is also fixed in one direction.  
A possible solution to this problem could be integrating an extended kalman filter to combine the LiDAR odometrys localization with the rotation of the IMU.  

## motor control over the GUI

Currently the motor_control_node does not accept inputs from the GUI.  
When this is fixed, theres also another prioritization to be implemented in the motor_control_node.  
Right now the priority only works between the controller and Nav2 with the controller having the highest priority.
