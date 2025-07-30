import asyncio
import os
import pyautogui
import pydash
from typing import Optional, TypedDict
from .executor import executor
from .formatArgument import toArr
from .findOnScreen import findOnScreen
from .getAbsPath import getAbsPath
from .paths import imagesDirPath
from ..types.workflows import Action, Image, Shot


async def analyzeShot(
    shot: Optional[Shot],
    executor=executor,
    imagesDirPath=imagesDirPath,
    isDebug=False,
):
    if shot is None:
        return await asyncio.sleep(0)
    URI_KEY = "uri"
    # 统一格式
    screenShot = {URI_KEY: shot} if isinstance(shot, str) else shot
    otherArg = {k: v for k, v in screenShot.items() if k != URI_KEY}
    # 尝试 相对路径 => 绝对路径 失败则使用原有值（uri | base64）
    targetImagePath = getAbsPath(pydash.get(screenShot, URI_KEY), imagesDirPath)
    targetImage = (
        targetImagePath
        if os.path.exists(targetImagePath)
        else pydash.get(screenShot, URI_KEY)
    )
    return await findOnScreen(
        targetImage=targetImage,
        **otherArg,
        executor=executor,
        isDebug=isDebug,
    )


async def analyzeImage(
    image: Optional[Image],
    executor=executor,
    imagesDirPath=imagesDirPath,
    isDebug=False,
):
    if image is None:
        return {"isPass": True}
    (positionRes, includesRes, excludesRes) = await asyncio.gather(
        (
            analyzeShot(
                pydash.get(image, "position"),
                executor=executor,
                imagesDirPath=imagesDirPath,
                isDebug=isDebug,
            )
        ),
        (
            asyncio.gather(
                # 展开
                *[
                    # 列表推导式
                    analyzeShot(
                        v,
                        executor=executor,
                        imagesDirPath=imagesDirPath,
                        isDebug=isDebug,
                    )
                    # 通用转换为数组
                    for v in toArr(pydash.get(image, "includes"))
                ]
            )
        ),
        (
            asyncio.gather(
                *[
                    analyzeShot(
                        v,
                        executor=executor,
                        imagesDirPath=imagesDirPath,
                        isDebug=isDebug,
                    )
                    for v in toArr(pydash.get(image, "excludes"))
                ]
            )
        ),
    )
    # 给了 position 的值 就应该解析出坐标
    positionPass = (
        (positionRes is not None) if pydash.get(image, "position") is not None else True
    )
    includesPass = all(v is not None for v in includesRes)
    excludesPass = all(v is None for v in excludesRes)
    return {
        "position": positionRes,
        "includes": includesRes,
        "excludes": excludesRes,
        "isPass": positionPass and includesPass and excludesPass,
    }


class PointOperationOpt(Image, TypedDict):
    action: Optional[Action]


async def pointOperation(arg: PointOperationOpt, isDebug=False):
    ACTION_KEY = "action"
    otherArg = {k: v for k, v in arg.items() if k != ACTION_KEY}
    imageRes = await analyzeImage(image=otherArg, isDebug=isDebug)
    if (
        pydash.get(imageRes, "isPass") == False
        or pydash.get(imageRes, "isPass") == None
    ):
        return imageRes
    pyautoguiActionFn = getattr(pyautogui, pydash.get(arg, "action.type"))
    (x, y) = (
        (None, None)
        if pydash.get(imageRes, "position") is None
        else (
            pydash.get(imageRes, "position[0]"),
            pydash.get(imageRes, "position[1]"),
        )
    )
    xyArguments = {"x": x, "y": y} if all(v is not None for v in (x, y)) else {}
    actionArguments: dict | list = pydash.get(arg, "action.arguments", {})
    # pyautogui.move(xOffset=0, yOffset=-100) 参数非 xy 一般不需要兼容
    (
        # 确保 actionArguments 会覆盖 xyArguments
        pyautoguiActionFn(**{**xyArguments, **actionArguments})
        if isinstance(actionArguments, dict)
        else pyautoguiActionFn(*actionArguments, **xyArguments)
    )
