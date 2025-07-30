import pyautogui
import os
import tempfile
from datetime import datetime


async def getScreenshot():
    # 捕获屏幕截图
    screenshot = pyautogui.screenshot()
    # 生成临时文件名，格式：2024-03-21-14-30-22
    filename = f"screenshot_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
    # 获取系统临时目录并保存
    filepath = os.path.join(tempfile.gettempdir(), filename)
    screenshot.save(filepath, format="png")
    return filepath
