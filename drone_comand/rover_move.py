#!/usr/bin/env python3
"""
Управление наземным ровером: движение в точку (x, y).
Подключается по SSH к роверу и запускает на нём скрипт движения.
Использование: python3 rover_move.py <rover-ip> <x> <y> [--script-path <path>]
Пример:       python3 rover_move.py 192.168.1.200 -2.0 -1.2
"""

import subprocess
import sys

ROVER_IP = sys.argv[1] if len(sys.argv) > 1 else None
X = sys.argv[2] if len(sys.argv) > 2 else None
Y = sys.argv[3] if len(sys.argv) > 3 else None

script_idx = next((i for i, a in enumerate(sys.argv) if a == "--script-path"), None)
REMOTE_SCRIPT = sys.argv[script_idx + 1] if script_idx is not None else "/home/sverk/rover_control/move.py"

if not all([ROVER_IP, X, Y]):
    print("Usage: python3 rover_move.py <rover-ip> <x> <y> [--script-path <path>]")
    print("Example: python3 rover_move.py 192.168.1.200 -2.0 -1.2")
    sys.exit(1)

PYTHON_SCRIPT = f"""
import sys
sys.path.insert(0, '/home/sverk/rover_control')
import move
move.move_to({X}, {Y})
"""
# TODO: заменить на реальный скрипт ровера, когда будет готов
# PYTHON_SCRIPT = f"""
# exec(open('{REMOTE_SCRIPT}').read())
# move_to({X}, {Y})
# """

SSH_CMD = "python3"

print(f"[rover] ip={ROVER_IP} target=({X}, {Y})")
r = subprocess.run(
    ["sshpass", "-p", "sverk", "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
     "-o", "UserKnownHostsFile=/dev/null",
     f"sverk@{ROVER_IP}", "-p", "22", SSH_CMD],
    input=PYTHON_SCRIPT, text=True, capture_output=True, timeout=30
)

print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)