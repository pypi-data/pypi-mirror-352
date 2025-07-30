import argparse  # 类似 node commander
from concurrent.futures import ThreadPoolExecutor
import json
import os
import time
import platform
import asyncio
import json5
import pyautogui
import pyperclip
import pydash  # py中的lodash get方法 可解决可选链问题
from .utils.pointOperation import analyzeImage
from .utils.index import (
    jsonDirPath,
    imagesDirPath,
    printDebug,
    getAbsPath,
    findOnScreen,
    toArr,
    execRun,
    readFile,
)
from .types.index import Shot, Image, Condition, Job, FlowMode, Workflows
from pynput import keyboard
from typing import List, Optional


async def bootstrap():
    # 获取当前时间戳（秒）并转换为毫秒，然后向下取整 int() 函数在处理浮点数时会自动向下取整到最接近的整数。
    startTime = int(time.time() * 1000)

    parser = argparse.ArgumentParser(
        # TODO 读取 toml description
        description="Use json5 for view-based workflows configuration"
    )
    # 相对路径 基于cwd拼接
    parser.add_argument(
        "--workflowJsonAddress", type=str, required=True, help="WorkflowJson address"
    )
    parser.add_argument(
        "--jsonDirPath",
        type=str,
        required=False,
        default=jsonDirPath,
        help="json dir path",
    )
    parser.add_argument(
        "--imagesDirPath",
        type=str,
        required=False,
        default=imagesDirPath,
        help="images dir path",
    )
    parser.add_argument(
        "--findOnScreenMaxThread",
        type=int,
        required=False,
        default=6,
        help="findOnScreen Maximum number of concurrent threads in the thread pool",
    )
    # 使用 action='store_true' 来创建一个布尔标志。如果希望默认为 True 并且当用户提供时设为 False，可以使用 action='store_false'。
    parser.add_argument(
        "--isDebug", action="store_true", help="Whether to enable debug"
    )
    args = parser.parse_args()  # args 是 Namespace 类型的 使用 . 获取属性
    args.isDebug and printDebug(args)
    executor = ThreadPoolExecutor(max_workers=args.findOnScreenMaxThread)

    async def analyzeCondition(condition: Optional[Condition]):
        if condition is None:
            return {"isPass": True}
        imageRes = await analyzeImage(
            pydash.get(condition, "image"),
            executor=executor,
            imagesDirPath=args.imagesDirPath,
            isDebug=args.isDebug,
        )
        args.isDebug and printDebug(
            'pydash.get(condition, "image")', pydash.get(condition, "image")
        )
        args.isDebug and printDebug("imageRes", imageRes)
        if pydash.get(condition, "run") is None:
            return {
                "position": pydash.get(imageRes, "position"),
                "isPass": pydash.get(imageRes, "isPass"),
            }
        runRes = execRun(
            toArr(pydash.get(condition, "run")), space={**globals(), **locals()}
        )
        args.isDebug and printDebug("runRes", runRes)
        return {
            "position": pydash.get(imageRes, "position"),
            "isPass": runRes,
        }

    async def execJobs(jobs: Optional[List[Job]], flowMode: Optional[FlowMode] = None):
        jobs: List[Job] = toArr(jobs)
        if len(jobs) == 0:
            return
        if flowMode == FlowMode.parallel.value:
            await asyncio.gather(*[execJob(v) for v in jobs])
        else:
            for v in jobs:
                await execJob(v)

    async def execJob(job: Job):
        if pydash.get(job, "delay.pre") is not None:
            await asyncio.sleep(pydash.get(job, "delay.pre"))
        conditionRes = await analyzeCondition(pydash.get(job, "condition"))
        if pydash.get(conditionRes, "isPass"):
            if pydash.get(job, "action") is not None:

                match pydash.get(job, "action.type"):
                    case "paste":
                        # pyautogui typewrite 写不了中文
                        pyperclip.copy(pydash.get(job, "action.arguments[0]"))
                        pasteArguments = (
                            ["command", "v"]  # macOS
                            if platform.system() == "Darwin"
                            else ["ctrl", "v"]  # Windows | Linux
                        )
                        # 直接使用hotkey失效 仅会输出v 参考 https://github.com/asweigart/pyautogui/issues/796
                        pyautogui.keyUp("fn")
                        pyautogui.hotkey(*pasteArguments)
                    case _:
                        # 通过 getattr 动态调用方法 不能 pyautogui[job["action"]["type"]] 因为pyautogui是一个模块不是一个字典（字典是可以的）
                        pyautoguiActionFn = getattr(
                            pyautogui, pydash.get(job, "action.type")
                        )
                        (x, y) = (
                            (None, None)
                            if pydash.get(conditionRes, "position") is None
                            else (
                                pydash.get(conditionRes, "position[0]"),
                                pydash.get(conditionRes, "position[1]"),
                            )
                        )
                        xyArguments = (
                            {"x": x, "y": y}
                            if all(v is not None for v in (x, y))
                            else {}
                        )
                        actionArguments: dict | list = pydash.get(
                            job, "action.arguments", {}
                        )
                        # pyautogui.move(xOffset=0, yOffset=-100) 参数非 xy 一般不需要兼容
                        (
                            # 确保 actionArguments 会覆盖 xyArguments
                            pyautoguiActionFn(**{**xyArguments, **actionArguments})
                            if isinstance(actionArguments, dict)
                            else pyautoguiActionFn(*actionArguments, **xyArguments)
                        )

            # loop
            if pydash.get(job, "loop") is None:
                await execJobs(pydash.get(job, "jobs"), pydash.get(job, "flowMode"))
            else:
                loopIndex = 1  # 计数器
                loopMax = pydash.get(job, "loop.max", default=float("inf"))
                while loopIndex <= loopMax:
                    args.isDebug and printDebug(f"循环{loopIndex}次")
                    await execJobs(pydash.get(job, "jobs"), pydash.get(job, "flowMode"))
                    loopExitCondition = False
                    if pydash.get(job, "loop.exitCondition") is not None:
                        conditionRes = await analyzeCondition(
                            pydash.get(job, "loop.exitCondition")
                        )
                        loopExitCondition = pydash.get(conditionRes, "isPass")
                    if loopExitCondition:
                        break
                    loopIndex += 1

        if pydash.get(job, "delay.next") is not None:
            await asyncio.sleep(pydash.get(job, "delay.next"))

    async def execWorkflows(workflows: Workflows):
        if isinstance(workflows, dict):
            await execJob(workflows)
        elif isinstance(workflows, list):
            for job in workflows:
                if isinstance(job, dict):
                    await execJob(job)
                elif isinstance(job, list):
                    await execWorkflows(job)  # 递归

    # F11 F12 退出进程
    def on_press(key):
        args.isDebug and printDebug(f"按下 {key}")
        if key in [keyboard.Key.f11, keyboard.Key.f12]:
            os._exit(0)  # 强制退出程序

    # 设置一个键盘监听器，在另一个线程中运行
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    workflowsPath = getAbsPath(args.workflowJsonAddress, args.jsonDirPath)
    content = await readFile(workflowsPath)
    # 使用 json5 解析读取到的内容
    workflows: Workflows = json5.loads(content)

    args.isDebug and printDebug(
        json.dumps(
            workflows,
            ensure_ascii=False,
            indent=2,
            separators=(",", ":"),
        )
    )

    await execWorkflows(workflows)

    args.isDebug and printDebug(
        f"整体任务耗时：{int(time.time() * 1000) - startTime} ms"
    )


def main():
    # 运行异步函数 它自己本身是同步的
    asyncio.run(bootstrap())
