import logging
import os
import json

# 配置日志目录
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")


class LowercaseLevelFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)


def setup_logger():
    logger = logging.getLogger("py_logger")
    # 设置日志级别为 DEBUG，记录所有级别的日志消息
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        # 创建格式化器
        formatter = LowercaseLevelFormatter(
            "%(asctime)s [python:%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 文件处理器
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# 初始化原始logger
_logger = setup_logger()


def _format_message(message):
    """格式化日志消息：字符串直接返回，其他类型转为JSON"""
    return (
        message
        if isinstance(message, str)
        else json.dumps(
            message,
            ensure_ascii=False,
            # 完全无空格
            separators=(",", ":"),
        )
    )


class StringifyMiddleware:
    """日志包装器：自动处理JSON序列化"""

    def __init__(self, logger):
        self._logger = logger

    def __getattr__(self, name):
        """动态代理所有日志方法"""
        if name in (
            "error",
            "info",
            "warn",
            "debug",
        ):
            return lambda msg: getattr(self._logger, name)(_format_message(msg))
        return getattr(self._logger, name)


# 创建包装后的logger实例
logger = StringifyMiddleware(_logger)
