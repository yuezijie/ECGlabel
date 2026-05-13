"""生日鹅鸭杀寻礼小游戏。

运行：
    python birthday_goose_hunt.py

玩法：WASD 控制白鹅在大地图探索；靠近藏起来的鸭子后，鼠标左键点击它；
被“砍倒”的鸭子会变成鸡腿并弹出 1-10 的礼物编号。全部找到后游戏结束。
"""

from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox


WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
WORLD_WIDTH = 2800
WORLD_HEIGHT = 1900
PLAYER_SPEED = 7
DISCOVER_RADIUS = 250
ATTACK_RADIUS = 110
PLAYER_COLLISION_RADIUS = 32
ENEMY_COUNT = 10

SPACE_COLOR = "#0d1630"
CORRIDOR_COLOR = "#314f73"
WALL_COLOR = "#0b1427"
WALL_EDGE_COLOR = "#73a7d2"
SHADOW_COLOR = "#07101f"
PLAYER_COLOR = "#fff8e7"
DUCK_COLOR = "#ffd45f"
DUCK_HEAD_COLOR = "#2f9f6b"
DEFEATED_COLOR = "#9d5454"
HIGHLIGHT_COLOR = "#ffd65c"
TEXT_COLOR = "#fff4c7"
GOLD_COLOR = "#f7bf3f"


@dataclass(frozen=True)
class Room:
    """飞船地图上的房间。"""

    name: str
    x1: float
    y1: float
    x2: float
    y2: float
    color: str


@dataclass(frozen=True)
class Prop:
    """飞船房间里的装饰物。"""

    kind: str
    x: float
    y: float
    w: float
    h: float
    color: str
    label: str = ""


@dataclass
class Goose:
    """地图上的隐藏鸭子。"""

    x: float
    y: float
    gift_number: int
    defeated: bool = False

    def distance_to(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)


@dataclass
class Player:
    """玩家控制的白鹅。"""

    x: float = WORLD_WIDTH / 2
    y: float = WORLD_HEIGHT / 2
    facing: str = "right"


ROOMS = [
    Room("舰桥", 1080, 120, 1740, 430, "#2c486c"),
    Room("厨房", 230, 190, 820, 560, "#304e6f"),
    Room("货舱", 1980, 170, 2600, 610, "#2e4a64"),
    Room("花园舱", 120, 760, 760, 1240, "#294f48"),
    Room("大厅", 970, 690, 1810, 1180, "#335575"),
    Room("医疗舱", 2030, 820, 2630, 1240, "#30506f"),
    Room("反应堆", 280, 1400, 900, 1780, "#453c67"),
    Room("礼物仓库", 1130, 1360, 1730, 1780, "#4b3f65"),
    Room("休息室", 1980, 1420, 2610, 1790, "#3a4d73"),
]

CORRIDORS = [
    (780, 330, 1110, 420),
    (1710, 310, 2010, 420),
    (1400, 410, 1500, 715),
    (760, 930, 990, 1030),
    (1800, 930, 2050, 1030),
    (1380, 1165, 1490, 1380),
    (760, 1510, 1150, 1615),
    (1710, 1530, 2000, 1630),
    (470, 1230, 590, 1415),
]

PROPS = [
    Prop("console", 1190, 190, 180, 70, "#4fc3f7", "NAV"),
    Prop("console", 1450, 190, 190, 70, "#8bd6ff", "MAP"),
    Prop("table", 430, 330, 180, 95, "#c58b49", ""),
    Prop("crate", 2110, 300, 125, 110, "#9c6b3e", ""),
    Prop("crate", 2350, 400, 150, 120, "#8b5e36", ""),
    Prop("plant", 280, 900, 90, 130, "#55bb6a", ""),
    Prop("plant", 560, 1080, 95, 140, "#4ead63", ""),
    Prop("round_table", 1220, 815, 170, 170, "#d3a34f", ""),
    Prop("round_table", 1530, 930, 170, 170, "#d3a34f", ""),
    Prop("bed", 2140, 920, 190, 95, "#a7d7ff", ""),
    Prop("bed", 2380, 1070, 190, 95, "#a7d7ff", ""),
    Prop("reactor", 455, 1495, 250, 180, "#8f7dff", ""),
    Prop("gift", 1280, 1475, 130, 130, "#ff6b8a", ""),
    Prop("gift", 1480, 1570, 150, 150, "#7dd3fc", ""),
    Prop("sofa", 2130, 1530, 310, 120, "#e28b6d", ""),
]

WALKABLE_AREAS = [
    (room.x1, room.y1, room.x2, room.y2) for room in ROOMS
] + CORRIDORS

DOORS = [
    (945, 335, 990, 415, "厨房 → 舰桥"),
    (1710, 325, 1760, 410, "舰桥 → 货舱"),
    (1410, 620, 1490, 690, "舰桥 ↓ 大厅"),
    (760, 940, 845, 1020, "花园舱 → 大厅"),
    (1800, 940, 1880, 1020, "大厅 → 医疗舱"),
    (1390, 1295, 1485, 1380, "大厅 ↓ 礼物仓库"),
    (865, 1525, 950, 1610, "反应堆 → 礼物仓库"),
    (1710, 1540, 1795, 1625, "礼物仓库 → 休息室"),
]

LIGHTS = [
    (1410, 260, 260, "#7fd7ff"),
    (540, 385, 235, "#ffd68a"),
    (2300, 410, 260, "#9fdfff"),
    (1430, 930, 330, "#b2e7ff"),
    (515, 1590, 300, "#b395ff"),
    (1450, 1560, 300, "#ffd36f"),
    (2300, 1570, 250, "#ffad8b"),
]

FLOOR_DECALS = [
    (1340, 930, 210, 72, "生日快乐", "#f7bf3f"),
    (1320, 1575, 260, 84, "GIFT BAY", "#ffdd80"),
    (2050, 520, 170, 54, "CARGO", "#b9e8ff"),
]


TELEMETRY_DOTS = [
    (110, 120),
    (420, 90),
    (840, 1550),
    (1830, 122),
    (2490, 760),
    (2620, 1320),
    (1640, 1860),
]


def point_in_rect(x: float, y: float, area: tuple[float, float, float, float]) -> bool:
    """判断点是否在矩形区域内。"""

    x1, y1, x2, y2 = area
    return x1 <= x <= x2 and y1 <= y <= y2


def point_in_walkable_area(x: float, y: float) -> bool:
    """判断点是否落在房间或走廊内。"""

    return any(point_in_rect(x, y, area) for area in WALKABLE_AREAS)


def is_walkable(x: float, y: float, radius: float = PLAYER_COLLISION_RADIUS) -> bool:
    """用多采样碰撞体判断角色是否能站在目标位置。"""

    samples = [
        (x, y),
        (x - radius, y),
        (x + radius, y),
        (x, y - radius),
        (x, y + radius),
        (x - radius * 0.72, y - radius * 0.72),
        (x + radius * 0.72, y - radius * 0.72),
        (x - radius * 0.72, y + radius * 0.72),
        (x + radius * 0.72, y + radius * 0.72),
    ]
    return all(point_in_walkable_area(sample_x, sample_y) for sample_x, sample_y in samples)

def clamp(value: float, minimum: float, maximum: float) -> float:
    """把数值限制在给定范围内。"""

    return max(minimum, min(value, maximum))


def make_hidden_geese(seed: int | None = 20260508) -> list[Goose]:
    """生成 10 只藏在房间角落和偏僻通道的鸭子。"""

    rng = random.Random(seed)
    gift_numbers = list(range(1, ENEMY_COUNT + 1))
    rng.shuffle(gift_numbers)

    hiding_spots = [
        (350, 265),
        (720, 515),
        (1125, 395),
        (2540, 560),
        (185, 1170),
        (710, 815),
        (2085, 1210),
        (360, 1730),
        (1695, 1750),
        (2580, 1450),
    ]

    geese: list[Goose] = []
    for index, (x, y) in enumerate(hiding_spots):
        goose_x = x
        goose_y = y
        for _ in range(30):
            candidate_x = clamp(x + rng.randint(-55, 55), 80, WORLD_WIDTH - 80)
            candidate_y = clamp(y + rng.randint(-55, 55), 80, WORLD_HEIGHT - 80)
            if is_walkable(candidate_x, candidate_y, radius=24):
                goose_x = candidate_x
                goose_y = candidate_y
                break
        geese.append(Goose(x=goose_x, y=goose_y, gift_number=gift_numbers[index]))
    return geese


class BirthdayGooseGame:
    """一个使用 Tkinter Canvas 绘制的轻量小游戏。"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("生日快乐！鹅鸭杀寻礼物")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=SPACE_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.player = Player()
        self.geese = make_hidden_geese()
        self.keys: set[str] = set()
        self.game_over = False
        self.last_message = "WASD 控制白鹅探索飞船，靠近藏鸭后用鼠标左键点击。"
        self.tick = 0

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.after(16, self.game_loop)

    def camera(self) -> tuple[float, float]:
        camera_x = clamp(self.player.x - WINDOW_WIDTH / 2, 0, WORLD_WIDTH - WINDOW_WIDTH)
        camera_y = clamp(self.player.y - WINDOW_HEIGHT / 2, 0, WORLD_HEIGHT - WINDOW_HEIGHT)
        return camera_x, camera_y

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        camera_x, camera_y = self.camera()
        return x - camera_x, y - camera_y

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        camera_x, camera_y = self.camera()
        return x + camera_x, y + camera_y

    def on_key_press(self, event: tk.Event) -> None:
        self.keys.add(event.keysym.lower())

    def on_key_release(self, event: tk.Event) -> None:
        self.keys.discard(event.keysym.lower())

    def move_player(self) -> None:
        dx = 0
        dy = 0
        if "w" in self.keys or "up" in self.keys:
            dy -= 1
        if "s" in self.keys or "down" in self.keys:
            dy += 1
        if "a" in self.keys or "left" in self.keys:
            dx -= 1
        if "d" in self.keys or "right" in self.keys:
            dx += 1

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        if dx < 0:
            self.player.facing = "left"
        elif dx > 0:
            self.player.facing = "right"

        next_x = clamp(self.player.x + dx * PLAYER_SPEED, 35, WORLD_WIDTH - 35)
        next_y = clamp(self.player.y + dy * PLAYER_SPEED, 35, WORLD_HEIGHT - 35)

        if is_walkable(next_x, self.player.y):
            self.player.x = next_x
        if is_walkable(self.player.x, next_y):
            self.player.y = next_y

    def on_click(self, event: tk.Event) -> None:
        if self.game_over:
            return

        world_x, world_y = self.screen_to_world(event.x, event.y)
        target = self.pick_target(world_x, world_y)
        if target is None:
            self.last_message = "再靠近一点，或者点准头顶有 ! 的鸭子！"
            return

        target.defeated = True
        remaining = sum(not goose.defeated for goose in self.geese)
        self.last_message = f"获得礼物编号 {target.gift_number}！还剩 {remaining} 只鸭子。"
        messagebox.showinfo("礼物时间", f"你砍倒了一只鸭子！请拿出 {target.gift_number} 号礼物。")

        if remaining == 0:
            self.finish_game()

    def pick_target(self, world_x: float, world_y: float) -> Goose | None:
        candidates = []
        for goose in self.geese:
            if goose.defeated:
                continue
            close_to_player = goose.distance_to(self.player.x, self.player.y) <= ATTACK_RADIUS
            clicked_goose = goose.distance_to(world_x, world_y) <= 48
            if close_to_player and clicked_goose:
                candidates.append(goose)
        return min(candidates, key=lambda goose: goose.distance_to(world_x, world_y), default=None)

    def finish_game(self) -> None:
        self.game_over = True
        self.last_message = "所有礼物都找到啦，生日快乐！"
        messagebox.showinfo("生日快乐", "10 份礼物全部解锁！祝你生日快乐，天天开心！")

    def game_loop(self) -> None:
        if not self.game_over:
            self.move_player()
            self.tick += 1
        self.draw()
        self.root.after(16, self.game_loop)

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_space_background()
        self.draw_ship_map()
        self.draw_geese()
        self.draw_player()
        self.draw_atmosphere()
        self.draw_hud()

    def draw_space_background(self) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=SPACE_COLOR, outline="")
        for index, (x, y) in enumerate(TELEMETRY_DOTS):
            sx = (x - camera_x * 0.28) % WINDOW_WIDTH
            sy = (y - camera_y * 0.28) % WINDOW_HEIGHT
            radius = 1 + index % 3
            self.canvas.create_oval(sx - radius, sy - radius, sx + radius, sy + radius, fill="#b6d8ff", outline="")

    def draw_ship_map(self) -> None:
        for x1, y1, x2, y2 in CORRIDORS:
            self.draw_panel(x1, y1, x2, y2, CORRIDOR_COLOR, "")
            self.draw_floor_lines(x1, y1, x2, y2, 120)

        for room in ROOMS:
            self.draw_panel(room.x1, room.y1, room.x2, room.y2, room.color, room.name)
            self.draw_floor_lines(room.x1, room.y1, room.x2, room.y2, 110)

        self.draw_light_spills()
        for x, y, w, h, text, color in FLOOR_DECALS:
            self.draw_floor_decal(x, y, w, h, text, color)
        for x1, y1, x2, y2, label in DOORS:
            self.draw_door(x1, y1, x2, y2, label)
        for prop in PROPS:
            self.draw_prop(prop)

    def draw_panel(self, x1: float, y1: float, x2: float, y2: float, fill: str, label: str) -> None:
        bevel = 30
        panel_points = [
            x1 + bevel,
            y1,
            x2 - bevel,
            y1,
            x2,
            y1 + bevel,
            x2,
            y2 - bevel,
            x2 - bevel,
            y2,
            x1 + bevel,
            y2,
            x1,
            y2 - bevel,
            x1,
            y1 + bevel,
        ]
        self.create_world_polygon(*[coord + 12 if index % 2 == 0 else coord + 16 for index, coord in enumerate(panel_points)], fill=SHADOW_COLOR, outline="")
        self.create_world_rectangle(x1 - 20, y1 - 20, x2 + 20, y2 + 20, fill=WALL_COLOR, outline="")
        self.create_world_polygon(*panel_points, fill=fill, outline=WALL_EDGE_COLOR, width=4)
        self.create_world_rectangle(x1 + 18, y1 + 18, x2 - 18, y2 - 18, fill="", outline="#456b91", width=1)
        self.create_world_line(x1 + 36, y1 + 24, x2 - 36, y1 + 24, fill="#83bee8", width=2)
        self.create_world_line(x1 + 36, y2 - 24, x2 - 36, y2 - 24, fill="#162944", width=3)
        if label:
            sx, sy = self.world_to_screen((x1 + x2) / 2, y1 + 35)
            self.canvas.create_text(sx + 2, sy + 2, text=label, fill="#102235", font=("Microsoft YaHei", 15, "bold"))
            self.canvas.create_text(sx, sy, text=label, fill="#d9f3ff", font=("Microsoft YaHei", 15, "bold"))

    def draw_floor_lines(self, x1: float, y1: float, x2: float, y2: float, spacing: int) -> None:
        start_x = int(x1 // spacing * spacing)
        start_y = int(y1 // spacing * spacing)
        for x in range(start_x, int(x2) + spacing, spacing):
            self.create_world_line(x, y1 + 12, x, y2 - 12, fill="#3e5f83")
            self.create_world_line(x + spacing / 2, y1 + 18, x + spacing / 2, y2 - 18, fill="#284563")
        for y in range(start_y, int(y2) + spacing, spacing):
            self.create_world_line(x1 + 12, y, x2 - 12, y, fill="#20364f")

    def draw_light_spills(self) -> None:
        for x, y, radius, color in LIGHTS:
            self.create_world_oval(x - radius, y - radius * 0.62, x + radius, y + radius * 0.62, fill=color, outline="", stipple="gray12")

    def draw_floor_decal(self, x: float, y: float, w: float, h: float, text: str, color: str) -> None:
        self.create_world_oval(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill="#10233a", outline=color, width=2)
        self.create_world_text(x, y, text, fill=color, font=("Arial", 12, "bold"))

    def draw_door(self, x1: float, y1: float, x2: float, y2: float, label: str) -> None:
        self.create_world_rectangle(x1, y1, x2, y2, fill="#132941", outline="#a6e8ff", width=2)
        self.create_world_rectangle(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill="", outline="#4bc3ff", width=2)
        self.create_world_line(x1 + 12, (y1 + y2) / 2, x2 - 12, (y1 + y2) / 2, fill="#f7bf3f", width=2)
        self.create_world_text((x1 + x2) / 2, y1 - 12, label, fill="#b9ecff", font=("Microsoft YaHei", 8, "bold"))

    def draw_prop(self, prop: Prop) -> None:
        x1 = prop.x
        y1 = prop.y
        x2 = prop.x + prop.w
        y2 = prop.y + prop.h
        if prop.kind == "console":
            self.create_world_rectangle(x1, y1, x2, y2, fill="#1b2b42", outline="#9fdfff", width=2)
            self.create_world_rectangle(x1 + 15, y1 + 14, x2 - 15, y2 - 18, fill=prop.color, outline="#cff4ff")
            self.create_world_oval(x2 - 34, y2 - 30, x2 - 18, y2 - 14, fill="#ff6b6b", outline="")
            self.create_world_text((x1 + x2) / 2, y2 - 12, prop.label, fill="#eaffff", font=("Arial", 10, "bold"))
        elif prop.kind == "table":
            self.create_world_rectangle(x1 + 14, y1 + 22, x2 - 14, y2 + 18, fill="#2a1b12", outline="")
            self.create_world_oval(x1, y1, x2, y2, fill=prop.color, outline="#4a2d18", width=3)
            self.create_world_oval(x1 + 20, y1 + 16, x2 - 20, y2 - 18, fill="#f0c079", outline="#fff0c7", width=2)
        elif prop.kind == "crate":
            self.create_world_rectangle(x1, y1, x2, y2, fill=prop.color, outline="#3a2417", width=3)
            self.create_world_line(x1, y1, x2, y2, fill="#d2a36e", width=2)
            self.create_world_line(x2, y1, x1, y2, fill="#d2a36e", width=2)
        elif prop.kind == "plant":
            self.create_world_rectangle(x1 + prop.w * 0.32, y1 + prop.h * 0.62, x2 - prop.w * 0.32, y2, fill="#9b5a35", outline="#5f321d")
            self.create_world_oval(x1, y1 + 15, x2, y1 + prop.h * 0.72, fill=prop.color, outline="#1f6f3a")
            self.create_world_oval(x1 + 24, y1, x2 + 22, y1 + prop.h * 0.62, fill="#7ed957", outline="#236b39")
        elif prop.kind == "round_table":
            self.create_world_oval(x1, y1, x2, y2, fill="#5b3f25", outline="#2b1b12", width=3)
            self.create_world_oval(x1 + 14, y1 + 10, x2 - 14, y2 - 18, fill=prop.color, outline="#ffe0a0", width=2)
        elif prop.kind == "bed":
            self.create_world_rectangle(x1, y1, x2, y2, fill="#315074", outline="#c3e8ff", width=3)
            self.create_world_rectangle(x1 + 16, y1 + 12, x1 + 70, y2 - 12, fill="#f5fbff", outline="")
            self.create_world_rectangle(x1 + 75, y1 + 12, x2 - 14, y2 - 12, fill=prop.color, outline="")
        elif prop.kind == "reactor":
            glow = 8 + (self.tick % 35)
            self.create_world_oval(x1 - glow, y1 - glow, x2 + glow, y2 + glow, fill="#4a3472", outline="")
            self.create_world_oval(x1, y1, x2, y2, fill="#2b2352", outline="#d5cfff", width=4)
            self.create_world_oval(x1 + 55, y1 + 35, x2 - 55, y2 - 35, fill=prop.color, outline="#f3edff", width=3)
        elif prop.kind == "gift":
            self.create_world_rectangle(x1, y1, x2, y2, fill=prop.color, outline="#fff0c7", width=3)
            self.create_world_rectangle(x1 + prop.w * 0.42, y1, x1 + prop.w * 0.58, y2, fill=GOLD_COLOR, outline="")
            self.create_world_rectangle(x1, y1 + prop.h * 0.42, x2, y1 + prop.h * 0.58, fill=GOLD_COLOR, outline="")
        elif prop.kind == "sofa":
            self.create_world_rectangle(x1, y1 + 28, x2, y2, fill="#6e3551", outline="#2a1420", width=3)
            self.create_world_rectangle(x1 + 20, y1, x2 - 20, y1 + 70, fill=prop.color, outline="#ffd4c6", width=2)

    def draw_geese(self) -> None:
        for duck in sorted(self.geese, key=lambda item: item.y):
            if duck.defeated:
                self.draw_chicken_leg(duck.x, duck.y)
                continue

            distance = duck.distance_to(self.player.x, self.player.y)
            if distance <= DISCOVER_RADIUS:
                label = "!" if distance <= ATTACK_RADIUS else "?"
                self.draw_duck(duck.x, duck.y, label, highlight=distance <= ATTACK_RADIUS)

    def draw_player(self) -> None:
        self.draw_player_goose(self.player.x, self.player.y, self.player.facing)
        sx, sy = self.world_to_screen(self.player.x, self.player.y)
        radius = ATTACK_RADIUS
        self.canvas.create_oval(
            sx - radius,
            sy - radius,
            sx + radius,
            sy + radius,
            outline="#fff0a8",
            width=2,
            dash=(5, 7),
        )

    def draw_player_goose(self, x: float, y: float, facing: str) -> None:
        sx, sy = self.world_to_screen(x, y)
        bob = math.sin(self.tick / 9) * 2
        flip = -1 if facing == "left" else 1
        outline = "#2d2518"

        self.canvas.create_oval(sx - 46, sy + 24, sx + 50, sy + 48, fill="#07101a", outline="")
        self.canvas.create_oval(sx - 42, sy - 12 + bob, sx + 34, sy + 40 + bob, fill=PLAYER_COLOR, outline=outline, width=3)
        self.canvas.create_polygon(
            sx - 6 * flip,
            sy - 8 + bob,
            sx + 11 * flip,
            sy - 62 + bob,
            sx + 36 * flip,
            sy - 58 + bob,
            sx + 18 * flip,
            sy - 2 + bob,
            fill=PLAYER_COLOR,
            outline=outline,
        )
        head_x1, head_x2 = sorted((sx + 13 * flip, sx + 58 * flip))
        wing_x1, wing_x2 = sorted((sx - 9 * flip, sx - 37 * flip))
        eye_x1, eye_x2 = sorted((sx + 30 * flip, sx + 38 * flip))
        self.canvas.create_oval(head_x1, sy - 82 + bob, head_x2, sy - 45 + bob, fill=PLAYER_COLOR, outline=outline, width=3)
        self.canvas.create_oval(wing_x1, sy + 0 + bob, wing_x2, sy + 28 + bob, fill="#e7dec8", outline=outline, width=2)
        self.canvas.create_oval(eye_x1, sy - 71 + bob, eye_x2, sy - 63 + bob, fill="#151515", outline="")
        self.canvas.create_polygon(
            sx + 55 * flip,
            sy - 68 + bob,
            sx + 82 * flip,
            sy - 60 + bob,
            sx + 55 * flip,
            sy - 52 + bob,
            fill="#f0a13a",
            outline="#8a4b12",
        )
        self.canvas.create_line(sx - 16, sy + 34 + bob, sx - 29, sy + 52 + bob, fill="#f0a13a", width=4)
        self.canvas.create_line(sx + 14, sy + 34 + bob, sx + 27, sy + 52 + bob, fill="#f0a13a", width=4)
        self.canvas.create_polygon(sx - 22, sy - 20 + bob, sx - 43, sy - 5 + bob, sx - 24, sy + 2 + bob, fill="#d34d4d", outline="#772828")
        self.canvas.create_oval(sx - 40, sy - 112 + bob, sx + 46, sy - 89 + bob, fill="#111d31", outline="#f5d66f", width=2)
        self.canvas.create_text(sx, sy - 101 + bob, text="你", fill=TEXT_COLOR, font=("Arial", 15, "bold"))

    def draw_duck(self, x: float, y: float, label: str, highlight: bool) -> None:
        sx, sy = self.world_to_screen(x, y)
        bob = math.sin(self.tick / 10) * 2
        body_color = HIGHLIGHT_COLOR if highlight else DUCK_COLOR
        outline = "#3a2b18"

        self.canvas.create_oval(sx - 36, sy + 18, sx + 40, sy + 40, fill="#07101a", outline="")
        self.canvas.create_oval(sx - 34, sy - 18 + bob, sx + 34, sy + 34 + bob, fill=body_color, outline=outline, width=3)
        self.canvas.create_oval(sx + 2, sy - 56 + bob, sx + 45, sy - 18 + bob, fill=DUCK_HEAD_COLOR, outline=outline, width=3)
        self.canvas.create_oval(sx - 24, sy - 5 + bob, sx + 12, sy + 22 + bob, fill="#e6b33d", outline=outline, width=2)
        self.canvas.create_oval(sx + 28, sy - 46 + bob, sx + 35, sy - 39 + bob, fill="#141414", outline="")
        self.canvas.create_polygon(sx + 42, sy - 38 + bob, sx + 66, sy - 31 + bob, sx + 42, sy - 24 + bob, fill="#f0a13a", outline="#8a4b12")
        self.canvas.create_line(sx - 13, sy + 28 + bob, sx - 23, sy + 44 + bob, fill="#f0a13a", width=4)
        self.canvas.create_line(sx + 12, sy + 29 + bob, sx + 22, sy + 44 + bob, fill="#f0a13a", width=4)
        self.canvas.create_oval(sx - 44, sy - 78 + bob, sx + 44, sy - 55 + bob, fill="#111d31", outline="#f5d66f", width=2)
        self.canvas.create_text(sx, sy - 67 + bob, text=label, fill=TEXT_COLOR, font=("Arial", 15, "bold"))

    def draw_chicken_leg(self, x: float, y: float) -> None:
        sx, sy = self.world_to_screen(x, y)
        self.canvas.create_oval(sx - 42, sy + 18, sx + 42, sy + 39, fill="#07101a", outline="")
        self.canvas.create_oval(sx - 31, sy - 12, sx + 18, sy + 29, fill="#c8752f", outline="#5a2b16", width=3)
        self.canvas.create_oval(sx - 22, sy - 4, sx + 8, sy + 20, fill="#e49a45", outline="")
        self.canvas.create_line(sx + 12, sy + 18, sx + 44, sy + 42, fill="#f4e7ca", width=12)
        self.canvas.create_oval(sx + 38, sy + 33, sx + 58, sy + 51, fill="#f4e7ca", outline="#9d8c73", width=2)
        self.canvas.create_oval(sx + 48, sy + 22, sx + 66, sy + 40, fill="#f4e7ca", outline="#9d8c73", width=2)

    def draw_atmosphere(self) -> None:
        self.canvas.create_rectangle(0, 86, WINDOW_WIDTH, 120, fill="#07111f", outline="", stipple="gray25")
        self.canvas.create_rectangle(0, WINDOW_HEIGHT - 46, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#050b16", outline="", stipple="gray25")
        self.canvas.create_rectangle(0, 0, 34, WINDOW_HEIGHT, fill="#050b16", outline="", stipple="gray25")
        self.canvas.create_rectangle(WINDOW_WIDTH - 34, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#050b16", outline="", stipple="gray25")

    def draw_hud(self) -> None:
        remaining = sum(not goose.defeated for goose in self.geese)
        defeated = ENEMY_COUNT - remaining
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 86, fill="#07111f", outline="")
        self.canvas.create_rectangle(16, 14, 335, 72, fill="#13263d", outline="#6ca6d8", width=2)
        self.canvas.create_text(
            34,
            28,
            anchor="w",
            text=f"生日鹅鸭杀寻礼物  {defeated}/{ENEMY_COUNT}",
            fill=TEXT_COLOR,
            font=("Microsoft YaHei", 18, "bold"),
        )
        self.canvas.create_text(
            34,
            56,
            anchor="w",
            text="靠近出现 ! 的鸭子，再左键点击",
            fill="#a6d9ff",
            font=("Microsoft YaHei", 11),
        )
        self.canvas.create_rectangle(360, 14, WINDOW_WIDTH - 18, 72, fill="#172942", outline="#405f82", width=2)
        self.canvas.create_text(
            380,
            43,
            anchor="w",
            text=self.last_message,
            fill="#d8f3ff",
            font=("Microsoft YaHei", 14),
        )

    def create_world_polygon(self, *coords: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        screen_coords = [
            coord - camera_x if index % 2 == 0 else coord - camera_y
            for index, coord in enumerate(coords)
        ]
        self.canvas.create_polygon(*screen_coords, **kwargs)

    def create_world_rectangle(self, x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_rectangle(x1 - camera_x, y1 - camera_y, x2 - camera_x, y2 - camera_y, **kwargs)

    def create_world_oval(self, x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_oval(x1 - camera_x, y1 - camera_y, x2 - camera_x, y2 - camera_y, **kwargs)

    def create_world_line(self, x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_line(x1 - camera_x, y1 - camera_y, x2 - camera_x, y2 - camera_y, **kwargs)

    def create_world_text(self, x: float, y: float, text: str, **kwargs: object) -> None:
        sx, sy = self.world_to_screen(x, y)
        self.canvas.create_text(sx, sy, text=text, **kwargs)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    BirthdayGooseGame().run()
