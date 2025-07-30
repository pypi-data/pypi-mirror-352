from typing import Any


def toArr(arr: Any) -> list[Any]:
    """将入参 包装转化成数组"""
    if isinstance(arr, list):
        return arr
    if arr is None:
        return []
    return [arr]
