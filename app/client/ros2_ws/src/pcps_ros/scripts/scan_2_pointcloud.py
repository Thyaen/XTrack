#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
import laser_geometry.laser_geometry as lg
import sensor_msgs_py.point_cloud2 as pc2

class LaserScanToPointCloud(Node):
    def __init__(self):
        super().__init__('laser_scan_to_pointcloud')
        
        # Initialize the laser projection object
        self.lp = lg.LaserProjection()
        
        # Subscriber for LaserScan
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/corrected_scan',  # Replace with your LiDAR scan topic
            self.scan_callback,
            10)
        
        # Publisher for PointCloud2
        self.pc_pub = self.create_publisher(
            PointCloud2,
            '/pointcloud',  # Output topic for PointCloud2
            10)

    def scan_callback(self, scan_msg):
        try:
            # Convert LaserScan to PointCloud2
            cloud_out = self.lp.projectLaser(scan_msg)
            
            # Publish the PointCloud2 message
            self.pc_pub.publish(cloud_out)
            
            #self.get_logger().info("Published PointCloud2")
            
        except Exception as e:
            self.get_logger().error(f"Error converting scan to pointcloud: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LaserScanToPointCloud()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
