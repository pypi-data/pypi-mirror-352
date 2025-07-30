import os


def getAbsPath(path: str, basePath: str = os.getcwd()):
    # 判断路径是否是绝对路径
    if os.path.isabs(path):
        return path  # 如果是绝对路径，直接返回
    else:
        return os.path.join(basePath, path)  # 否则，转换为绝对路径并返回
