import asyncio
from typing import Callable
from utils.jsPy import getJsEnvArg, pyToJsArg
from utils.log import logger


class RequestHandlerMiddleware:
    # 构造函数: 在Python中，类的构造函数是通过__init__方法定义的；而在TypeScript中，则是使用constructor关键字。
    # 不同的是，在Python中你需要显式地包含self作为第一个参数来引用实例本身，而TypeScript则通过this关键字隐式引用
    def __init__(self, toolName: str, toolFunction: Callable):
        self.toolName = toolName
        self.toolFunction = toolFunction

    async def bootstrap(self):
        try:
            arg = await getJsEnvArg()
            logger.info({"type": f"{self.toolName}:pre", "arg": arg})
            res = await self.toolFunction(arg)
            logger.info({"type": f"{self.toolName}:next", "res": res})
            return await pyToJsArg(res)
        except Exception as e:
            logger.error({"type": f"{self.toolName}:next", "err": str(e)})
            return await pyToJsArg(
                {
                    "msg": "操作失败",
                    "err": str(e),
                }
            )

    def run(self):
        # 运行异步函数 它自己本身是同步的
        asyncio.run(self.bootstrap())
