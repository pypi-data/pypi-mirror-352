import argparse
import asyncio
import base64
import json
import os
import io
import aiofiles
import aiohttp
import json5
import pyautogui
import pyperclip
import platform
import time
import ddddocr
import pydash
from typing import Literal, Optional, Tuple, List, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from flowjson.utils.getAbsPath import getAbsPath
from flowjson.utils.img import (
    base64ToBytes,
    bytesToImage,
    getImgExt,
    toBase64,
    pathToBytes,
    toBytes,
    uriToBytes,
)
from flowjson.utils.imgEnsure import imgEnsure
from flowjson.utils.imgOcr import imgOcr
from flowjson.utils.index import execRun, findOnScreen, imagesDirPath, printDebug
from flowjson.utils.pointOperation import pointOperation
from flowjson.utils.screenshot import getScreenshot
from flowjson.utils.typewrite import typewrite
from flowjson.utils.vCode import vCodeClickType, vCodeFillType, vCodeScrollType
from flowjson.utils.formatOcrTextWithLayout import formatOcrTextWithLayout
from paddleocr import PaddleOCR
from PIL import Image


async def bootstrap():
    # confidence 取值 预期是 选中能识别 未选中 不能识别
    # confidence = 0.99
    # [res1, res2, res3] = await asyncio.gather(
    #     *[
    #         # n 选中
    #         findOnScreen(
    #             os.path.join(imagesDirPath, "dmr/ck/job2/7-1-n-selected-include.png"),
    #             confidence=confidence,
    #         ),
    #         # n 未选中
    #         findOnScreen(
    #             os.path.join(imagesDirPath, "dmr/ck/job2/3-1-n-unselected-click.png"),
    #             confidence=confidence,
    #         ),
    #         # 模糊 能匹配
    #         findOnScreen(
    #             os.path.join(
    #                 imagesDirPath, "dmr/ck/job2/6-1-breakdown-prompt-click.png"
    #             ),
    #             confidence=0.8,
    #         ),
    #     ]
    # )
    # printDebug(res1, res2, res3)
    # pyautogui.press("e")
    # pyautogui.press(keys="space")

    # pyautogui.typewrite(['a','b'], interval=0.25)  # 不支持中文直接输入 每个字符之间的间隔为0.25秒
    # 直接使用失效 仅会输出v 参考 https://github.com/asweigart/pyautogui/issues/796 https://github.com/asweigart/pyautogui/issues/687
    # pyperclip.copy("你好，世界！")
    # pyautogui.hotkey('ctrl', 'v') # Windows/Linux
    # 方法1
    # pyautogui.keyUp('fn')
    # pyautogui.hotkey('command', 'v') # macOS
    # 方法2
    # with pyautogui.hold(['command']):
    #     pyautogui.press('v')
    # 方法3
    # pyautogui.hotkey("command")
    # pyautogui.hotkey("command", "v")

    # 将鼠标移动到初始位置(例如屏幕的(100, 100)位置)
    # pyautogui.clcik(1178, 570)

    # 按下鼠标左键(开始拖拽)
    # pyautogui.mouseDown(1178, 582)
    # pyautogui.mouseUp(1331, 582)
    # 将鼠标拖拽到新位置(例如屏幕的(300, 300)位置)
    # pyautogui.dragTo(300, 300, duration=0.5)
    # # 释放鼠标左键(结束拖拽)
    # pyautogui.mouseUp()

    # 验证码分类
    # print(
    #     # 英文数字（填充类）验证码 得到文本
    #     # 54G6
    #     await vCodeFillType(
    #         getAbsPath('src/common/images/vcode/1-tc-code.png')
    #     ),
    #     # 中文（点选类）验证码 得到坐标
    #     # {'学': (339.5, 212.5), '商': (426.5, 183.0), '师': (551.0, 216.5), '走': (58.5, 145.5), '爱': (215.5, 200.5), 'C': (741.0, 35.0)}
    #     await vCodeClickType(
    #         getAbsPath('src/common/images/vcode/2-dj-code.png')
    #     ),
    #     # 滑块（滑动类）验证码 得到坐标
    #     await vCodeScrollType(
    #         getAbsPath('src/common/images/vcode/3-hk-code-target.png'),
    #         getAbsPath('src/common/images/vcode/3-hk-code-background.png')
    #     )
    # )

    # # 转换测试
    # # s = "/Users/bytedance/fe/pyautogui-extend/src/common/images/vcode/1-tc-code.png"
    # # s = "https://img.picui.cn/free/2025/05/19/682ae7b926f48.png"
    # s = await toBase64('/Users/bytedance/fe/pyautogui-extend/src/common/images/vcode/1-tc-code.png')
    # # 54G6
    # print(await vCodeFillType(
    #     await toBytes(
    #        s
    #     )
    # ))
    # print(await getImgExt(s))

    # print(await findOnScreen(
    #     await bytesToImage(
    #         await toBytes(getAbsPath("src/common/images/tdd/docker-icon.png"))
    #     )
    # ))

    print(
        json.dumps(
            {"type": "pointOperation:next", "imageRes": 1},
            ensure_ascii=False,
            # 完全无空格
            separators=(",", ":"),
        )
    )
    return


def main():
    startTime = int(time.time() * 1000)
    # 运行异步函数 它自己本身是同步的
    asyncio.run(bootstrap())
    printDebug(f"整体任务耗时：{int(time.time() * 1000) - startTime} ms")


main()
