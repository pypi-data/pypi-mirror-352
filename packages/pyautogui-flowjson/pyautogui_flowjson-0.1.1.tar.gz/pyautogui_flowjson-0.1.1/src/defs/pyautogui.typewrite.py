from flowjson.utils.typewrite import typewrite
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware


async def fun(arg):
    await typewrite(**arg)
    return "操作成功"


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("typewrite", fun).run()
