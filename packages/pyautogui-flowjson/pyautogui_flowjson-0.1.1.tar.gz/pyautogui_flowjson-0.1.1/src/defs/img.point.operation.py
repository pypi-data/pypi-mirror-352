from flowjson.utils.pointOperation import pointOperation
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware


async def fun(arg):
    imageRes = await pointOperation(arg)
    if imageRes:
        return {
            "msg": "操作失败 图片整体查找验证不通过",
            "err": imageRes,
        }
    return "操作成功"


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("img-point-operation", fun).run()
