#!/usr/bin/env python3
"""
Полёт в точку в aruco_map-кадре (по ArUco-маркерам).
Использование: python3 move.py <drone-ip> <x> <y> [высота_м]
Пример:       python3 move.py 192.168.1.111 2.0 3.0 1.5
"""

import subprocess
import sys

DRONE_IP = sys.argv[1] if len(sys.argv) > 1 else None
X = sys.argv[2] if len(sys.argv) > 2 else None
Y = sys.argv[3] if len(sys.argv) > 3 else None
ALT = sys.argv[4] if len(sys.argv) > 4 else "1.5"

if not all([DRONE_IP, X, Y]):
    print("Usage: python3 move.py <drone-ip> <x> <y> [altitude_m]")
    print("Example: python3 move.py 192.168.1.111 2.0 3.0 1.5")
    sys.exit(1)

PYTHON_SCRIPT = f"""
import sverk_interfaces
d = sverk_interfaces.init(Nodename='cli_move')
d.control.navigate_wait(x={X}, y={Y}, z={ALT}, yaw=0.0, speed=0.5, frame_id='aruco_map', auto_arm=True, timeout=30, tolerance=0.3)
print('MOVE: reached ({X}, {Y}, {ALT}m) in aruco_map')
"""

SSH_CMD = "source /opt/ros/humble/setup.bash && source /home/sverk/sverk_ws/install/setup.bash && python3"

print(f"[move] drone={DRONE_IP} target=({X}, {Y}) alt={ALT}m")
r = subprocess.run(
    ["sshpass", "-p", "sverk", "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     f"sverk@{DRONE_IP}", "-p", "22", SSH_CMD],
    input=PYTHON_SCRIPT, text=True, capture_output=True, timeout=45
)

print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)
