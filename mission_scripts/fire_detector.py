#!/usr/bin/env python3
"""
Детектор огоньков на снимках облёта.
Анализирует все cell_*.jpg в drone_comand/img/,
ищет красные точки (огоньки) в центральной области изображения.

Использование: python3 fire_detector.py [--img-dir <путь>] [--config <путь>]
"""

import os
import sys
import re
import json
import argparse

try:
    from PIL import Image
except ImportError:
    print("[fire_detector] ERROR: PIL/Pillow not installed. Install: pip install Pillow")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_IMG_DIR = os.path.join(PROJECT_DIR, "drone_comand", "img")
DEFAULT_CONFIG = os.path.join(PROJECT_DIR, "config.json")

RED_R_THRESHOLD = 180
RED_G_MAX = 100
RED_B_MAX = 100
CENTER_ZONE_RATIO = 0.4
MIN_RED_RATIO = 0.01


def extract_coords(filename):
    match = re.search(r'__x(-?[\d.]+)_y(-?[\d.]+)\.jpg$', filename)
    if match:
        return float(match.group(1)), float(match.group(2))
    match = re.search(r'cell_(\d+)_(\d+)', filename)
    if match:
        return None, None
    return None, None


def is_red_pixel(r, g, b):
    return r > RED_R_THRESHOLD and g < RED_G_MAX and b < RED_B_MAX


def detect_fire(image_path):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    pixels = img.load()

    cx1 = int(w * (0.5 - CENTER_ZONE_RATIO / 2))
    cx2 = int(w * (0.5 + CENTER_ZONE_RATIO / 2))
    cy1 = int(h * (0.5 - CENTER_ZONE_RATIO / 2))
    cy2 = int(h * (0.5 + CENTER_ZONE_RATIO / 2))

    red_count = 0
    total_center = 0

    for x in range(cx1, cx2):
        for y in range(cy1, cy2):
            r, g, b = pixels[x, y]
            total_center += 1
            if is_red_pixel(r, g, b):
                red_count += 1

    if total_center == 0:
        return False, 0.0

    ratio = red_count / total_center
    detected = ratio > MIN_RED_RATIO
    return detected, round(ratio, 4)


def update_config(config_path, detections):
    with open(config_path, "r") as f:
        config = json.load(f)

    config["detected_fires"] = detections

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"[fire_detector] Config updated: {config_path}")


def main():
    parser = argparse.ArgumentParser(description="Fire detector on survey images")
    parser.add_argument("--img-dir", default=DEFAULT_IMG_DIR, help="Image directory")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config file path")
    args = parser.parse_args()

    img_dir = args.img_dir
    config_path = args.config

    if not os.path.isdir(img_dir):
        print(f"[fire_detector] ERROR: image dir not found: {img_dir}")
        sys.exit(1)

    files = sorted(
        [f for f in os.listdir(img_dir) if f.startswith("cell_") and f.endswith(".jpg")]
    )

    if not files:
        print("[fire_detector] No cell_*.jpg images found")
        sys.exit(0)

    print(f"[fire_detector] Analyzing {len(files)} images...")
    detections = []

    for f in files:
        path = os.path.join(img_dir, f)
        x, y = extract_coords(f)

        if x is None:
            print(f"[fire_detector] SKIP {f}: no coordinates in filename")
            continue

        fire, ratio = detect_fire(path)
        status = "FIRE" if fire else "clear"
        print(f"[fire_detector] {f}  coords=({x},{y})  {status}  red_ratio={ratio}")

        if fire:
            detections.append({
                "cell": re.match(r'(cell_\d+_\d+)', f).group(1) if re.match(r'(cell_\d+_\d+)', f) else f,
                "x": x,
                "y": y,
                "red_ratio": ratio,
                "image": f
            })

    print(f"[fire_detector] Found {len(detections)} fire(s)")

    if detections:
        for d in detections:
            print(f"  FIRE at ({d['x']}, {d['y']}) — {d['image']} (ratio={d['red_ratio']})")
        update_config(config_path, detections)
    else:
        print("[fire_detector] No fires detected — config not modified")
        update_config(config_path, [])

    sys.exit(0)


if __name__ == "__main__":
    main()