#!/usr/bin/env python3
"""
Скрипт облёта полигона N×N змейкой.
Взлёт → облёт всех ячеек с фото → посадка.
При любой ошибке — аварийная посадка.
Отказоустойчивый: повторяет взлёт и посадку при сбоях.

Использование: python3 survey_grid.py <ip> <altitude> <N> <cell_size>
Пример:       python3 survey_grid.py 192.168.1.111 1.5 4 0.8
"""

import subprocess
import sys
import time

SCRIPTS = "/home/user/arh2026/ai/simple_project/drone_comand"
DRONE_IP = None
completed_cells = 0
total_cells = 0


def run(cmd, desc=""):
    global completed_cells
    print(f"[survey] {desc}")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"[ERROR] {desc} FAILED (code={r.returncode})", file=sys.stderr)
        emergency_land()
        sys.exit(1)
    completed_cells += 1


def emergency_land():
    print("[survey] EMERGENCY LANDING")
    for attempt in (1, 2):
        r = subprocess.run(["python3", f"{SCRIPTS}/land.py", DRONE_IP])
        if r.returncode == 0:
            print("[survey] Emergency landing OK")
            return
        print(f"[survey] Emergency landing attempt {attempt} FAILED (code={r.returncode})")
        if attempt == 1:
            time.sleep(2.0)
    print("[survey] CRITICAL: emergency landing failed after 2 attempts")


def try_takeoff(ALT):
    for attempt in (1, 2):
        print(f"[survey] TAKEOFF {ALT}m (attempt {attempt})")
        r = subprocess.run(["python3", f"{SCRIPTS}/takeoff.py", DRONE_IP, ALT])
        if r.returncode == 0:
            return True
        print(f"[survey] Takeoff attempt {attempt} FAILED (code={r.returncode})")
        if attempt == 1:
            print("[survey] Retrying takeoff in 3s...")
            time.sleep(3.0)
    return False


def generate_cells(N, cell_size):
    offset = (N - 1) * cell_size / 2
    cells = []
    for i in range(N):
        if i % 2 == 0:
            x_values = [-offset + j * cell_size for j in range(N)]
        else:
            x_values = [-offset + j * cell_size for j in range(N - 1, -1, -1)]
        for j, x in enumerate(x_values):
            y = -offset + i * cell_size
            cells.append((round(x, 2), round(y, 2), f"cell_{i}_{j}.jpg"))
    return cells


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 survey_grid.py <ip> <altitude> <N> <cell_size>")
        print("Example: python3 survey_grid.py 192.168.1.111 1.5 4 0.8")
        sys.exit(1)

    global DRONE_IP, total_cells
    DRONE_IP = sys.argv[1]
    ALT = sys.argv[2]
    N = int(sys.argv[3])
    CELL_SIZE = float(sys.argv[4])

    cells = generate_cells(N, CELL_SIZE)
    total_cells = len(cells)

    print(f"[survey] Drone: {DRONE_IP}")
    print(f"[survey] Grid: {N}x{N}, Alt: {ALT}m, Cell: {CELL_SIZE}m")
    print(f"[survey] Total cells: {total_cells}")

    if not try_takeoff(ALT):
        print("[survey] TAKEOFF FAILED after 2 attempts — aborting mission")
        sys.exit(1)

    print("[survey] Waiting 3s for ArUco capture...")
    time.sleep(3.0)

    for x, y, name in cells:
        run(["python3", f"{SCRIPTS}/move.py", DRONE_IP, str(x), str(y), ALT],
            f"Move to ({x}, {y})")
        time.sleep(1.0)
        r = subprocess.run(["python3", f"{SCRIPTS}/save_img.py", DRONE_IP, name])
        if r.returncode != 0:
            print(f"[survey] Photo {name} FAILED (code={r.returncode}) — continuing")
        else:
            print(f"[survey] Photo: {name}")
        time.sleep(0.5)

    print(f"[survey] LAND ({completed_cells}/{total_cells} cells surveyed)")
    for attempt in (1, 2):
        r = subprocess.run(["python3", f"{SCRIPTS}/land.py", DRONE_IP])
        if r.returncode == 0:
            print(f"[survey] DONE — {completed_cells}/{total_cells} photos")
            sys.exit(0 if completed_cells == total_cells else 2)
        print(f"[survey] Land attempt {attempt} FAILED (code={r.returncode})")
        if attempt == 1:
            time.sleep(2.0)

    print(f"[survey] LAND FAILED after 2 attempts — {completed_cells}/{total_cells} photos")
    sys.exit(3)


if __name__ == "__main__":
    main()