#!/usr/bin/env python3
"""
Получить телеметрию дрона в кадре aruco_map.
Использование: python3 telemetry.py <drone-ip>
Пример:       python3 telemetry.py 192.168.1.111
"""

import subprocess
import sys

DRONE_IP = sys.argv[1] if len(sys.argv) > 1 else None

if not DRONE_IP:
    print("Usage: python3 telemetry.py <drone-ip>")
    print("Example: python3 telemetry.py 192.168.1.111")
    sys.exit(1)

PYTHON_SCRIPT = """
import sverk_interfaces
d = sverk_interfaces.init(Nodename='cli_telemetry')
t = d.control.get_telemetry(frame_id='aruco_map', timeout=3.0)
if t is None:
    print('ERROR: no aruco telemetry (markers not visible?)')
else:
    import math
    ok = all(math.isfinite(float(getattr(t, k, float('nan')))) for k in ('x', 'y', 'z'))
    if ok:
        yaw = float(getattr(t, 'yaw', 0.0))
        print(f'x={t.x:.3f}  y={t.y:.3f}  z={t.z:.3f}  yaw={yaw:.3f}')
    else:
        print(f'ERROR: invalid telemetry x={getattr(t,\"x\",\"?\")} y={getattr(t,\"y\",\"?\")} z={getattr(t,\"z\",\"?\")}')
"""

SSH_CMD = "source /opt/ros/humble/setup.bash && source /home/sverk/sverk_ws/install/setup.bash && python3"

print(f"[telemetry] drone={DRONE_IP}")
r = subprocess.run(
    ["sshpass", "-p", "sverk", "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     f"sverk@{DRONE_IP}", "-p", "22", SSH_CMD],
    input=PYTHON_SCRIPT, text=True, capture_output=True, timeout=15
)

print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)