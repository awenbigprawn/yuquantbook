"""通用辅助函数。"""

from datetime import date, datetime
from typing import Any


def to_date_str(value: Any) -> str:
    """将输入转换为 YYYY-MM-DD 字符串。"""
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, datetime):
        return value.date().strftime("%Y-%m-%d")
    return str(value)


def chunked(seq: list[Any], size: int) -> list[list[Any]]:
    """将列表按给定大小分块。"""
    return [seq[i : i + size] for i in range(0, len(seq), size)]
