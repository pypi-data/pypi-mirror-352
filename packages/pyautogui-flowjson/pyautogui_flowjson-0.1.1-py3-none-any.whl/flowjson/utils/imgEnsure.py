import asyncio
import pydash
from typing import Optional, TypedDict
from ..types.workflows import Screenshot
from .findOnScreen import findOnScreen


class ImgEnsureOpt(Screenshot, TypedDict):
    timeout: Optional[float]


async def imgEnsure(arg: ImgEnsureOpt):

    async def task():
        while True:
            res = await findOnScreen(
                targetImage=pydash.get(arg, "uri"),
                confidence=pydash.get(arg, "confidence"),
            )
            if res is None:
                await asyncio.sleep(0.3)
            else:
                return res

    timeout = pydash.get(arg, "timeout", 30)
    try:
        result = await asyncio.wait_for(task(), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        raise Exception(f"操作失败，已经超过最大执行时间 {timeout} 秒")
