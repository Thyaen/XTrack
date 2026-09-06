#!/usr/bin/env python3
import socket
import pickle
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

# UDP client configuration
SERVER_PORT = 12346
BUFFER_SIZE = 65507  # Max UDP packet size

class ImuSubscriber(Node):
    def __init__(self):
        super().__init__('imu_subscriber')
        self.ip_address = self.declare_parameter('ip_address', '192.168.0.121').get_parameter_value().string_value
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.subscription = self.create_subscription(
            Imu,
            '/imu_meas',  # Topic where LIDAR publishes LaserScan messages
            self.scan_callback,
            10)
        self.get_logger().info('Subscribed to /imu topic')

    def scan_callback(self, msg):
        try:
            # Serialize the LaserScan message
            serialized_msg = pickle.dumps(msg)
            
            # Send over UDP
            self.sock.sendto(serialized_msg, (self.ip_address, SERVER_PORT))
            self.get_logger().info(f'Sent IMU Data')
            
        except Exception as e:
            self.get_logger().error(f'Error sending message: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ImuSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down client')
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()