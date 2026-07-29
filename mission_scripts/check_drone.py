#!/usr/bin/env python3
"""
Check-цикл для дрона, не участвующего в облёте.
Взлёт 1.5м → ждать 3с → фото → посадка.
Отказоустойчивый: при ошибке на любом этапе пытается продолжить.

Использование: python3 check_drone.py <ip> <drone_id>
Пример:       python3 check_drone.py 192.168.1.112 2
"""

import subprocess
import sys
import time

SCRIPTS = "/home/user/arh2026/ai/simple_project/drone_comand"

if len(sys.argv) < 3:
    print("Usage: python3 check_drone.py <ip> <drone_id>")
    print("Example: python3 check_drone.py 192.168.1.112 2")
    sys.exit(1)

ip = sys.argv[1]
drone_id = sys.argv[2]
filename = f"drone_{drone_id}_check.jpg"
alt = "1.5"
took_off = False
all_ok = True


def try_takeoff():
    global took_off
    for attempt in (1, 2):
        print(f"[check] Drone-{drone_id} ({ip}): TAKEOFF {alt}m (attempt {attempt})")
        r = subprocess.run(["python3", f"{SCRIPTS}/takeoff.py", ip, alt])
        if r.returncode == 0:
            took_off = True
            return True
        print(f"[check] Drone-{drone_id} ({ip}): takeoff attempt {attempt} FAILED (code={r.returncode})")
        if attempt == 1:
            print(f"[check] Drone-{drone_id} ({ip}): retrying in 3s...")
            time.sleep(3.0)
    return False


def try_land():
    for attempt in (1, 2):
        print(f"[check] Drone-{drone_id} ({ip}): LAND (attempt {attempt})")
        r = subprocess.run(["python3", f"{SCRIPTS}/land.py", ip])
        if r.returncode == 0:
            return True
        print(f"[check] Drone-{drone_id} ({ip}): land attempt {attempt} FAILED (code={r.returncode})")
        if attempt == 1:
            time.sleep(2.0)
    return False


# --- MAIN ---
print(f"[check] Drone-{drone_id} ({ip}): starting check cycle")

if not try_takeoff():
    print(f"[check] Drone-{drone_id} ({ip}): TAKEOFF FAILED after 2 attempts — skipping drone")
    sys.exit(1)

print(f"[check] Drone-{drone_id} ({ip}): waiting 3s for stabilization...")
time.sleep(3.0)

print(f"[check] Drone-{drone_id} ({ip}): PHOTO → {filename}")
r = subprocess.run(["python3", f"{SCRIPTS}/save_img.py", ip, filename])
if r.returncode != 0:
    print(f"[check] Drone-{drone_id} ({ip}): PHOTO FAILED (code={r.returncode}) — continuing")
    all_ok = False

print(f"[check] Drone-{drone_id} ({ip}): LAND")
if not try_land():
    print(f"[check] Drone-{drone_id} ({ip}): LAND FAILED after 2 attempts")
    all_ok = False
    sys.exit(1)

status = "OK" if all_ok else "PARTIAL"
print(f"[check] Drone-{drone_id} ({ip}): DONE ({status})")
sys.exit(0 if all_ok else 1)