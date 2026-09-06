# controller_sender.py (Windows)
import socket
import pygame
import time
import json
import platform

ROS_IP = 'localhost'  
ROS_PORT = 6005

is_windows = platform.system() == "Windows"
right_axis_index = 3 if is_windows else 4
triangle_button = 3 if is_windows else 2
square_button = 2 if is_windows else 3

def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ROS_IP, ROS_PORT))
            print("✅ Verbunden mit ROS")
            return sock
        except Exception as e:
            print(f"❌ Verbindung fehlgeschlagen: {e} – neuer Versuch in 3s...")
            time.sleep(3)

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("⚠️ Kein Controller erkannt.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"🎮 Controller erkannt: {joystick.get_name()}")

    sock = connect()

    while True:
        try:
            pygame.event.pump()
            axes = {
                "left": -joystick.get_axis(1),  # Linker Stick Y
                "right": -joystick.get_axis(right_axis_index)  # Rechter Stick Y
            }

            buttons = {
                "triangle": joystick.get_button(triangle_button),
                "square": joystick.get_button(square_button),
                "circle": joystick.get_button(1)
            }

            message = json.dumps({"axes": axes, "buttons": buttons}) + "\n"
            sock.sendall(message.encode())
            time.sleep(0.05)
        except Exception as e:
            print(f"⚠️ Fehler beim Senden: {e}")
            sock.close()
            sock = connect()

if __name__ == "__main__":
    main()
