import logging
from typing import Any


# 定義彩色格式化類
class ColoredFormatter(logging.Formatter):
    """自定義彩色日誌格式化類"""

    # ANSI 顏色碼
    COLORS = {
        "DEBUG": "\033[94m",  # 藍色
        "INFO": "\033[92m",  # 綠色
        "WARNING": "\033[93m",  # 黃色
        "ERROR": "\033[91m",  # 紅色
        "CRITICAL": "\033[95m",  # 紫色
        "RESET": "\033[0m",  # 重置顏色
    }

    def format(self, record):
        # 保存原始訊息
        log_message = super().format(record)
        # 如果日誌級別在顏色字典中，則添加顏色
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        # 否則返回原始訊息
        return log_message


# 創建一個實例，供直接引用
colored_formatter = ColoredFormatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "root": {"level": "DEBUG", "handlers": ["consoleHandler", "fileHandler"]}
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored_formatter",
            "stream": "ext://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "formatter",
            "filename": "app.log",
        },
    },
    "formatters": {
        "formatter": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
        # 修改格式化器配置，使用可被引用的類或函數名稱
        "colored_formatter": {
            "()": ColoredFormatter,
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    },
}
