"""任务调度模块，定义持仓、股价、导出、重连任务。"""

import asyncio
import logging
from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from stock_tracker.config.settings import get_settings
from stock_tracker.database.db_manager import DatabaseManager
from stock_tracker.exporter.csv_exporter import CSVExporter
from stock_tracker.exporter.excel_exporter import ExcelExporter
from stock_tracker.ib_connector.data_fetcher import IBDataFetcher
from stock_tracker.ib_connector.ib_client import IBClient

logger = logging.getLogger(__name__)


class StockTrackerScheduler:
    """股票记账调度器。"""

    def __init__(self, db_manager: DatabaseManager, ib_client: IBClient, fetcher: IBDataFetcher) -> None:
        self.db_manager = db_manager
        self.ib_client = ib_client
        self.fetcher = fetcher
        self.settings = get_settings()
        self.scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    def daily_positions_snapshot(self) -> None:
        """每日持仓快照任务。"""
        logger.info("开始获取每日持仓...")
        try:
            asyncio.run(self._daily_positions_snapshot_async())
        except Exception as exc:
            logger.exception("每日持仓任务失败: %s", exc)

    async def _daily_positions_snapshot_async(self) -> None:
        if not await self.ib_client.connect():
            raise ConnectionError("无法连接 IB")

        accounts = await self.ib_client.get_accounts()
        today = date.today().strftime("%Y-%m-%d")
        all_positions: list[dict] = []
        for account in accounts:
            positions = await self.ib_client.get_positions(account)
            for p in positions:
                p["snapshot_date"] = today
            all_positions.extend(positions)

        if all_positions:
            self.db_manager.save_positions(all_positions)
            logger.info("保存 %s 条持仓记录", len(all_positions))
        await self.ib_client.disconnect()

    def weekly_prices_update(self) -> None:
        """周度股价更新任务。"""
        logger.info("开始周度股价更新...")
        try:
            asyncio.run(self._weekly_prices_update_async())
        except Exception as exc:
            logger.exception("周度股价更新失败: %s", exc)

    async def _weekly_prices_update_async(self) -> None:
        if not await self.ib_client.connect():
            raise ConnectionError("无法连接 IB")

        symbols_df = self.db_manager.query_dataframe("SELECT symbol FROM symbols_config WHERE is_active = 1")
        for symbol in symbols_df["symbol"].tolist():
            data = await self.fetcher.get_historical_data(symbol, duration="10 Y")
            if data:
                self.db_manager.save_prices(data)
        await self.ib_client.disconnect()

    def monthly_export(self) -> None:
        """月度导出任务。"""
        logger.info("开始月度报表导出...")
        today = date.today().strftime("%Y-%m-%d")
        positions_df = self.db_manager.get_positions_dataframe()
        prices_df = self.db_manager.get_prices_dataframe()

        excel_exporter = ExcelExporter(str(self.settings.export_path / f"monthly_report_{today}.xlsx"))
        csv_positions = CSVExporter(str(self.settings.export_path / f"positions_{today}.csv"))
        csv_prices = CSVExporter(str(self.settings.export_path / f"prices_{today}.csv"))

        excel_exporter.export_positions(positions_df, sheet_name="持仓")
        csv_positions.export_dataframe(positions_df)
        csv_prices.export_dataframe(prices_df)
        logger.info("月度报表导出完成")

    def ib_reconnect(self) -> None:
        """每日 IB 重连任务。"""
        logger.info("执行 IB 重连检查...")
        try:
            asyncio.run(self._ib_reconnect_async())
        except Exception as exc:
            logger.exception("IB 重连任务失败: %s", exc)

    async def _ib_reconnect_async(self) -> None:
        connected = await self.ib_client.ensure_connection()
        logger.info("IB 连接状态: %s", connected)

    def setup_tasks(self) -> None:
        """配置所有定时任务。"""
        self.scheduler.add_job(
            self.daily_positions_snapshot,
            CronTrigger(hour=4, minute=30),
            id="daily_positions_snapshot",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.weekly_prices_update,
            CronTrigger(day_of_week="sun", hour=10, minute=0),
            id="weekly_prices_update",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.monthly_export,
            CronTrigger(day=1, hour=9, minute=0),
            id="monthly_export",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.ib_reconnect,
            CronTrigger(hour=15, minute=5),
            id="ib_reconnect",
            replace_existing=True,
        )
        logger.info("定时任务配置完成")

    def list_jobs(self) -> list[dict[str, str]]:
        """返回任务状态列表。"""
        return [
            {
                "id": job.id,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger),
            }
            for job in self.scheduler.get_jobs()
        ]

    def start(self) -> None:
        """启动调度器（阻塞式）。"""
        logger.info("启动调度器")
        self.scheduler.start()
