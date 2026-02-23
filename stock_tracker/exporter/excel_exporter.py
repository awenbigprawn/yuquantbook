"""Excel 导出模块，支持大数据分块写入。"""

from pathlib import Path

import pandas as pd


class ExcelExporter:
    """Excel 导出器。"""

    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def export_positions(self, df: pd.DataFrame, sheet_name: str = "持仓") -> Path:
        """导出持仓到 Excel。"""
        with pd.ExcelWriter(self.output_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return self.output_path

    def export_prices(self, df: pd.DataFrame, chunk_size: int = 10000) -> Path:
        """导出股价到 Excel（分块处理）。"""
        with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
            start_row = 0
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i : i + chunk_size]
                chunk.to_excel(
                    writer,
                    sheet_name="prices",
                    index=False,
                    startrow=start_row,
                    header=(start_row == 0),
                )
                start_row += len(chunk)
        return self.output_path
