"""
Loguru 日志配置。

日志文件写入 .claw/logs/ 目录，按时间和大小自动切割。

使用方式：
    from claw.utils.logger import logger

    logger.info("hello")
    logger.debug("debug info")
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
# src/claw/utils/logger.py  →  项目根目录
_ROOT = Path(__file__).parent.parent.parent.parent
_LOG_DIR = _ROOT / ".claw" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 移除默认 handler（避免重复输出到 stderr）
# ---------------------------------------------------------------------------
logger.remove()

# ---------------------------------------------------------------------------
# Console handler：输出到 stderr，带颜色
# ---------------------------------------------------------------------------
logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# ---------------------------------------------------------------------------
# File handler：写入 .claw/logs/，按时间 + 大小切割
# ---------------------------------------------------------------------------
logger.add(
    _LOG_DIR / "aclaw_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="10 MB",      # 单文件超过 10MB 切割
    retention="7 days",    # 保留最近 7 天
    compression="gz",      # 旧日志压缩
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    enqueue=True,           # 线程安全，支持多进程
)

# ---------------------------------------------------------------------------
# 全局导出
# ---------------------------------------------------------------------------
__all__ = ["logger"]
