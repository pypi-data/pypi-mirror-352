import asyncio
import os
import aiofiles
import base64
import aiohttp
import io
from PIL import Image


async def pathToBytes(path: str):
    """本地文件 转 图片字节流"""
    # 使用 aiofiles 进行异步文件读取
    # "rb" 表示以二进制只读模式打开文件 r: read (读取) b: binary (二进制)
    async with aiofiles.open(path, "rb") as f:
        return await f.read()


async def uriToBytes(uri: str):
    """远程URI 转 图片字节流"""
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            # raise_for_status() 会检查 HTTP 响应的状态码
            # 如果状态码是 4xx 或 5xx，会直接抛出 HTTPError 异常
            response.raise_for_status()
            return (
                await response.read()
            )  # 返回的是响应体的原始字节流（bytes），不进行任何解码 使用 .decode('utf-8')解码 将其转换为字符串
            # return await response.text() # 响应体的内容解析为字符串（str） 默认使用 'utf-8' 编码


async def base64ToBytes(base64Str: str):
    """Base64 转 图片字节流"""
    # 处理 base64 字符串，如果包含逗号则取逗号后的部分，否则使用整个字符串
    # 例如: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." -> "iVBORw0KGgoAAAANSUhEUgAA..."
    core = base64Str.split(",")[1] if "," in base64Str else base64Str
    # base64.b64decode 本身是同步操作，但我们可以将其包装在异步函数中
    # 如果数据量较大，可以考虑使用 asyncio.to_thread 来避免阻塞事件循环
    return await asyncio.to_thread(base64.b64decode, core)


async def ImageToBytes(image: Image.Image):
    """PIL Image 转 图片字节流"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


async def toBytes(source: str | bytes | Image.Image):
    """
    将 本地文件/远程URI/base64/PIL Image 转 Bytes
    """
    # 如果已经是 bytes 类型，直接返回
    if isinstance(source, bytes):
        return source
    # 如果是PIL Image，转换为bytes
    if isinstance(source, Image.Image):
        return await ImageToBytes(source)
    # 本地绝对路径 是否存在
    if os.path.exists(source):
        return await pathToBytes(source)
    # 是否 远程URI
    if source.startswith("http"):
        return await uriToBytes(source)
    # 否则是base64字符串
    return await base64ToBytes(source)


async def bytesToImage(bytes: bytes):
    """图片字节流 转 PIL Image 对象"""
    # 使用 asyncio.to_thread 将同步的 Image.open 操作转换为异步操作
    # 使用PIL裁剪图片并识别文字
    return await asyncio.to_thread(Image.open, io.BytesIO(bytes))


async def getImgExt(source: str | bytes):
    """获取图片格式"""
    image = await bytesToImage(await toBytes(source))
    # 获取图片格式（PIL 会检查这些二进制数据的文件头（File Headers）来识别图片格式）
    return image.format.lower()


async def toBase64(source: str | bytes):
    """将 本地文件/远程URI/base64 转 Base64"""
    bytes = await toBytes(source)
    # 二进制转 Base64
    base64Str = base64.b64encode(bytes).decode("utf-8")
    ext = await getImgExt(bytes)
    # 添加 data:image/{ext};base64 前缀
    return f"data:image/{ext};base64,{base64Str}"
