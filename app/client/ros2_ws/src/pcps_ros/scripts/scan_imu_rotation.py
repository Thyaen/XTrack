#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
import numpy as np
import math
import tf_transformations


class ScanCorrectorNode(Node):

    def __init__(self):
        super().__init__('lidar_imu_fusion_node')
        
        # Parameters
        self.lidar_topic = self.declare_parameter('lidar_topic', '/scan_rotated').get_parameter_value().string_value
        self.imu_topic = self.declare_parameter('imu_topic', '/imu_meas_rotated').get_parameter_value().string_value
        self.output_topic = self.declare_parameter('output_topic', '/corrected_scan').get_parameter_value().string_value
        
        # Subscribers
        self.lidar_sub = self.create_subscription(
            LaserScan,
            self.lidar_topic,
            self.lidar_callback,
            10)
        self.imu_sub = self.create_subscription(
            Imu,
            self.imu_topic,
            self.imu_callback,
            10)
        
        # Publisher
        self.scan_pub = self.create_publisher(LaserScan, self.output_topic, 10)
        
        # Timer for 10 Hz publishing (period = 0.1 seconds)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # Initialize variables
        self.current_yaw = 0.0
        self.latest_scan = None

    def imu_callback(self, msg):
        """Extract yaw from IMU quaternion orientation."""
        # Convert quaternion to Euler angles (yaw only)
        quaternion = (
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        )
        # Simplified quaternion to yaw (assuming Z-axis is up)
        siny_cosp = 2.0 * (quaternion[3] * quaternion[2] + quaternion[0] * quaternion[1])
        cosy_cosp = 1.0 - 2.0 * (quaternion[1] ** 2 + quaternion[2] ** 2)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def lidar_callback(self, msg):
        """Store the latest LiDAR scan."""
        self.latest_scan = msg

    def timer_callback(self):
        """Process and publish the latest LiDAR scan at 10 Hz."""
        if self.latest_scan is None:
            return  # No scan data yet
        
        # Process the latest scan with the current yaw
        self.process_scan(self.latest_scan)

    def process_scan(self, scan):
        """Rotate LiDAR scan points based on current IMU yaw."""
        # Create a new LaserScan message
        transformed_scan = LaserScan()
        transformed_scan.header = scan.header
        transformed_scan.header.stamp = scan.header.stamp #self.get_clock().now().to_msg()  # Update timestamp
        angle_offset = self.current_yaw #math.pi # 180 / 2  # 90°
        transformed_scan.angle_min = scan.angle_min #+ angle_offset
        transformed_scan.angle_max = scan.angle_max #+ angle_offset
        transformed_scan.angle_increment = scan.angle_increment
        transformed_scan.time_increment = scan.time_increment
        transformed_scan.scan_time = scan.scan_time
        transformed_scan.range_min = scan.range_min
        transformed_scan.range_max = scan.range_max
        transformed_scan.ranges = [float('inf')] * len(scan.ranges)  # Initialize with invalid ranges
        transformed_scan.intensities = [0.0] * len(scan.intensities) if scan.intensities else []

        # Rotate each range measurement
        for i in range(len(scan.ranges)):

            if scan.ranges[i] < scan.range_min or scan.ranges[i] > scan.range_max:
                continue  # Skip invalid ranges

            index = int(i + round(angle_offset/transformed_scan.angle_increment, 1)) 
            
            if index >= len(scan.ranges):
                index = index - len(scan.ranges)
            
            transformed_scan.ranges[index] = scan.ranges[i]
            if scan.intensities:
                transformed_scan.intensities[index] = scan.intensities[i]

        # Publish the transformed scan
        self.scan_pub.publish(transformed_scan)

def main(args=None):
    rclpy.init(args=args)
    node = ScanCorrectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
