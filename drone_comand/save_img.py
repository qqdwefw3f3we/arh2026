#!/usr/bin/env python3
"""
Сохранить снимок с камеры дрона.
Скачивает фото на локальную машину в drone_comand/img/
Использование: python3 save_img.py <drone-ip> [имя_файла]
Пример:       python3 save_img.py 192.168.1.111 photo.jpg
"""

import subprocess
import sys
import os

DRONE_IP = sys.argv[1] if len(sys.argv) > 1 else None
FILENAME = sys.argv[2] if len(sys.argv) > 2 else "photo.jpg"

if not DRONE_IP:
    print("Usage: python3 save_img.py <drone-ip> [filename]")
    print("Example: python3 save_img.py 192.168.1.111 my_shot.jpg")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DIR = os.path.join(SCRIPT_DIR, "img")
os.makedirs(LOCAL_DIR, exist_ok=True)
LOCAL_PATH = os.path.join(LOCAL_DIR, FILENAME)
REMOTE_PATH = f"/tmp/{FILENAME}"

PYTHON_SCRIPT = f"""
import sverk_interfaces, cv2
d = sverk_interfaces.init(Nodename='cli_photo')
frame = d.image.take_picture(timeout=3.0)
if hasattr(frame, 'encoding'):
    frame = d.image.to_cv2(frame)
cv2.imwrite('{REMOTE_PATH}', frame)
print('OK:{REMOTE_PATH}')
"""

SSH_CMD = "source /opt/ros/humble/setup.bash && source /home/sverk/sverk_ws/install/setup.bash && python3"

print(f"[photo] drone={DRONE_IP} -> {LOCAL_PATH}")

r = subprocess.run(
    ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     f"sverk@{DRONE_IP}", "-p", "22", SSH_CMD],
    input=PYTHON_SCRIPT, text=True, capture_output=True, timeout=30
)
print(r.stdout)

# Скачиваем фото
scp_result = subprocess.run(
    ["scp", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     "-P", "22", f"sverk@{DRONE_IP}:{REMOTE_PATH}", LOCAL_PATH],
    capture_output=True, text=True, timeout=15
)

if scp_result.returncode == 0:
    print(f"SAVED: {LOCAL_PATH}")
else:
    print(f"SCP ERROR: {scp_result.stderr}", file=sys.stderr)
    sys.exit(1)
