import os

# 当前工作目录
cwdPath = os.getcwd()

commonDirPath = os.path.join(cwdPath, "src/common")

# images目录
imagesDirPath = os.path.join(commonDirPath, "images")

# images目录
jsonDirPath = os.path.join(commonDirPath, "jsons")

# __file__ 是一个特殊变量，它指向当前模块的文件名。这个文件名可以是相对路径也可以是绝对路径，这取决于如何运行该脚本或模块
# utilsFilePath = os.path.abspath(__file__)

# 当前文件所在的目录
# utilsDirPath = os.path.dirname(utilsFilePath)
