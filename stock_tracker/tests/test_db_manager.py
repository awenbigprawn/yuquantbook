"""数据库模块测试。"""

import time

import pytest

from stock_tracker.database.db_manager import DatabaseManager


class TestDatabaseManager:
    """DatabaseManager 测试集合。"""

    @pytest.fixture()
    def db(self, tmp_path):
        """创建临时数据库。"""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))

    def test_save_positions(self, db: DatabaseManager):
        """测试持仓保存。"""
        positions = [
            {
                "account_id": "DU123456",
                "symbol": "AAPL",
                "quantity": 100,
                "avg_cost": 150.0,
                "market_value": 17500.0,
                "unrealized_pnl": 2500.0,
                "snapshot_date": "2026-02-24",
            }
        ]
        db.save_positions(positions)
        df = db.get_positions_dataframe()
        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "AAPL"

    def test_save_prices_batch(self, db: DatabaseManager):
        """测试批量股价保存性能。"""
        prices = [
            {
                "symbol": "AAPL",
                "trade_date": f"2020-01-{i:02d}",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000,
                "adjusted_close": 103.0,
            }
            for i in range(1, 32)
        ]

        start = time.time()
        db.save_prices(prices)
        elapsed = time.time() - start

        assert elapsed < 1.0
        df = db.get_prices_dataframe("AAPL")
        assert len(df) == 31
