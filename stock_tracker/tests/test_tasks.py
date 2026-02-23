"""任务调度模块测试。"""

from stock_tracker.database.db_manager import DatabaseManager
from stock_tracker.ib_connector.data_fetcher import IBDataFetcher
from stock_tracker.ib_connector.ib_client import IBClient
from stock_tracker.scheduler.tasks import StockTrackerScheduler


def test_setup_tasks(tmp_path):
    """测试任务配置成功。"""
    db = DatabaseManager(str(tmp_path / "test.db"))
    client = IBClient("127.0.0.1", 7497, 1)
    fetcher = IBDataFetcher(client)
    scheduler = StockTrackerScheduler(db, client, fetcher)
    scheduler.setup_tasks()
    jobs = scheduler.list_jobs()
    assert len(jobs) == 4
