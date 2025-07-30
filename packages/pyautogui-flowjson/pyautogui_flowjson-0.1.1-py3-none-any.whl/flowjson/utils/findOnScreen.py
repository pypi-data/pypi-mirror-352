import cv2  # OpenCV库，用于计算机视觉任务，如图像处理和特征检测
import numpy as np
import time
import os
import pyscreeze
import pyautogui
import asyncio
from concurrent.futures import ThreadPoolExecutor  # 类似 web worker
from functools import partial
from .executor import executor
from .img import bytesToImage, toBytes
from .paths import imagesDirPath
from .getAbsPath import getAbsPath
from .printDebug import printDebug

# pyscreeze0.1.19+ 默认值为 True 导致pyautogui.locateOnScreen找不到图片直接抛错 [参考](https://blog.csdn.net/2402_84238572/article/details/142457302)
# pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False

# 捕获 屏幕截图
screenshot = pyautogui.screenshot()
# 保存 屏幕截图
# screenshot.save(os.path.join(imagesDirPath, f"screenshot_{int(time.time() * 1000)}.png"))
# 获取 分辨率
screenWidth, screenHeight = pyautogui.size()
# 获取dpi Mac Retina显示屏适配 [参考](https://www.codeleading.com/article/91556513765/)
dpi = int(screenshot.size[0] / screenWidth)


async def findOnScreen(
    targetImage: str, confidence=0.95, executor=executor, isDebug=False, retryCount=0
):
    """
    在屏幕中查询图片的位置并点击其中心
    """
    image = await bytesToImage(await toBytes(targetImage))
    # 获取当前正在运行的事件循环
    loop = asyncio.get_running_loop()
    # 使用partial 相当于js中的 bind 预制参数
    bindLocateOnScreen = partial(
        pyautogui.locateOnScreen,  # 这一定是 同步方法
        image,
        grayscale=True,
        confidence=confidence,
    )
    # 使用共享的 executor 并发执行 定位操作
    locationFuture = loop.run_in_executor(executor, bindLocateOnScreen)
    try:
        # 等待 当前
        location = await locationFuture
    except Exception as err:
        isDebug and printDebug("err", err)
        location = None
    if location is None:
        if retryCount > 0:
            return None
        # Mac dpi=2 缩小50% 重试 优化体验
        return await findOnScreen(
            image.resize((image.size[0] // 2, image.size[1] // 2)),
            confidence,
            executor,
            isDebug,
            retryCount + 1,
        )
    # 计算中心点坐标
    centerX, centerY = pyautogui.center(location)
    return (centerX / dpi, centerY / dpi)

    # 直接同步使用OpenCV
    # # 读取目标图像并转换为灰度图，以便进行模板匹配
    # target = cv2.imread(targetImagePath, cv2.IMREAD_GRAYSCALE)
    # # 将截图转换为NumPy数组，并使用OpenCV将其从RGB颜色空间转换为灰度图
    # screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    # # 在截屏中寻找目标图像的位置。matchTemplate方法会在截屏上滑动模板图像，并返回一个匹配结果矩阵
    # result = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    # # minMaxLoc 找到匹配结果中的最小值和最大值及其位置，这里关注的是最大值位置，因为它表示最匹配的地方。
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # # 如果最大匹配值大于设定的阈值（这里是 confidence），则认为找到了目标图像，返回其在屏幕上的中心坐标；否则返回None表示未找到。
    # if max_val > confidence:  # 设定匹配阈值
    #     x = (max_loc[0] + target.shape[1] // 2) / dpi
    #     y = (max_loc[1] + target.shape[0] // 2) / dpi
    #     return (
    #         x,
    #         y,
    #     )
    # return None
