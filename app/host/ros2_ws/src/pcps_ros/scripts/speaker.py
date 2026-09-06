#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from action_msgs.msg import GoalStatusArray, GoalStatus
import subprocess
import os
from ament_index_python.packages import get_package_share_directory
from random import randrange

class Speaker(Node):
    def __init__(self):
        super().__init__('speaker_node')
        # Subscribe to the Nav2 action status topic
        self.subscription = self.create_subscription(
            GoalStatusArray,
            '/goal_status_host',
            self.status_callback,
            10
        )
        self.get_logger().info('Monitoring Nav2 goal status...')

    def status_callback(self, msg):
        #print(msg.status_list[-1])
        #for status in msg.status_list:
        #    print(status)
        goal_succeeded_audio_list = ['happythomas', 'gesinereachedgoal', 'goalreachedjasper', 'goalreachedoscar'] 
        if msg.status_list[-1].status == GoalStatus.STATUS_SUCCEEDED:
            random_number = randrange(4)
            try:
                self.audio_speaker(goal_succeeded_audio_list[random_number])
            except:
                self.get_logger().warning('Goal succeeded!')
        elif msg.status_list[-1].status == GoalStatus.STATUS_CANCELED:
            try:
                self.audio_speaker('goal_canceled')
            except:
                self.get_logger().warning('Goal was canceled!')
        elif msg.status_list[-1].status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Goal failed!')
        elif msg.status_list[-1].status == GoalStatus.STATUS_EXECUTING:
            self.get_logger().info('Goal is being executed...')
        elif msg.status_list[-1].status == GoalStatus.STATUS_ACCEPTED:
            self.get_logger().info('Goal has been accepted...')
        else:
            self.get_logger().info(f'Goal status: {msg.status_list.status}')

    def audio_speaker(self, filename):

        pcps_ros_path = get_package_share_directory('pcps_ros')

        file = filename + '.wav'
        file_path = os.path.join(pcps_ros_path, 'audios', file)

        command = [
            "aplay", file_path
        ]

        # Run the espeak command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running espeak: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = Speaker()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()