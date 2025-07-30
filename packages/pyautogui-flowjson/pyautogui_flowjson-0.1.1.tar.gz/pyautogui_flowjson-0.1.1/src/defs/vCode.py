import pydash
from flowjson.utils.vCode import vCodeClickType, vCodeFillType, vCodeScrollType
from utils.RequestHandlerMiddleware import RequestHandlerMiddleware


async def fun(arg):
    # 与 js 不同的是 不需要 break; “穿透”行为
    match pydash.get(arg, "type"):
        case "fill":
            res = await vCodeFillType(pydash.get(arg, "source"))
        case "click":
            res = await vCodeClickType(pydash.get(arg, "source"))
        case "scroll":
            res = await vCodeScrollType(
                targetSource=pydash.get(arg, "source"),
                backgroundSource=pydash.get(arg, "backgroundSource"),
                simple_target=pydash.get(arg, "simple_target"),
            )
        case _:
            return {
                "msg": "操作失败",
                "err": "未知的验证码类型",
            }
    return {
        "msg": "操作成功",
        "res": res,
    }


# 直接运行脚本的方式 而非包的调用
if __name__ == "__main__":
    RequestHandlerMiddleware("verification-code", fun).run()
