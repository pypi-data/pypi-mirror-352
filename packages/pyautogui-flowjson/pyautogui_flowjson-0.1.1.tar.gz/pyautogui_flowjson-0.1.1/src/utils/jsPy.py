import json
import os
from flowjson.utils.getAbsPath import getAbsPath
from flowjson.utils.pathResolve import pathResolve


absCwdpath = pathResolve(os.path.dirname(__file__), "../../")

# 打开文件并读取内容
with open(getAbsPath("package.json", absCwdpath), "r", encoding="utf-8") as file:
    pkg = json.load(file)


async def getJsEnvArg():
    """解析 js 的 env 参数"""
    # 获取环境变量中 特定 参数
    stringify = os.environ.get(pkg["jspy_identifier"])
    obj: dict = json.loads(stringify)
    return obj


async def pyToJsArg(arg: any):
    """
    py 将结果 传递给 js

    如果 不是通过 js 调用的py 仅会直接打印参数
    """
    # 非js调用py
    if os.environ.get("isNodeExec") is None:
        return print(
            json.dumps(
                arg,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    return print(
        json.dumps(
            {pkg["jspy_identifier"]: arg},
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
