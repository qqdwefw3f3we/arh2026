#!/usr/bin/env python3
"""
Инициализация ровера перед миссией:
  1. Задать начальную клетку (initial-cell)
  2. Снять программный STOP (clear)

Должен вызываться один раз перед началом движения ровера.

Использование:
  python3 rover_init.py <rover-ip> [--col <col>] [--row <row>]
Пример:
  python3 rover_init.py 192.168.1.201            # cell (1, 1) yaw 0 по умолчанию
  python3 rover_init.py 192.168.1.201 --col 2 --row 3  # cell (2, 3) yaw 0
"""

import subprocess
import sys

ROVER_USER = "pi"
ROVER_PASSWORD = "raspberry"


def main():
    rover_ip = None
    col = 1
    row = 1

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--col" and i + 1 < len(sys.argv):
            col = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--row" and i + 1 < len(sys.argv):
            row = int(sys.argv[i + 1])
            i += 2
        elif not sys.argv[i].startswith("--") and rover_ip is None:
            rover_ip = sys.argv[i]
            i += 1
        else:
            i += 1

    if rover_ip is None:
        print("Usage: python3 rover_init.py <rover-ip> [--col <col>] [--row <row>]")
        print("Example: python3 rover_init.py 192.168.1.201")
        print("         python3 rover_init.py 192.168.1.201 --col 2 --row 3")
        sys.exit(1)

    url = f"http://{rover_ip}:8767"
    client = "tools/rover_control_client.py"

    print(f"[rover init] ip={rover_ip} initial-cell=({col}, {row}) yaw=0")

    remote_cmd = (
        f"cd ~/sverk_rover && "
        f"source install/setup.zsh 2>/dev/null; "
        f"python3 \"{client}\" --url \"{url}\" initial-cell {col} {row} --yaw 0 && "
        f"python3 \"{client}\" --url \"{url}\" clear"
    )

    r = subprocess.run(
        ["sshpass", "-p", ROVER_PASSWORD, "ssh",
         "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=5",
         "-o", "UserKnownHostsFile=/dev/null",
         f"{ROVER_USER}@{rover_ip}", "-p", "22", remote_cmd],
        capture_output=True, text=True, timeout=30
    )

    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
