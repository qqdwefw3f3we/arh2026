# Drone Command Scripts

Скрипты для управления дроном через SSH + ROS2 (sverk_interfaces).

## Команды

| Файл | Назначение | Вызов |
|------|-----------|-------|
| `takeoff.py` | Взлёт в body-кадре | `python3 takeoff.py <ip> [высота_м]` |
| `move.py` | Полёт в точку по ArUco | `python3 move.py <ip> <x> <y> [высота_м]` |
| `land.py` | Посадка | `python3 land.py <ip>` |
| `save_img.py` | Снимок с камеры | `python3 save_img.py <ip> [имя_файла]` |

> **save_img.py** сохраняет фото в локальную папку `img/` рядом со скриптом.
> Достаточно передать только имя файла, путь подставится автоматически.

## Примеры

```bash
# Взлёт на 1.5 метра
python3 takeoff.py 192.168.1.111

# Взлёт на 2 метра
python3 takeoff.py 192.168.1.111 2.0

# Полёт в точку (2.0, 3.0) в кадре aruco_map на высоте 1.5м
python3 move.py 192.168.1.111 2.0 3.0

# Полёт в точку на высоте 2.0м
python3 move.py 192.168.1.111 2.0 3.0 2.0

# Посадка
python3 land.py 192.168.1.111

# Сохранить фото с камеры (автоматически в img/)
python3 save_img.py 192.168.1.111
python3 save_img.py 192.168.1.111 my_photo.jpg
```

## Полный сценарий облёта

```bash
DRONE=192.168.1.111

# 1. Взлёт
python3 takeoff.py $DRONE 1.5

# 2. Облёт квадрата (фото в drone_comand/img/)
python3 move.py $DRONE 0.0 0.0
python3 save_img.py $DRONE cell_0_0.jpg

python3 move.py $DRONE 1.6 0.0
python3 save_img.py $DRONE cell_1_0.jpg

python3 move.py $DRONE 1.6 1.6
python3 save_img.py $DRONE cell_1_1.jpg

python3 move.py $DRONE 0.0 1.6
python3 save_img.py $DRONE cell_0_1.jpg

# 3. Посадка
python3 land.py $DRONE
```

## Как это работает

```
takeoff.py → SSH → дрон → sverk_interfaces → offboard_control → PX4 → моторы

move.py    → SSH → дрон → sverk_interfaces.navigate_wait(frame_id="aruco_map")
             → ждёт прилёта в точку (timeout 30с) → return code 0 при успехе

land.py    → SSH → дрон → sverk_interfaces.control.land()
             → автоматическая посадка

save_img.py → SSH → дрон → cv2.imwrite(/tmp/...) → scp → локальная img/
```

Каждый скрипт блокируется до завершения действия. Агент может вызывать их последовательно — каждая команда не вернёт управление, пока не выполнена.

Все координаты в move — в метрах в кадре `aruco_map`. Требуется ArUco-локализация на дроне.

---

## Zoo Code / AI Agent Usage

### Базовые команды для агента

При передаче этих инструкций AI-агенту (Zoo Code), используй следующий формат:

```
Агент, у тебя есть доступ к дрону через Python-скрипты. Путь к скриптам:
/home/user/arh2026/ai/simple_project/drone_comand/

Доступные действия:
1. python3 /home/user/arh2026/ai/simple_project/drone_comand/takeoff.py <ip> [alt]
   — взлёт дрона, alt по умолчанию 1.5м. Блокируется до завершения.

2. python3 /home/user/arh2026/ai/simple_project/drone_comand/move.py <ip> <x> <y> [alt]
   — полёт в координаты (x, y) в кадре aruco_map, alt по умолчанию 1.5м.
   Блокируется до прилёта в точку (timeout 30с). Возвращает код 0 при успехе.

3. python3 /home/user/arh2026/ai/simple_project/drone_comand/land.py <ip>
   — посадка дрона

4. python3 /home/user/arh2026/ai/simple_project/drone_comand/save_img.py <ip> [filename]
   — сохранить снимок с камеры в локальную папку img/.
   filename по умолчанию photo.jpg. Фото скачивается с дрона через scp.

IP дрона: 192.168.1.111
Все координаты в метрах в системе aruco_map.
Все скрипты блокирующие — каждая следующая команда выполняется только после завершения предыдущей.
```

### Пример задачи для агента

```
Облети квадрат 1.6×1.6 метра, делая фото в каждом углу.
После облёта посади дрон.
IP дрона: 192.168.1.111
```

Агент вызовет последовательно:
```
python3 takeoff.py 192.168.1.111 1.5
python3 move.py 192.168.1.111 0.0 0.0
python3 save_img.py 192.168.1.111 cell_0_0.jpg
python3 move.py 192.168.1.111 1.6 0.0
python3 save_img.py 192.168.1.111 cell_1_0.jpg
python3 move.py 192.168.1.111 1.6 1.6
python3 save_img.py 192.168.1.111 cell_1_1.jpg
python3 move.py 192.168.1.111 0.0 1.6
python3 save_img.py 192.168.1.111 cell_0_1.jpg
python3 land.py 192.168.1.111
```

### Важно

- takeoff использует **body-кадр** (аварийный подскок) — маркеры с земли могут быть не видны
- move использует **aruco_map** — маркеры должны быть видны, иначе команда не выполнится
- После взлёта дрон автоматически пытается поймать ArUco-маркеры
- save_img сохраняет фото в локальную папку `img/` через scp — дрон должен быть доступен по SSH
