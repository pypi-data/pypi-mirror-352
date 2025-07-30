from typing import List
from .img import toBytes

# 必须在最后否则调用会报错 可能是 python-shell 自身的bug
from paddleocr import PaddleOCR


# PaddleOCR
# uv add paddleocr
# uv add paddlepaddle==3.0.0rc1
# uv add --dev setuptools
# CCache 是一个编译器缓存工具，它可以极大地减少重复编译的时间。它通过缓存之前编译的结果来避免不必要的重新编译。这对于开发环境中的频繁构建特别有用，尤其是在持续集成（CI）环境中
# brew install ccache && ccache -s  安装 及 检测
# 初始化 只需要执行一次 同时开启角度分类 这对于那些可能存在倾斜或者倒置文本的图片特别有用 use_angle_cls=True，设置为中文识别 lang="ch"

# use_angle_cls: 开启角度分类，用于识别倾斜或倒置的文本
# lang: 设置识别语言为中文
ocr = PaddleOCR(use_angle_cls=True, lang="ch")


async def imgOcr(uri: str | bytes):
    bytes = await toBytes(uri)
    result = ocr.ocr(
        img=bytes,
        # cls: 是否使用方向分类器，用于识别倾斜或倒置的文本
        cls=True,
    )
    lines: List[str] = []
    for res in result:
        for line in res:
            # [左上角坐标, 右上角坐标, 右下角坐标, 左下角坐标], (文本, 置信度)
            coordinates, (text, confidence) = line
            lines.append(text)

    return lines
