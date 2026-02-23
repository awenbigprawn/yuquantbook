"""导出模块测试。"""

import pandas as pd

from stock_tracker.database.db_manager import DatabaseManager
from stock_tracker.exporter.csv_exporter import CSVExporter
from stock_tracker.exporter.excel_exporter import ExcelExporter


def test_excel_export_positions(tmp_path):
    """测试持仓 Excel 导出。"""
    df = pd.DataFrame([{"symbol": "AAPL", "quantity": 10}])
    output = tmp_path / "positions.xlsx"
    exporter = ExcelExporter(str(output))
    exporter.export_positions(df)
    assert output.exists()


def test_csv_export_dataframe(tmp_path):
    """测试 DataFrame CSV 导出。"""
    df = pd.DataFrame([{"symbol": "AAPL", "quantity": 10}])
    output = tmp_path / "positions.csv"
    exporter = CSVExporter(str(output))
    exporter.export_dataframe(df, chunk_size=1)
    assert output.exists()
    content = output.read_text(encoding="utf-8-sig")
    assert "AAPL" in content


def test_csv_export_from_query(tmp_path):
    """测试 SQL 直出 CSV。"""
    db = DatabaseManager(str(tmp_path / "test.db"))
    db.save_positions(
        [
            {
                "account_id": "DU1",
                "symbol": "TSLA",
                "quantity": 2,
                "avg_cost": 200,
                "market_value": 450,
                "unrealized_pnl": 50,
                "snapshot_date": "2026-01-01",
            }
        ]
    )
    output = tmp_path / "query.csv"
    exporter = CSVExporter(str(output))
    exporter.export_from_query(db, "SELECT symbol, quantity FROM positions")
    assert output.exists()
    assert "TSLA" in output.read_text(encoding="utf-8-sig")
