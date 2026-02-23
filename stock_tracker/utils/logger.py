"""日志工具模块，统一 logging 与 loguru 配置。"""

import logging
import sys
from pathlib import Path

from loguru import logger as loguru_logger


def setup_logger(log_level: str = "INFO", log_file: str = "logs/stock_tracker.log") -> logging.Logger:
    """初始化日志系统。"""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
    )
    loguru_logger.add(
        log_file,
        rotation="10 MB",
        retention="30 days",
        level=log_level.upper(),
        encoding="utf-8",
    )

    return logging.getLogger("stock_tracker")
