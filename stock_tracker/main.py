"""主入口文件，提供命令行执行能力。"""

import argparse
import logging

from stock_tracker.config.settings import get_settings
from stock_tracker.database.db_manager import DatabaseManager
from stock_tracker.ib_connector.data_fetcher import IBDataFetcher
from stock_tracker.ib_connector.ib_client import IBClient
from stock_tracker.scheduler.tasks import StockTrackerScheduler
from stock_tracker.utils.logger import setup_logger


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="股票记账自动化系统")
    parser.add_argument(
        "--mode",
        choices=["run", "snapshot", "weekly", "export", "reconnect", "jobs"],
        default="run",
        help="运行模式",
    )
    return parser


def main() -> None:
    """程序主函数。"""
    settings = get_settings()
    setup_logger(settings.log_level)
    logger = logging.getLogger(__name__)

    db_manager = DatabaseManager(settings.db_path)
    ib_client = IBClient(settings.ib_host, settings.ib_port, settings.client_id)
    fetcher = IBDataFetcher(ib_client)
    scheduler = StockTrackerScheduler(db_manager, ib_client, fetcher)
    scheduler.setup_tasks()

    args = build_parser().parse_args()

    if args.mode == "run":
        scheduler.start()
    elif args.mode == "snapshot":
        scheduler.daily_positions_snapshot()
    elif args.mode == "weekly":
        scheduler.weekly_prices_update()
    elif args.mode == "export":
        scheduler.monthly_export()
    elif args.mode == "reconnect":
        scheduler.ib_reconnect()
    elif args.mode == "jobs":
        for job in scheduler.list_jobs():
            logger.info("任务 %s -> 下次执行: %s", job["id"], job["next_run_time"])


if __name__ == "__main__":
    main()
