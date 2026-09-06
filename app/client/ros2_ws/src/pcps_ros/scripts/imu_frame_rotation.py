#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import tf_transformations
import math

class ImuRotateZNode(Node):
    def __init__(self):
        super().__init__('imu_rotate_z')
        self.sub = self.create_subscription(
            Imu, '/imu_meas_client', self.imu_callback, 10)
        self.pub = self.create_publisher(Imu, '/imu_meas_rotated', 10)
        self.get_logger().info('IMU Z-axis 90-degree rotation node started')

    def imu_callback(self, msg):
        # Create new IMU message
        rotated_msg = Imu()
        rotated_msg.header = msg.header
        rotated_msg.header.frame_id = msg.header.frame_id

        # Rotation quaternion for 90° around Z-axis (counterclockwise)
        rotation_quat = tf_transformations.quaternion_from_euler(0.0, 0.0, -math.pi/2)

        # Original orientation quaternion
        q_orig = [
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ]

        # Apply rotation to orientation
        q_rotated = tf_transformations.quaternion_multiply(rotation_quat, q_orig)
        rotated_msg.orientation.x = q_rotated[0]
        rotated_msg.orientation.y = q_rotated[1]
        rotated_msg.orientation.z = -q_rotated[2]
        rotated_msg.orientation.w = q_rotated[3]

        # Rotate angular velocity (90° around Z: x->-y, y->x, z->z)
        rotated_msg.angular_velocity.x = msg.angular_velocity.y
        rotated_msg.angular_velocity.y = msg.angular_velocity.x
        rotated_msg.angular_velocity.z = msg.angular_velocity.z

        # Rotate linear acceleration (90° around Z: x->-y, y->x, z->z)
        rotated_msg.linear_acceleration.x = msg.linear_acceleration.y
        rotated_msg.linear_acceleration.y = msg.linear_acceleration.x
        rotated_msg.linear_acceleration.z = msg.linear_acceleration.z

        # Copy covariance matrices
        rotated_msg.orientation_covariance = msg.orientation_covariance
        rotated_msg.angular_velocity_covariance = msg.angular_velocity_covariance
        rotated_msg.linear_acceleration_covariance = msg.linear_acceleration_covariance

        # Publish transformed message
        self.pub.publish(rotated_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuRotateZNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()