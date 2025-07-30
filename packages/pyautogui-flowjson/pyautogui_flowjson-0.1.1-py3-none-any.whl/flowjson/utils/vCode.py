import asyncio
import io
import ddddocr
from .img import toBytes, bytesToImage, getImgExt

# [参考](https://www.cnblogs.com/gggod/p/18145831)


async def vCodeFillType(source: str) -> str:
    """
    英文数字（填充类）验证码 得到文本
    """
    bytes = await toBytes(source)
    ocr = ddddocr.DdddOcr(show_ad=False)  # show_ad=False关闭广告
    return ocr.classification(bytes)  # 54G6


async def vCodeClickType(source: str):
    """
    中文（点选类）验证码 得到坐标
    """
    bytes = await toBytes(source)
    ocr = ddddocr.DdddOcr(det=True, show_ad=False)  # show_ad=False关闭广告
    format, img = await asyncio.gather(getImgExt(bytes), bytesToImage(bytes))
    res: dict[str, tuple[float, float]] = {}
    for box in ocr.detection(bytes):
        lt_x1, lt_y1, rb_x2, rb_y2 = box
        cropped = img.crop((lt_x1, lt_y1, rb_x2, rb_y2))
        # 将裁剪后的图片转换为bytes
        img_byte_arr = io.BytesIO()
        cropped.save(img_byte_arr, format=format)
        img_byte_arr = img_byte_arr.getvalue()
        # 使用普通OCR识别文字
        text = ddddocr.DdddOcr(show_ad=False).classification(img_byte_arr)
        x = (lt_x1 + rb_x2) / 2
        y = (lt_y1 + rb_y2) / 2
        res[text] = (x, y)
    return res


async def vCodeScrollType(targetSource: str, backgroundSource: str, simple_target=True):
    """
    滑块（滑动类）验证码 得到坐标
    Args:
        targetSource: 目标图片
        backgroundSource: 背景图片
        simple_target: 表示使用简单模式匹配,只返回目标位置信息
    Returns:
        dict: {
            'target': [int, int, int, int]  # 目标位置 [左上x, 左上y, 右下x, 右下y]
        }
    """
    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)  # show_ad=False关闭广告
    targetBytes, backgroundBytes = await asyncio.gather(
        toBytes(targetSource), toBytes(backgroundSource)
    )
    return det.slide_match(targetBytes, backgroundBytes, simple_target=simple_target)
