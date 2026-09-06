# Manual Start

## Description
In case the automatic start fails, you may have to manually start it and refer to the [Error Guide](docs/error_guide.md) for help.  
Follow the instructions below step by step to troubleshoot.

### Requirements
**ONLY WORKS ON A LINUX OS.**  
If you do not have a Linux OS installed, please see [here](https://www.google.com/search?client=firefox-b-lm&channel=entpr&q=how+to+install+linux+os).  
Make sure you have Docker installed.

### Installation
Make sure the mounts and hardware are attached correctly before proceeding. For guidance, refer to the [Mount](docs/mounts.md) and [Hardware Guide](docs/hardware.md).  
Currently, the mounts should be installed correctly.

##### Docker Container Setup
Please clone this git repository:
```
git clone https://git.tu-berlin.de/FF/progpra-pcbs-av/a-so2025/pcps.git
```
Also update and clone the submodules with:
```
cd pcps/
git submodule update --init
```
Then navigate into pcps/app/client and do as follows:
```
docker compose build
```
**Note: This step may take a while, depending on your download rate.**

### Configuration
Make sure your device is connected to the WiFi "FF_Launchpad".  
Make sure the joystick controller is charged and connected to your device.  
Make sure your browser is in light mode.
Make sure the hardware is set up correctly, according to the [Hardware Documentation.](docs/hardware.md)
Check the battery charge of the two main batteries and ensure they are charged.  
Look up the ip adress of your device by executing:
```
hostname -I
```
It should look something like this: 192.168.0.121  

### Usage

#### Raspberry PI
Connect to the Raspberry PI by doing:
```
ssh pia@teamA.local
```
Password:
```
TUBerlin2025+
```

To start the transmission of the LiDAR data, please do:
```
cd repository/pcps/
git submodule update --init
```

And then start the docker container:
```
cd app/host/
sudo docker compose build
sudo docker compose up -d
sudo docker attach ros2_humble_pcps_host
```

Once you are connected to the container, execute:
```
colcon build
```
**Note: Any error messages that appear during colcon build can usually be ignored, as long as the build completes successfully.**  

Try to ping the LiDAR Sensor:
```
ping 192.168.11.2
```
If unsuccesfull, refer to [Error Guide](docs/error_guide.md) and follow the instructions in a new terminal, while the container keeps running.  
Once done, test if ping 192.168.11.2 is succesful now. If not, refer to Error Guide again.  

Now open a new Terminal using byobu  
```
byobu
#Press "(FN +) F2" to open a new Terminal
```
**Note: You can switch between windows by pressing "FN + F3" (or just "F3", depending on your keyboard settings)**  

Source the workspace in both terminals:
```
source install/setup.bash #Make sure you execute this command in both byobu Terminals
```
In one terminal, execute this command for lidar communication:
```
ros2 launch pcps_ros pcps_lidar.launch.py ip_address:=<client_ip_address>
```
**Note that you should now see continous logs about the LiDAR Scans being sent. If you get an error message, please refer to the [Error Guide](docs/error_guide.md).** <br>
In the other terminal, execute this for imu communication:
```
ros2 launch pcps_ros pcps_imu.launch.py ip_address:=<client_ip_address>
```
**Note: Make sure you change "<client_ip_address>" to your devices ip address**<br><br>


In a new Terminal, connect to the Raspberry PI again to start the camera stream and execute:  
**Note that byobu may prove useful for running multiple Terminals here as well. For more Information, refer to the [Byobu Documentation.](https://gist.github.com/jshaw/5255721)**
```
cd pcps/GUI
sudo python3 camera_stream.py
```
**Note that Connections erros may occur. For now, they can be ignored.**  

In another new terminal activate the python virtual environment, navigate into the XTrack Hub and then execute the main file with:
```
source venv/bin/activate
cd xtrack-hub-main
python3 main.py

```
**Note: Any Connection Errors can be ignored for now**

#### Client (Your device)
Open a Terminal in the directory of the git repository and do:
```
cd motor_control
python3 gamepad_bridge.py
```
**Note: Connection Errors can be ignored for now, since the connection is only established later on**

To start the GUI, open a new Terminal in the directory of the cloned git repository, and do:  
```
cd app/client
xhost +local:docker  
export DISPLAY=:0
docker compose build
docker compose up -d
```

**To open the web interface, open localhost:5000 on your browser.**  

Attach to the Container by doing:
```
docker attach ros2_humble_pcps
```

Now, start byobu in the container:
```
byobu
```

Now execute:
```
⁠ls # If you see the src folder you are in the correct directory and can proceed with building and using the packages:
colcon build # rplidar_ros stderr output is normal  
source install/setup.bash
ros2 run pcps_ros motor_control_node.py
```
**Note: Any error messages that appear during colcon build can usually be ignored, as long as the build completes successfully.**  

##### Manual Motor Control
<img src="docs/charts/controller_manual.png" alt="Joystick Controller Controls" width="600"/><br>
In order to manually control the vehicle, simply use the joysticks to interrupt the autonomous Navigation.  
The left joystick(L3) steers the left track, while the right joystick(R3) controls the right one.

###### Starting the mapping:

Open a new Window using byobu by pressing "(Fn +) F2" in the Terminal.  
To switch between windows if needed, press "(Fn +) F3".  
In the new Window, execute the following command:
```
source install/setup.bash
ros2 launch pcps_ros pcps_slam.launch.py
```
The launch file starts following processes:
1. **server_scan.py**: Receives Lidar data from PI via UDP connection and publishes it as LaserScan messages via the /scan topic
2. **scan_to_pointcloud.py**: Transforms LaserScan Messages from /scan topic into PointCloud2 messages and publishes them via the /pointcloud topic
3. **odometry.launch.py**: Launch File from the kiss-ICP package that publishes odometry via the /kiss/odometry topic as well as frame transformations (odom_lidar -> base_link) via the \tf topic
4. **online_async_launch.py**: Launch File from the slam_toolbox package that creates and publishes a SLAM map via the /map topic

After successfully launching the nodes you should see a slam map visualized in Rviz2:

<img src="docs/img/slammap_final.png" alt="Example of a SLAM map in Rviz2" width="600"/><br> 

(⚠️): If Rviz2 is empty verify if the lidar communication is still working. See [Error Guide](docs/error_guide.md) for more information.

The created maps can be saved with the slam plugin via Panels -> Add New Panel -> SlamToolboxPlugin. 
Enter the map name and path in the fields next to the `save map` and `serialize map` button like this:  
```
src/pcps_ros/maps/<your_map_name> 
```
**And save them by pressing the two corresponding buttons.** The `save map` option creates a PGM and YAML file for external systems that require the map and the `serialize map` option creates a DATA and POSEGRAPH File for maps that will be used internally with the slam toolbox only. After saving it is recommended to check if the created files are in the maps folder.


###### Starting the Navigation

Start by interrupting the Mapping Process in the terminal by pressing "Ctrl + C".  
Before launching the navigation it is important to verify if the path to the created slam map is correct:
```
cd src/pcps_ros/config
nano slam_localization.yaml 
```
Make sure to adjust the variable  `map_file_name` to match the desired global path of the map.
The navigation launch file can then be launched as follows: 
```
cd ../../..
colcon build
source install/setup.bash
ros2 launch pcps_ros pcps_navigation.launch.py
```
**Note: Any error messages that appear during colcon build can usually be ignored, as long as the build completes successfully.**   
Besides the processes that the slam launch file already executes, the navigation launch file starts the `navigation_launch.py`, which takes the slam map as input and generates command velocities for the XTrack as Twist messages via the /cmd_vel topic.

After launching navigation, your slam map should be loaded with a corresponding cost map and base footprint in Rviz2:

<p align="center">
<img src="docs/img/costmap_final.png" alt="Example of a navigation map in Rviz2" width="600"/><br>
</p>
It is possible to adjust the color of the cost map under the `Color_Scheme` map property.

For optimal usability, we recommend manually arranging the windows so that Rviz2 is positioned on the right side of the screen and the web interface on the left, allowing for seamless side-by-side interaction and visualization:  <br>
<img src="docs/img/gui_screenshot.jpg" alt="Screenshot of graphic user interface" width="600"/><br>


**Restart process starting from "Starting the mapping:" if Map is incorrect or faulty.**
Set a target position with the `2D Goal Pose` plugin in Rviz2. To terminate a navigation command the Navigation Panel from Rviz2 can be used (Panels -> Add New Panel -> Navigation 2 -> Pause) or terminate the ros2 nodes with Ctrl + C in the terminal.

Notes:

(⚠️) if the XTrack doesnt find a path or cant translate the command velocities from nav2 after a certain time it will do a fast rotation around its own axis, so keep this in mind to keep your walls clean and safe.

You can find recorded ros bags to test the configuration without the sensor hardware [here](tools/ros%20bags/).