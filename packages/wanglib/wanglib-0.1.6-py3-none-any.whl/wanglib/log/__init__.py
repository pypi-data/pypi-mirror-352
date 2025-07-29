import os
import sys
from pathlib import Path
from typing import Any, TextIO

from loguru import logger


class LoggerManager:
    """
    日志管理器，用于快速构建美观好用的loguru日志
    """

    def __init__(self) -> None:
        self.logger = logger
        self.terminal_logger_id: int = 0
        self.jsonl_logger_id: int = 0
        self.file_logger_id: int = 0
        self.logger.remove()  # 清除默认的Logger

    def get_logger(self):
        """获取日志对象"""
        return self.logger

    def add_terminal_logger(
        self,
        level: str = "INFO",
        target: TextIO | Any = sys.stdout,
        is_output_name: bool = False,
        is_output_function: bool = False,
        enqueue=True,
    ) -> "LoggerManager":
        """添加对终端记录的日志记录器"""
        self.logger.level("TRACE", color="<cyan>", icon="🤔 __TRACE")
        self.logger.level("DEBUG", color="<blue>", icon="🚧 __DEBUG")
        self.logger.level("INFO", color="<white>", icon="ℹ️ ___INFO")
        self.logger.level("SUCCESS", color="<green>", icon="✅ SUCCESS")
        self.logger.level("WARNING", color="<yellow>", icon="🤯 WARNING")
        self.logger.level("ERROR", color="<red>", icon="😡 __ERROR")

        default_format: str = (
            "<g>{time:MM-DD HH:mm:ss}</g> "
            + "[<lvl>{level.icon}</lvl>] "
            + ("<c><u>{name}</u></c> " if is_output_name else "")
            + ("<c>{function}:{line}</c> " if is_output_function else "")
            + "|| <lvl>{message}</lvl>"
        )
        self.terminal_logger_id = self.logger.add(
            target,
            level=level,
            diagnose=False,
            format=default_format,
            enqueue=enqueue,
        )

        return self

    def add_jsonl_logger(
        self,
        log_dir: os.PathLike = Path("./logs/"),
        level: str = "INFO",
        enqueue=True,
        rotation="100 MB",
        retention="10 days",
    ) -> "LoggerManager":
        """添加对jsonl文件的日志记录器"""
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.jsonl_logger_id = self.logger.add(
            Path(log_dir).joinpath("log-{time}.jsonl"),
            level=level,
            enqueue=enqueue,
            serialize=True,
            rotation=rotation,
            retention=retention,
        )

        return self

    def add_file_logger(
        self,
        log_dir: os.PathLike = Path("./logs/"),
        level: str = "INFO",
        enqueue=True,
        rotation="100 MB",
        retention="10 days",
    ) -> "LoggerManager":
        """添加对log文件的日志记录器"""
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.file_logger_id = self.logger.add(
            Path(log_dir).joinpath("log-{time}.log"),
            level=level,
            enqueue=enqueue,
            rotation=rotation,
            retention=retention,
        )

        return self

    def remove_terminal_logger(self) -> "LoggerManager":
        """移除对终端的日志记录器"""
        self.logger.remove(self.terminal_logger_id)
        return self

    def remove_jsonl_logger(self) -> "LoggerManager":
        """移除对jsonl文件的日志记录器"""
        self.logger.remove(self.jsonl_logger_id)
        return self

    def remove_file_logger(self) -> "LoggerManager":
        """移除对文件的日志记录器"""
        self.logger.remove(self.file_logger_id)
        return self
