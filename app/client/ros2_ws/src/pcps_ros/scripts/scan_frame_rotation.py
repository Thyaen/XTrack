#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math

class LidarNEDtoENUNode(Node):
    def __init__(self):
        super().__init__('scan_frame_rotation')
        self.sub = self.create_subscription(
            LaserScan, '/scan_client', self.lidar_callback, 10)
        self.pub = self.create_publisher(LaserScan, '/scan_rotated', 10)
        self.get_logger().info('Scan Frame Rotation node started')

    def lidar_callback(self, msg):
        # Create new LaserScan message for ENU
        enu_msg = LaserScan()
        enu_msg.header = msg.header
        enu_msg.header.frame_id = msg.header.frame_id

        # Copy unchanged fields
        enu_msg.angle_min = msg.angle_min
        enu_msg.angle_max = msg.angle_max 
        enu_msg.angle_increment = msg.angle_increment
        enu_msg.time_increment = msg.time_increment
        enu_msg.scan_time = msg.scan_time
        enu_msg.range_min = msg.range_min
        enu_msg.range_max = msg.range_max
        enu_msg.ranges = [float('inf')] * len(msg.ranges) #msg.ranges[:]
        enu_msg.intensities = [float('inf')] * len(msg.ranges) #msg.intensities[:]

        # Rotation Angle
        angle_offset = math.pi 

        # Rotate each range measurement
        for i in range(len(msg.ranges)):

            if msg.ranges[i] < msg.range_min or msg.ranges[i] > msg.range_max:
                continue  # Skip invalid range

            index = int(i + round(angle_offset/enu_msg.angle_increment, 1)) #- 3
            
            if index >= len(msg.ranges):
                index = index - len(msg.ranges)
            
            enu_msg.ranges[index] = msg.ranges[i]
            if msg.intensities:
                enu_msg.intensities[index] = msg.intensities[i]

        # Publish transformed message
        self.pub.publish(enu_msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarNEDtoENUNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()