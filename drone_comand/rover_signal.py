#!/usr/bin/env python3
"""
Включение светодиодных сигналов на ровере.
Подключается по SSH к роверу и запускает на нём скрипт сигналов.
Использование: python3 rover_signal.py <rover-ip> [--script-path <path>]
Пример:       python3 rover_signal.py 192.168.1.200
"""

import subprocess
import sys

ROVER_IP = sys.argv[1] if len(sys.argv) > 1 else None

script_idx = next((i for i, a in enumerate(sys.argv) if a == "--script-path"), None)
REMOTE_SCRIPT = script_idx and sys.argv[script_idx + 1] or "/home/sverk/rover_control/signal.py"

if not ROVER_IP:
    print("Usage: python3 rover_signal.py <rover-ip> [--script-path <path>]")
    print("Example: python3 rover_signal.py 192.168.1.200")
    sys.exit(1)

PYTHON_SCRIPT = f"""
# TODO: заменить на реальный скрипт сигналов, когда будет готов
import sys
sys.path.insert(0, '/home/sverk/rover_control')
import signal as sig
sig.activate()

print('SIGNAL: LED signals activated')
"""

# Альтернативный вариант (закомментирован):
# PYTHON_SCRIPT = f"""
# exec(open('{REMOTE_SCRIPT}').read())
# activate_signals()
# print('SIGNAL: LED signals activated')
# """

SSH_CMD = "python3"

print(f"[rover_signal] ip={ROVER_IP}")
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