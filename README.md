# 生日鹅鸭杀寻礼物

这是一个用 Python 标准库 `tkinter` 做的生日小游戏：玩家控制一只鹅在大地图里探索，找到藏起来的 10 只鹅并点击“砍倒”，每次会弹出一个 1-10 的礼物编号，方便你在现实中拿出对应礼物。

## 运行方式

```bash
python birthday_goose_hunt.py
```

## 玩法

- 用 `WASD` 或方向键移动玩家鹅。
- 靠近藏起来的鹅时，地图上会显示 `?`；进入可点击范围后会显示 `!`。
- 鼠标左键点击显示 `!` 的鹅，会弹出礼物编号。
- 找齐 10 只鹅后，游戏会显示通关祝福。

## 个性化修改

你可以直接编辑 `birthday_goose_hunt.py`：

- 修改 `ENEMY_COUNT` 和 `make_hidden_geese()` 中的位置来调整礼物数量和藏鹅位置。
- 修改 `WINDOW_WIDTH`、`WINDOW_HEIGHT`、`WORLD_WIDTH`、`WORLD_HEIGHT` 来调整窗口和地图大小。
- 修改 `messagebox.showinfo()` 中的文字，加入你们之间的昵称、梗或生日祝福。
