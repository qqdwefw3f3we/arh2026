#!/usr/bin/env python3
"""
Взлёт дрона в body-кадре (аварийный подскок).
Использование: python3 takeoff.py <drone-ip> [высота_м]
Пример:       python3 takeoff.py 192.168.1.111 1.5
"""

import subprocess
import sys

DRONE_IP = sys.argv[1] if len(sys.argv) > 1 else None
ALT = sys.argv[2] if len(sys.argv) > 2 else "1.5"

if not DRONE_IP:
    print("Usage: python3 takeoff.py <drone-ip> [altitude_m]")
    print("Example: python3 takeoff.py 192.168.1.111 1.5")
    sys.exit(1)

PYTHON_SCRIPT = f"""
import sverk_interfaces
d = sverk_interfaces.init(Nodename='cli_takeoff')
d.control.navigate(x=0.0, y=0.0, z={ALT}, yaw=0.0, speed=0.5, frame_id='body', auto_arm=True)
print('TAKEOFF: armed, climbing to {ALT}m')
"""

SSH_CMD = "source /opt/ros/humble/setup.bash && source /home/sverk/sverk_ws/install/setup.bash && python3"

print(f"[takeoff] drone={DRONE_IP} alt={ALT}m")
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
