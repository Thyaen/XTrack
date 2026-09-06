import socket
import threading
import time
import base64
import logging
import json
from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO
import rclpy
from rclpy.node import Node
import cv2
import struct
import numpy as np
import queue
from ultralytics import YOLO
from torch import cuda
import json
import os

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    cfg = json.load(f)
CAM_IP = cfg.get('HOST_IP', '192.168.0.111')

# --- YOLO + Tracking Pipeline Config ---
TCP_HOST       = '0.0.0.0'
TCP_PORT       = 9999
WEBCAM_WIDTH   = 640
WEBCAM_HEIGHT  = 480
DETECT_EVERY_N = 25       # nur jedes n. Frame neu detektieren
CONF_THRESH    = 0.3     # Mindest-Confidence
DEVICE         = 'cuda' if cuda.is_available() else 'cpu'

# YOLO-8s Modell laden
model = YOLO('yolov8s.pt')
model.to(DEVICE)

# CSRT-Tracker
if hasattr(cv2, 'legacy'):
    Tracker_create      = cv2.legacy.TrackerCSRT_create
    MultiTracker_create = cv2.legacy.MultiTracker_create
else:
    Tracker_create      = cv2.TrackerCSRT_create
    MultiTracker_create = cv2.MultiTracker_create

# Queue für asynchrone Pipeline
raw_queue = queue.Queue(maxsize=1)

app = Flask(__name__, template_folder='templates', static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True, async_mode="threading")

# --- TCP Control-Server ---
SERVER_IP = '127.0.0.1'
SERVER_PORT = 6006
control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
motor_socket = None

def connect_control():
    global motor_socket
    while True:
        try:
            motor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            motor_socket.connect((SERVER_IP, SERVER_PORT))
            print("[INFO] Verbindung zum Motor-Server hergestellt.")
            return
        except Exception as e:
            print(f"[FEHLER] Verbindung fehlgeschlagen: {e}")
            time.sleep(3)

def send_command(command):
    global motor_socket
    try:
        motor_socket.sendall((command + "\n").encode())
    except Exception as e:
        print(f"[FEHLER] Befehl senden fehlgeschlagen: {e}")

@app.route("/motor", methods=["POST"])
def motor_control():
    motor1 = float(request.form.get("motor1", "0.0"))
    motor2 = float(request.form.get("motor2", "0.0"))
    payload = {"left": motor1, "right": motor2}
    send_command(json.dumps(payload))
    return "", 204

# --- Camera Stream-Receiver (Raw Frames) ---
CAM_PORT = 5050

def receive_images_tcp():
    while True:
        try:
            logging.info(f"🔌 Verbinde mit Kamera unter {CAM_IP}:{CAM_PORT} ...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((CAM_IP, CAM_PORT))
            sock.settimeout(5.0)
            logging.info("✅ Verbindung hergestellt.")

            buffer = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    logging.warning("❌ Verbindung geschlossen.")
                    break
                buffer += data

                while True:
                    start = buffer.find(b'\xff\xd8')
                    end = buffer.find(b'\xff\xd9', start)
                    if start != -1 and end != -1 and end > start:
                        jpg = buffer[start:end+2]
                        buffer = buffer[end+2:]
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            img = cv2.resize(img, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
                            try:
                                raw_queue.put(img, block=False)
                            except queue.Full:
                                pass
                        continue
                    break
        except Exception as e:
            logging.error(f"⚠️ Fehler bei TCP-Verbindung: {e}. Versuche erneut in 2s...")
            time.sleep(2)

# --- Detection & Tracking Thread ---
def process_loop():
    frame_idx = 0
    trackers  = None
    labels    = []
    confs     = []
    while True:
        try:
            frame = raw_queue.get(timeout=0.02)
        except queue.Empty:
            continue
        frame_idx += 1
        disp = frame.copy()

        # Detection every N-th frame
        if frame_idx % DETECT_EVERY_N == 0:
            res    = model(frame, device=DEVICE, verbose=False)[0]
            new_tr = MultiTracker_create()
            labels.clear(); confs.clear()
            for box in res.boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESH:
                    continue
                x0, y0, x1, y1 = map(int, box.xyxy[0])
                w, h = x1 - x0, y1 - y0
                tr = Tracker_create()
                new_tr.add(tr, frame, (x0, y0, w, h))
                cls = int(box.cls[0])
                labels.append(res.names[cls])
                confs.append(conf)
                cv2.rectangle(disp, (x0, y0), (x1, y1), (0,255,0), 2)
                cv2.putText(disp, f"{labels[-1]} {confs[-1]:.2f}",
                            (x0, y0-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            trackers = new_tr

        elif trackers is not None:
            ok, boxes = trackers.update(frame)
            if ok:
                for i, b in enumerate(boxes):
                    x, y, w, h = map(int, b)
                    cv2.rectangle(disp, (x, y), (x+w, y+h), (255,0,0), 2)
                    cv2.putText(disp, f"{labels[i]} {confs[i]:.2f}",
                                (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)

        # encode and emit via SocketIO
        ret, buf = cv2.imencode('.jpg', disp)
        if not ret:
            continue
        b64 = base64.b64encode(buf.tobytes()).decode('utf-8')
        socketio.emit('camera_frame', {'frame': b64})
        time.sleep(0.02)

# --- ROS2 Bridge Node ---
class RosBridgeNode(Node):
    def __init__(self):
        super().__init__('flask_frontend_bridge')
        from std_msgs.msg import String
        self.create_subscription(
            String,
            '/sensor_topic',
            self.ros_topic_callback,
            10
        )

    def ros_topic_callback(self, msg):
        raw = msg.data.encode('utf-8')
        try:
            control_sock.sendall(raw)
        except (BrokenPipeError, OSError):
            connect_control()
            control_sock.sendall(raw)

# --- SLAM-Publisher-Thread ---
def slam_publisher(node: RosBridgeNode):
    while rclpy.ok():
        try:
            map_data = kiss_icp.get_map()
        except AttributeError:
            map_data = []
        points = np.array(map_data).tolist()
        socketio.emit('slam_map', {'map': points})
        node.get_logger().debug('Published SLAM map')
        rclpy.spin_once(node, timeout_sec=0.1)

@app.route('/')
def index():
    return render_template('index.html')

# --- Main ---
if __name__ == '__main__':
    threading.Thread(target=connect_control, daemon=True).start()
    threading.Thread(target=receive_images_tcp, daemon=True).start()
    threading.Thread(target=process_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
