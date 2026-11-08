# 自动测试

都是 Python + Playwright 脚本，直接打开上一级目录的 `index.html`，截图输出到 `tests/out/`。

```bash
pip install playwright
playwright install chromium        # 或者用系统 Chrome：export CHROME=/usr/bin/google-chrome
python3 tests/jumps.py             # 逐个跳转 DEV 节点，检查场景和存档，报错就打印
```

| 脚本 | 做什么 |
|---|---|
| `sim.py 速度 质量下限` | 机器人连玩 50 天，每天打印收入、服务数、走单、存款、房租是否交上。例：熟练 `8.5 0.8`、普通 `11 0.65`、新手 `14 0.5` |
| `tut.py 天数 [订单]` | 按游戏里的提示一步步操作，检查教学能不能走通。例：`tut.py 1`、`tut.py 20` |
| `jumps.py` | 跳转所有 DEV 节点 |
| `boss.py` | 第 50 天 BOSS 战从开始到打烊 |
| `run50.py` | 从第 1 天跳过到第 56 天，覆盖所有场景 |
| `small.py` | 375×667 和 360×640 小屏截图 |
| `fpsq.py` | 三档画质的帧率 |

脚本会调用游戏里的全局函数（`devJump`、`startPlay`、`serve` 等），改了这些函数名要同步更新。
