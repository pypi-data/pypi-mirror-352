from flowjson.utils.imgEnsure import imgEnsure
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware


async def fun(arg):
    res = await imgEnsure(arg)
    return {
        "msg": "操作成功 检测到图片存在 点位信息",
        "res": res,
    }


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("img-ensure", fun).run()
