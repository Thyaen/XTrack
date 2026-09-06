#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuRotateZNode(Node):
    def __init__(self):
        super().__init__('imu_robot_localization')
        self.sub = self.create_subscription(
            Imu, '/imu_meas_rotated', self.imu_callback, 10)
        self.pub = self.create_publisher(Imu, '/imu_rl', 10)
        #self.get_logger().info('IMU Z-axis 90-degree rotation node started')

    def imu_callback(self, msg_input):
        # Create new IMU message
        msg = Imu()
        msg = msg_input
        msg.header.frame_id = 'base_link_rl'

        # Publish transformed message
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuRotateZNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()