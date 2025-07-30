# RequestHandlerMiddleware 必须在第一行 否则解析会报错 Error: ModuleNotFoundError: No module named 'utils.RequestHandlerMiddleware'
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware
from flowjson.utils.imgOcr import imgOcr


async def fun(arg):
    res = await imgOcr(**arg)
    return {
        "msg": "操作成功 ocr 文本内容",
        "res": " ".join(res),
    }


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("img-ocr", fun).run()
