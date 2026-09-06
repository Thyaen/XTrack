#!/usr/bin/env python3
import socket
import pickle
import rclpy
from rclpy.node import Node
from action_msgs.msg import GoalStatusArray

# UDP server configuration
SERVER_IP = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 12349
BUFFER_SIZE = 65507  # Max UDP packet size

class StatusPublisher(Node):
    def __init__(self):
        super().__init__('status_publisher')
        self.publisher = self.create_publisher(GoalStatusArray, '/goal_status_host', 10)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((SERVER_IP, SERVER_PORT))
        self.get_logger().info(f'UDP server listening on {SERVER_IP}:{SERVER_PORT}')

        self.receive_messages()

    def receive_messages(self):
        while True:
            try:
                # Receive data
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                # Deserialize the GoalStatus message
                try:
                    msg = pickle.loads(data)
                    if isinstance(msg, GoalStatusArray):
                        self.publisher.publish(msg)
                    else:
                        self.get_logger().error('Received data is not a GoalStatus message')
                except Exception as e:
                    self.get_logger().error(f'Deserialization error: {e}')
            except KeyboardInterrupt:
                self.get_logger().info('Shutting down server')
                break
            except Exception as e:
                self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = StatusPublisher()
    try:
        rclpy.spin_once(node, timeout_sec=0)  # Spin once to initialize, then handle UDP loop
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
