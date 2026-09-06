#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import socket
import threading
import time
import json
import numpy as np

SERVER_PORT = 6003

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')
        self.ip_address = self.declare_parameter('ip_address', '192.168.0.111').get_parameter_value().string_value
        self.control_mode = "auto"  
        self.get_logger().info(f"Starte mit Modus: {self.control_mode}")

        self.sock = self.connect_to_server()
        threading.Thread(target=self.send_keep_alive, daemon=True).start()

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        threading.Thread(target=self.controller_tcp_listener, daemon=True).start()
        threading.Thread(target=self.gui_tcp_listener, daemon=True).start()
        threading.Thread(target=self.check_auto_reenable, daemon=True).start()

        self.last_manual_input_time = 0
        self.controller_timeout = 3.0

        self.last_gui_input_time = 0
        self.gui_timeout = 3.0

    def connect_to_server(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.ip_address, SERVER_PORT))
                self.get_logger().info("TCP-Verbindung zum Motorserver hergestellt.")
                return sock
            except Exception as e:
                self.get_logger().warn(f"Verbindung fehlgeschlagen: {e}, neuer Versuch in 3s...")
                time.sleep(3)

    def send_keep_alive(self):
        while True:
            try:
                self.sock.sendall(b"ping\n")
                time.sleep(1)
            except:
                self.get_logger().warn("Keep-Alive fehlgeschlagen. Reconnect...")
                self.sock = self.connect_to_server()

    def send_motor_commands(self, left, right):
        left = max(-1.0, min(1.0, left))
        right = max(-1.0, min(1.0, right))
        try:
            self.sock.sendall(f"motor1:{left:.3f}\n".encode())
            self.sock.sendall(f"motor2:{right:.3f}\n".encode())
        except Exception as e:
            self.get_logger().error(f"Senden fehlgeschlagen: {e}")

    def cmd_vel_callback(self, msg):
        if self.control_mode != "auto":
            return

        throttle = msg.linear.x
        steering = msg.angular.z
        
        if throttle == 0.0 and steering > 0: # Reine Drehung nach links
            left = -0.4
            right = 0.28
            self.send_motor_commands(left, right)
        elif throttle == 0.0 and steering < 0: # Reine Drehung nach rechts
            left = 0.28
            right = -0.4
            self.send_motor_commands(left, right)
        elif throttle > 0 and steering == 0.0: # Nach vorne
            left = 0.25
            right = 0.25
            self.send_motor_commands(left, right)
        elif throttle < 0 and steering == 0.0: # Nach hinten
            left = -0.33
            right = -0.33
            self.send_motor_commands(left, right)
        else:
            if throttle > 0: # Vorwärts mit Kurve
                left = throttle - steering # -0.12
                if abs(left) > 0.3:
                    left = 0.26 * np.sign(left)
                elif abs(left) < 0.2:
                    left = 0.26 * np.sign(left)
                right = throttle + steering # 0.48
                if abs(right) > 0.3:
                    right = 0.26 * np.sign(right)
                elif abs(right) < 0.2:
                    right = 0.26 * np.sign(right)
                self.send_motor_commands(left, right)
            else: # Rückwärts mit Kurve
                left = throttle - steering # -0.12
                if abs(left) > 0.4:
                    left = 0.4 * np.sign(left)
                elif abs(left) < 0.2:
                    left = 0.3 * np.sign(left)
                right = throttle + steering # 0.48
                if abs(right) > 0.4:
                    right = 0.4 * np.sign(right)
                elif abs(right) < 0.2:
                    right = 0.3 * np.sign(right)
                self.send_motor_commands(left, right)

    def controller_tcp_listener(self):
        HOST = '0.0.0.0'
        PORT = 6005

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            self.get_logger().info(f"Warte auf Controllerverbindung auf Port {PORT}...")
            conn, addr = s.accept()
            self.get_logger().info(f"Controller verbunden von {addr}")

            buffer = ""
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        self.get_logger().warn("Controller-Verbindung verloren.")
                        break
                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        try:
                            payload = json.loads(line)
                            self.process_controller_data(payload)
                        except json.JSONDecodeError:
                            self.get_logger().warn("Ungültiges JSON vom Controller.")
                except Exception as e:
                    self.get_logger().error(f"Fehler in Controller-Verbindung: {e}")
                    break

    def gui_tcp_listener(self):
        HOST = '127.0.0.1'
        PORT = 6006  

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            self.get_logger().info(f"Warte auf GUI-Verbindung auf Port {PORT}...")
            conn, addr = s.accept()
            self.get_logger().info(f"GUI verbunden von {addr}")

            buffer = ""
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        self.get_logger().warn("GUI-Verbindung verloren.")
                        break
                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        try:
                            payload = json.loads(line)
                            self.process_gui_data(payload)
                        except json.JSONDecodeError:
                            self.get_logger().warn("Ungültiges JSON von GUI.")
                except Exception as e:
                    self.get_logger().error(f"Fehler in GUI-Verbindung: {e}")
                    break

    def process_controller_data(self, payload):
        left = payload["axes"].get("left", 0.0)
        right = payload["axes"].get("right", 0.0)

        if abs(left) < 0.2: left = 0.0
        if abs(right) < 0.2: right = 0.0

        is_moving = abs(left) > 0.0 or abs(right) > 0.0

        if is_moving:
            self.last_manual_input_time = time.time()
            if self.control_mode != "controller":
                self.get_logger().info("Wechsel zu CONTROLLER-Steuerung.")
                self.control_mode = "controller"

        if self.control_mode == "controller":
            self.send_motor_commands(left, right)

    def process_gui_data(self, payload):
        left = payload.get("left", 0.0)
        right = payload.get("right", 0.0)

        if abs(left) < 0.05: left = 0.0
        if abs(right) < 0.05: right = 0.0

        is_moving = abs(left) > 0.0 or abs(right) > 0.0

        if is_moving:
            self.last_gui_input_time = time.time()
            if self.control_mode not in ["controller", "gui"]:
                self.get_logger().info("Wechsel zu GUI-Steuerung.")
                self.control_mode = "gui"

        self.get_logger().debug(f"GUI Input: left={left:.2f}, right={right:.2f}, mode={self.control_mode}")

        if self.control_mode == "gui":
            self.send_motor_commands(left, right)

    def check_auto_reenable(self):
        while True:
            time.sleep(0.5)

            if self.control_mode == "controller":
                if time.time() - self.last_manual_input_time > self.controller_timeout:
                    self.get_logger().info("Controller-Timeout")
                    if time.time() - self.last_gui_input_time <= self.gui_timeout:
                        self.control_mode = "gui"
                        self.get_logger().info("GUI-Steuerung.")
                    else:
                        self.control_mode = "auto"
                        self.get_logger().info("Nav2-Steuerung.")
            elif self.control_mode == "gui":
                if time.time() - self.last_gui_input_time > self.gui_timeout:
                    self.control_mode = "auto"
                    self.get_logger().info("Controller- und GUI-Timeout – zurück zu Nav2.")

def main(args=None):
    rclpy.init(args=args)
    node = MotorControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Beende motor_control_node...")
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
