import inspect
import os
from .paths import cwdPath

# os.path.dirname(os.path.abspath(__file__)
# uvx 执行 $HOME/.cache/uv/archive-v0/rdF1xxx/lib/pythonxxx/site-packages/flowjson/utils
# 项目中 安装执行 $HOME/fe/pyautogui-extend/.venv/lib/pythonxxx/site-packages/flowjson/utils
# 项目中 调试执行 $HOME/fe/pyautogui-extend/src/flowjson/utils


def printDebug(*args):
    frame = inspect.currentframe().f_back  # 获取上一层调用栈
    try:
        relativeFileName = os.path.relpath(frame.f_code.co_filename, cwdPath)
    except ValueError as e:
        # 计算相对路径时 两个路径处于不同的挂载点上 会报错（例如 wins上一个C盘一个D盘 Parallels中一个C盘一个\\Mac\Home）
        relativeFileName = frame.f_code.co_filename
    print(f"[{relativeFileName}:{frame.f_lineno}]", *args)
