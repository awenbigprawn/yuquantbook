"""SQLite 数据库管理器，提供初始化、写入、查询能力。"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from stock_tracker.database.models import CREATE_TABLES_SQL, INDEX_SQL


class DatabaseManager:
    """数据库管理类。"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self) -> Iterable[sqlite3.Connection]:
        """数据库连接上下文管理器。"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            yield conn
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self) -> None:
        """初始化数据库结构。"""
        with self.get_connection() as conn:
            for sql in CREATE_TABLES_SQL:
                conn.execute(sql)
            for sql in INDEX_SQL:
                conn.execute(sql)

    def save_accounts(self, accounts: list[dict[str, Any]]) -> None:
        """批量保存账户数据。"""
        sql = """
        INSERT INTO accounts (account_id, account_name, currency)
        VALUES (:account_id, :account_name, :currency)
        ON CONFLICT(account_id) DO UPDATE SET
            account_name = excluded.account_name,
            currency = excluded.currency;
        """
        with self.get_connection() as conn:
            conn.executemany(sql, accounts)

    def save_positions(self, positions: list[dict[str, Any]]) -> None:
        """批量保存持仓快照。"""
        sql = """
        INSERT INTO positions (
            account_id, symbol, quantity, avg_cost,
            market_value, unrealized_pnl, snapshot_date
        )
        VALUES (
            :account_id, :symbol, :quantity, :avg_cost,
            :market_value, :unrealized_pnl, :snapshot_date
        )
        ON CONFLICT(account_id, symbol, snapshot_date) DO UPDATE SET
            quantity = excluded.quantity,
            avg_cost = excluded.avg_cost,
            market_value = excluded.market_value,
            unrealized_pnl = excluded.unrealized_pnl;
        """
        with self.get_connection() as conn:
            conn.executemany(sql, positions)

    def save_prices(self, prices: list[dict[str, Any]], batch_size: int = 5000) -> None:
        """分批保存股价历史。"""
        sql = """
        INSERT INTO prices (
            symbol, trade_date, open, high, low,
            close, volume, adjusted_close
        )
        VALUES (
            :symbol, :trade_date, :open, :high, :low,
            :close, :volume, :adjusted_close
        )
        ON CONFLICT(symbol, trade_date) DO UPDATE SET
            open = excluded.open,
            high = excluded.high,
            low = excluded.low,
            close = excluded.close,
            volume = excluded.volume,
            adjusted_close = excluded.adjusted_close;
        """

        with self.get_connection() as conn:
            for i in range(0, len(prices), batch_size):
                conn.executemany(sql, prices[i : i + batch_size])

    def log_fetch(self, fetch_type: str, symbol: str, status: str, error_message: str | None = None) -> None:
        """记录数据抓取日志。"""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO fetch_logs (fetch_type, symbol, status, error_message)
                VALUES (?, ?, ?, ?)
                """,
                (fetch_type, symbol, status, error_message),
            )

    def query_dataframe(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:
        """执行查询并返回 DataFrame。"""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_positions_dataframe(self, snapshot_date: str | None = None) -> pd.DataFrame:
        """读取持仓 DataFrame。"""
        if snapshot_date:
            return self.query_dataframe(
                "SELECT * FROM positions WHERE snapshot_date = ? ORDER BY account_id, symbol",
                (snapshot_date,),
            )
        return self.query_dataframe("SELECT * FROM positions ORDER BY snapshot_date DESC, account_id, symbol")

    def get_prices_dataframe(self, symbol: str | None = None) -> pd.DataFrame:
        """读取价格 DataFrame。"""
        if symbol:
            return self.query_dataframe(
                "SELECT * FROM prices WHERE symbol = ? ORDER BY trade_date",
                (symbol,),
            )
        return self.query_dataframe("SELECT * FROM prices ORDER BY symbol, trade_date")
