"""CSV 导出模块，支持分块和 SQL 直出。"""

from pathlib import Path
from typing import Any

import pandas as pd

from stock_tracker.database.db_manager import DatabaseManager


class CSVExporter:
    """CSV 导出器。"""

    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def export_dataframe(self, df: pd.DataFrame, chunk_size: int = 50000) -> Path:
        """导出 DataFrame 到 CSV（utf-8-sig）。"""
        first = True
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]
            chunk.to_csv(
                self.output_path,
                mode="w" if first else "a",
                index=False,
                header=first,
                encoding="utf-8-sig",
            )
            first = False
        if len(df) == 0:
            df.to_csv(self.output_path, index=False, encoding="utf-8-sig")
        return self.output_path

    def export_from_query(
        self,
        db_manager: DatabaseManager,
        query: str,
        params: tuple[Any, ...] | None = None,
        chunk_size: int = 50000,
    ) -> Path:
        """从 SQL 查询直接分块导出 CSV。"""
        with db_manager.get_connection() as conn:
            first = True
            for chunk in pd.read_sql_query(query, conn, params=params, chunksize=chunk_size):
                chunk.to_csv(
                    self.output_path,
                    mode="w" if first else "a",
                    index=False,
                    header=first,
                    encoding="utf-8-sig",
                )
                first = False
        return self.output_path
