import os
import aiofiles


async def readFile(filePath: str):
    # 使用 aiofiles 打开文件
    async with aiofiles.open(filePath, mode="r", encoding="utf-8") as file:
        # 读取文件内容
        content = await file.read()
    return content


def getFileExt(path: str):
    """从路径中获取文件扩展名"""
    # 获取文件扩展名并处理:
    # 1. os.path.splitext(path) - 将路径分割为文件名和扩展名,返回元组 (文件名, 扩展名)
    # 2. [1] - 取元组的第二个元素,即扩展名部分
    # 3. lower() - 将扩展名转换为小写
    # 4. lstrip(".") - 去掉扩展名开头的点号
    # 例如: "/path/to/image.PNG" -> "png"
    return os.path.splitext(path)[1].lower().lstrip(".")
