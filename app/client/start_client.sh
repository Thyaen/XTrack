#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/config.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config-Datei $CONFIG_FILE nicht gefunden!" >&2
  exit 1
fi

HOST_IP=$(jq -r '.HOST_IP' "$CONFIG_FILE")


# --- Einstellungen ---
CONTAINER="ros2_humble_pcps"
SESSION="pcps"
WORKSPACE="/root/ros2_ws"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1) Gamepad-Bridge im Hintergrund starten (Logs unterdrückt)
pushd "${SCRIPT_DIR}/../../motor_control" >/dev/null
  python3 gamepad_bridge.py &>/dev/null &
popd >/dev/null

# 2) Docker-Container bauen & starten
pushd "${SCRIPT_DIR}" >/dev/null
  xhost +local:docker
  export DISPLAY="${DISPLAY:-:0}"
  docker compose up -d --build
popd >/dev/null

# 3) Byobu-Session + Fenster anlegen
docker exec "${CONTAINER}" byobu new-session -d -s "${SESSION}" -n motor \
  "bash -lc 'source /opt/ros/humble/setup.bash; \
             cd ${WORKSPACE}; \
             colcon build --symlink-install; \
             source install/setup.bash; \
             ros2 run pcps_ros motor_control_node.py --ros-args -p ip_address:=${HOST_IP}; \
             exec bash'"

docker exec "${CONTAINER}" byobu new-window -t "${SESSION}" -n slam \
  "bash -lc 'source /opt/ros/humble/setup.bash; \
             cd ${WORKSPACE}; \
             source install/setup.bash; \
             echo \"=== SLAM gestartet (STRG+C beendet nur den Prozess) ===\"; \
             ros2 launch pcps_ros pcps_navigation.launch.py ip_address:=${HOST_IP}; \
             echo \"--- SLAM-Prozess beendet (F3/F4 für Fensterwahl) ---\"; \
             exec bash'"

# 4) Direkt ins SLAM-Fenster attachen
echo "==> Attaching to SLAM (Window 1). Mit F3/F4 zu Motor (Window 0) wechseln."
exec docker exec -it "${CONTAINER}" byobu attach -t "${SESSION}:1"
