"""数据库建表语句定义。"""

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS accounts (
        account_id TEXT PRIMARY KEY,
        account_name TEXT,
        currency TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        quantity REAL,
        avg_cost REAL,
        market_value REAL,
        unrealized_pnl REAL,
        snapshot_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(account_id, symbol, snapshot_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        trade_date DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        adjusted_close REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, trade_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS symbols_config (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        asset_type TEXT,
        exchange TEXT,
        currency TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS fetch_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fetch_type TEXT,
        symbol TEXT,
        status TEXT,
        error_message TEXT,
        fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
]

INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_positions_account_date ON positions(account_id, snapshot_date);",
    "CREATE INDEX IF NOT EXISTS idx_prices_symbol_date ON prices(symbol, trade_date);",
]
