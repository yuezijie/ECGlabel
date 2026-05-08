"""生日鹅鸭杀寻礼小游戏。

运行：
    python birthday_goose_hunt.py

玩法：WASD 控制白鹅在大地图探索；靠近藏起来的鹅后，鼠标左键点击它；
被“砍倒”的鹅会弹出 1-10 的礼物编号。全部找到后游戏结束。
"""

from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
WORLD_WIDTH = 2600
WORLD_HEIGHT = 1800
PLAYER_SPEED = 7
DISCOVER_RADIUS = 230
ATTACK_RADIUS = 105
ENEMY_COUNT = 10

BG_COLOR = "#17324d"
GRID_COLOR = "#244a6a"
POND_COLOR = "#1f7aa8"
GRASS_COLOR = "#2f7a3e"
PATH_COLOR = "#8a6b3f"
PLAYER_COLOR = "#fff7df"
ENEMY_COLOR = "#f8f1d5"
DEFEATED_COLOR = "#9b4c4c"
HIGHLIGHT_COLOR = "#ffd35a"
TEXT_COLOR = "#fff4c7"


@dataclass
class Goose:
    """地图上的鹅。"""

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


def clamp(value: float, minimum: float, maximum: float) -> float:
    """把数值限制在给定范围内。"""

    return max(minimum, min(value, maximum))


def make_hidden_geese(seed: int | None = 20260508) -> list[Goose]:
    """生成 10 只藏在地图边角和偏僻区域的鹅。"""

    rng = random.Random(seed)
    gift_numbers = list(range(1, ENEMY_COUNT + 1))
    rng.shuffle(gift_numbers)

    hiding_spots = [
        (180, 170),
        (WORLD_WIDTH - 180, 170),
        (180, WORLD_HEIGHT - 170),
        (WORLD_WIDTH - 180, WORLD_HEIGHT - 170),
        (520, 260),
        (WORLD_WIDTH - 560, 340),
        (430, WORLD_HEIGHT - 430),
        (WORLD_WIDTH - 460, WORLD_HEIGHT - 390),
        (WORLD_WIDTH / 2 - 420, WORLD_HEIGHT / 2 + 360),
        (WORLD_WIDTH / 2 + 520, WORLD_HEIGHT / 2 - 310),
    ]

    geese: list[Goose] = []
    for index, (x, y) in enumerate(hiding_spots):
        geese.append(
            Goose(
                x=clamp(x + rng.randint(-75, 75), 80, WORLD_WIDTH - 80),
                y=clamp(y + rng.randint(-75, 75), 80, WORLD_HEIGHT - 80),
                gift_number=gift_numbers[index],
            )
        )
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
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.player = Player()
        self.geese = make_hidden_geese()
        self.keys: set[str] = set()
        self.game_over = False
        self.last_message = "WASD 探索地图，靠近藏鹅后用鼠标左键点击。"

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

        self.player.x = clamp(self.player.x + dx * PLAYER_SPEED, 35, WORLD_WIDTH - 35)
        self.player.y = clamp(self.player.y + dy * PLAYER_SPEED, 35, WORLD_HEIGHT - 35)

    def on_click(self, event: tk.Event) -> None:
        if self.game_over:
            return

        world_x, world_y = self.screen_to_world(event.x, event.y)
        target = self.pick_target(world_x, world_y)
        if target is None:
            self.last_message = "再靠近一点，或者点准藏起来的鹅！"
            return

        target.defeated = True
        remaining = sum(not goose.defeated for goose in self.geese)
        self.last_message = f"获得礼物编号 {target.gift_number}！还剩 {remaining} 只鹅。"
        messagebox.showinfo("礼物时间", f"你砍倒了一只鹅！请拿出 {target.gift_number} 号礼物。")

        if remaining == 0:
            self.finish_game()

    def pick_target(self, world_x: float, world_y: float) -> Goose | None:
        candidates = []
        for goose in self.geese:
            if goose.defeated:
                continue
            close_to_player = goose.distance_to(self.player.x, self.player.y) <= ATTACK_RADIUS
            clicked_goose = goose.distance_to(world_x, world_y) <= 45
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
        self.draw()
        self.root.after(16, self.game_loop)

    def draw(self) -> None:
        self.canvas.delete("all")
        camera_x, camera_y = self.camera()
        self.draw_map(camera_x, camera_y)
        self.draw_geese()
        self.draw_player()
        self.draw_hud()

    def draw_map(self, camera_x: float, camera_y: float) -> None:
        for x in range(0, WORLD_WIDTH + 1, 120):
            sx = x - camera_x
            self.canvas.create_line(sx, -camera_y, sx, WORLD_HEIGHT - camera_y, fill=GRID_COLOR)
        for y in range(0, WORLD_HEIGHT + 1, 120):
            sy = y - camera_y
            self.canvas.create_line(-camera_x, sy, WORLD_WIDTH - camera_x, sy, fill=GRID_COLOR)

        self.create_world_oval(860, 580, 1420, 920, fill=POND_COLOR, outline="#76c8e8", width=3)
        self.create_world_oval(1960, 1040, 2380, 1390, fill=POND_COLOR, outline="#76c8e8", width=3)
        self.create_world_rectangle(250, 740, 880, 930, fill=PATH_COLOR, outline="")
        self.create_world_rectangle(1120, 1320, 2050, 1490, fill=PATH_COLOR, outline="")
        self.create_world_oval(122, 1020, 560, 1510, fill=GRASS_COLOR, outline="")
        self.create_world_oval(1830, 150, 2440, 560, fill=GRASS_COLOR, outline="")

    def draw_geese(self) -> None:
        for goose in self.geese:
            if goose.defeated:
                self.draw_goose(goose.x, goose.y, DEFEATED_COLOR, "×")
                continue

            distance = goose.distance_to(self.player.x, self.player.y)
            if distance <= DISCOVER_RADIUS:
                label = "!" if distance <= ATTACK_RADIUS else "?"
                color = HIGHLIGHT_COLOR if distance <= ATTACK_RADIUS else ENEMY_COLOR
                self.draw_goose(goose.x, goose.y, color, label)

    def draw_player(self) -> None:
        self.draw_goose(self.player.x, self.player.y, PLAYER_COLOR, "你")
        sx, sy = self.world_to_screen(self.player.x, self.player.y)
        radius = ATTACK_RADIUS
        self.canvas.create_oval(
            sx - radius,
            sy - radius,
            sx + radius,
            sy + radius,
            outline="#fff0a8",
            dash=(4, 6),
        )

    def draw_goose(self, x: float, y: float, color: str, label: str) -> None:
        sx, sy = self.world_to_screen(x, y)
        self.canvas.create_oval(sx - 24, sy - 18, sx + 25, sy + 18, fill=color, outline="#3b2c1a", width=2)
        self.canvas.create_oval(sx + 12, sy - 35, sx + 39, sy - 11, fill=color, outline="#3b2c1a", width=2)
        self.canvas.create_polygon(sx + 38, sy - 26, sx + 58, sy - 20, sx + 38, sy - 14, fill="#f2a23a", outline="#8a4b12")
        self.canvas.create_line(sx - 8, sy + 17, sx - 16, sy + 32, fill="#f2a23a", width=3)
        self.canvas.create_line(sx + 12, sy + 17, sx + 21, sy + 32, fill="#f2a23a", width=3)
        self.canvas.create_text(sx, sy + 50, text=label, fill=TEXT_COLOR, font=("Arial", 16, "bold"))

    def draw_hud(self) -> None:
        remaining = sum(not goose.defeated for goose in self.geese)
        defeated = ENEMY_COUNT - remaining
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 74, fill="#081a2a", outline="")
        self.canvas.create_text(
            18,
            18,
            anchor="w",
            text=f"生日鹅鸭杀寻礼物  |  已找到 {defeated}/{ENEMY_COUNT}",
            fill=TEXT_COLOR,
            font=("Microsoft YaHei", 18, "bold"),
        )
        self.canvas.create_text(
            18,
            50,
            anchor="w",
            text=self.last_message,
            fill="#d8f3ff",
            font=("Microsoft YaHei", 13),
        )
        self.canvas.create_text(
            WINDOW_WIDTH - 18,
            50,
            anchor="e",
            text="提示：靠近出现 ! 的鹅，然后左键点击",
            fill="#a6d9ff",
            font=("Microsoft YaHei", 12),
        )

    def create_world_oval(self, x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_oval(x1 - camera_x, y1 - camera_y, x2 - camera_x, y2 - camera_y, **kwargs)

    def create_world_rectangle(self, x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> None:
        camera_x, camera_y = self.camera()
        self.canvas.create_rectangle(x1 - camera_x, y1 - camera_y, x2 - camera_x, y2 - camera_y, **kwargs)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    BirthdayGooseGame().run()
