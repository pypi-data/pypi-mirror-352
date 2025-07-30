from functools import reduce
from typing import Any, List, Mapping
import uuid


def execRun(
    run: List[str] = [],
    space: dict[str, Any] | None = None,
):
    """执行run获取结果
    def add(a, b):
        return a + b

    res = utils.execRun(
        [
            "x = 1",
            "y = 2",
            "add(x, y)",
        ],
        space={**globals(), **locals()},
    )
    print(res)  # 3
    """
    if len(run) == 0:
        return
    # 函数名 随机生成
    fnName = f"_fn_{uuid.uuid4().hex}"
    # 缩进块
    indentedBlock = "    "
    # 使用 enumerate 获取每个元素的索引和值，结合 reduce 进行拼接
    functionBody = reduce(
        lambda acc, pair: f"{acc}\n{indentedBlock}{('return ' if pair[0] == len(run) - 1 else '')}{pair[1]}",
        enumerate(run),  # enumerate 返回的是 (index, value) 的元组
        "",
    )
    exec(f"""def {fnName}():{functionBody}""", space)
    return space[fnName]()
