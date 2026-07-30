#!/usr/bin/env python3
"""
Управление наземным ровером: движение в клетку сетки 6×6.
Принимает drone-координаты (x, y), переводит в rover-клетку (col, row 1..6)
и отправляет команду goal-cell через HTTP API.

Формула перевода:
  rover_col = round((drone_x - DRONE_MIN) / (DRONE_MAX - DRONE_MIN) * (GRID_SIZE - 1)) + 1
  rover_row = round((drone_y - DRONE_MIN) / (DRONE_MAX - DRONE_MIN) * (GRID_SIZE - 1)) + 1
  DRONE_MIN = -2.0, DRONE_MAX = 2.0, GRID_SIZE = 6
  → rover_col = round((drone_x + 2.0) * 5 / 4) + 1

Использование:
  python3 rover_move.py <rover-ip> <drone-x> <drone-y> [--yaw <angle>]
Примеры:
  python3 rover_move.py 192.168.1.201 -2.0 -2.0       # → rover cell (1, 1)
  python3 rover_move.py 192.168.1.201  2.0  2.0       # → rover cell (6, 6)
  python3 rover_move.py 192.168.1.201  0.0  0.0 --yaw 90  # → rover cell (3, 3) yaw 90
"""

import subprocess
import sys

DRONE_MIN = -2.0
DRONE_MAX = 2.0
GRID_SIZE = 6
ROVER_USER = "pi"
ROVER_PASSWORD = "raspberry"


def drone_to_rover_cell(drone_x, drone_y):
    """Перевод drone-координат (x, y) в rover-клетку (col, row 1..6)."""
    col = round((drone_x - DRONE_MIN) / (DRONE_MAX - DRONE_MIN) * (GRID_SIZE - 1)) + 1
    row = round((drone_y - DRONE_MIN) / (DRONE_MAX - DRONE_MIN) * (GRID_SIZE - 1)) + 1
    col = max(1, min(GRID_SIZE, col))
    row = max(1, min(GRID_SIZE, row))
    return col, row


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 rover_move.py <rover-ip> <drone-x> <drone-y> [--yaw <angle>]")
        print("Example: python3 rover_move.py 192.168.1.201 -2.0 -2.0")
        print("         python3 rover_move.py 192.168.1.201  2.0  2.0 --yaw 90")
        sys.exit(1)

    rover_ip = sys.argv[1]
    drone_x = float(sys.argv[2])
    drone_y = float(sys.argv[3])

    yaw = 0
    yaw_idx = next((i for i, a in enumerate(sys.argv) if a == "--yaw"), None)
    if yaw_idx is not None and yaw_idx + 1 < len(sys.argv):
        yaw = int(sys.argv[yaw_idx + 1])

    col, row = drone_to_rover_cell(drone_x, drone_y)
    url = f"http://{rover_ip}:8767"
    client = "tools/rover_control_client.py"

    print(f"[rover] ip={rover_ip} drone=({drone_x}, {drone_y}) → rover_cell=({col}, {row}) yaw={yaw}")

    remote_cmd = (
        f"cd ~/sverk_rover && "
        f"source install/setup.zsh 2>/dev/null; "
        f"python3 \"{client}\" --url \"{url}\" goal-cell {col} {row} --yaw {yaw} --replace"
    )

    r = subprocess.run(
        ["sshpass", "-p", ROVER_PASSWORD, "ssh",
         "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=5",
         "-o", "UserKnownHostsFile=/dev/null",
         f"{ROVER_USER}@{rover_ip}", "-p", "22", remote_cmd],
        capture_output=True, text=True, timeout=60
    )

    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
