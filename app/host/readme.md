ssh pia@teamA.local

pw: TUBerlin2025+

clone the repository with:
```
https://git.tu-berlin.de/FF/progpra-pcbs-av/a-so2025/pcps.git
```

Upload and initialize the submodules with:
```
cd pcps/
git submodule upload --init
```
check that the rplidar_ros package is not empty:
```
cd app/host/ros2_ws/src/rplidar_ros
ls
```
also ping the lidar:
```
ping 192.168.11.2
```
if there is no response check the error guide

Return to the host folder where the docker compose file is located and execute:
```
sudo docker compose build

sudo docker compose up -d

sudo docker attach ros2_humble_pcps_host
```
you should be in the ros2_ws. Execute byobu and open another terminal (2 in total):
```
colcon build

byobu

FN + F2
```
Source the workspace in both terminals:
```
source install/setup.bash
```
In one terminal execute this command for lidar communication:
```
ros2 launch pcps_ros pcps_lidar.launch.py ip_address:=<client_ip_address>
```
In the otherone execute this for imu communication:
```
ros2 launch pcps_ros pcps_imu.launch.py ip_address:=<client_ip_address>
```






