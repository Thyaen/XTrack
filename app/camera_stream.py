#!/usr/bin/env python3
import socket
import time
import cv2
from picamera2 import Picamera2

HOST = "0.0.0.0"  # IP deines Laptops/Dockers
PORT = 5050

picam2 = Picamera2()
video_config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(video_config)
picam2.start()
time.sleep(2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print(f"🚀 TCP Kamera-Server läuft auf {HOST}:{PORT}, warte auf Verbindung...")

conn, addr = sock.accept()
print(f"✅ Verbindung von {addr}")

try:
    while True:
        frame = picam2.capture_array()
        ret, jpg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        if not ret:
            continue

        conn.sendall(jpg.tobytes())  # Kein Header nötig – Webserver erkennt JPEG-Start/Ende

except KeyboardInterrupt:
    print("⛔️ Abbruch durch Benutzer")
finally:
    conn.close()
    sock.close()
    picam2.stop()
