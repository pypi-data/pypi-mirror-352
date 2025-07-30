from enum import Enum
from typing import (
    List,
    Literal,
    Optional,
    TypedDict,
)  # 自 Python 3.5 开始作为标准库的一部分 帮助你更精确地指定变量、函数参数和返回值的类型


class Screenshot(TypedDict):
    """截图"""

    uri: str
    confidence: Optional[float]
    """相似度"""


Shot = str | Screenshot


class Image(TypedDict):
    """图片"""

    position: Optional[Shot]
    """位置图片 会获取 x y 坐标 用于 pyautogui action"""
    includes: Optional[Shot | List[Shot]]
    """包含"""
    excludes: Optional[Shot | List[Shot]]
    """排除"""


class Condition(TypedDict):
    """执行条件"""

    image: Optional[Image]

    run: Optional[str | List[str]]
    """run exec 执行脚本"""


class Action(TypedDict):
    """pyautogui 执行的具体操作"""

    type: str
    """操作类型"""
    arguments: Optional[List | dict]


class Delay(TypedDict):
    """延迟"""

    pre: Optional[float]
    """前置延迟"""
    next: Optional[float]
    """后置延迟"""


class Loop(TypedDict):
    """子任务 循环"""

    max: Optional[int]
    """最大迭代次数 默认是 float('inf')"""
    exitCondition: Optional[Condition]
    """退出条件 每次循环后会检测条件 满足则退出"""


class FlowMode(Enum):
    """子任务 流模式"""

    parallel = "parallel"
    """并行"""

    serial = "serial"
    """串行"""


class Job(TypedDict):
    """任务"""

    delay: Optional[Delay]
    condition: Optional[Condition]
    """
    当前任务的 执行条件

    如果不满足条件 当前任务会跳过 子任务也随之跳过（可以做分支判断）
    """
    action: Optional[Action]

    loop: Optional[Loop]
    flowMode: Optional[FlowMode]
    """默认 FlowMode.serial"""
    jobs: Optional[List["Job"]]  # 使用字符串 "xxx" 来进行前向引用（forward reference）
    """子任务"""


Workflows = Job | List[Job | List[Job]]
