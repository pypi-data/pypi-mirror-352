from flowjson.utils.screenshot import getScreenshot
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware


async def fun(arg):
    res = await getScreenshot()
    return {
        "msg": "操作成功",
        "res": res,
    }


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("screenshot", fun).run()
