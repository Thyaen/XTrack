#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class OdomFrameChanger(Node):
    def __init__(self):
        super().__init__('odom_frame_changer')

        # Create subscriber and publisher
        self.subscriber = self.create_subscription(
            Odometry,
            '/kiss/odometry',
            self.odom_callback,
            10
        )
        self.publisher = self.create_publisher(
            Odometry,
            '/odom_modified',
            10
        )

        self.get_logger().info('Odom Frame Changer Node started')

    def odom_callback(self, msg):
        # Create a new Odometry message by copying the incoming message
        modified_odom = Odometry()
        modified_odom = msg

        # Modify frame IDs
        modified_odom.header.frame_id = 'odom_lidar_rl'
        modified_odom.child_frame_id = 'base_link_rl'

        # Publish the modified message
        self.publisher.publish(modified_odom)

def main(args=None):
    rclpy.init(args=args)
    node = OdomFrameChanger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()