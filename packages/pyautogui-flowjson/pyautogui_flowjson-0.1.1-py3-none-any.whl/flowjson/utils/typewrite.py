import asyncio
import platform
import re
import pyautogui
import pyperclip


async def typewrite(message: str | list[str], interval=0.0):

    # 使用正则表达式判断是否包含中文字符
    if isinstance(message, str) and bool(re.search(r"[\u4e00-\u9fff]", message)):
        # 先保存copy的内容
        preText = pyperclip.paste()
        pyperclip.copy(message)
        # 直接使用失效 仅会输出v 参考 https://github.com/asweigart/pyautogui/issues/796 https://github.com/asweigart/pyautogui/issues/687
        pyautogui.keyUp("fn")
        await asyncio.sleep(0)
        arr = ("command", "v") if platform.system() == "Darwin" else ("ctrl", "v")
        pyautogui.hotkey(*arr)
        pyperclip.copy(preText) # 恢复之前的内容
        return

    pyautogui.typewrite(message=message, interval=interval)
