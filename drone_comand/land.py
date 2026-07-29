#!/usr/bin/env python3
"""
Посадка дрона.
Использование: python3 land.py <drone-ip>
Пример:       python3 land.py 192.168.1.111
"""

import subprocess
import sys

DRONE_IP = sys.argv[1] if len(sys.argv) > 1 else None

if not DRONE_IP:
    print("Usage: python3 land.py <drone-ip>")
    print("Example: python3 land.py 192.168.1.111")
    sys.exit(1)

PYTHON_SCRIPT = """
import sverk_interfaces
d = sverk_interfaces.init(Nodename='cli_land')
resp = d.control.land(timeout=15.0)
print('LAND: ' + str(resp))
"""

SSH_CMD = "source /opt/ros/humble/setup.bash && source /home/sverk/sverk_ws/install/setup.bash && python3"

print(f"[land] drone={DRONE_IP}")
r = subprocess.run(
    ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     f"sverk@{DRONE_IP}", "-p", "22", SSH_CMD],
    input=PYTHON_SCRIPT, text=True, capture_output=True, timeout=30
)

print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)
