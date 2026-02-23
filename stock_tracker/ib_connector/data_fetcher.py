"""IB 数据获取器，封装历史数据与实时价格抓取。"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from stock_tracker.ib_connector.ib_client import IBClient

logger = logging.getLogger(__name__)


class IBDataFetcher:
    """负责从 IB 拉取市场数据。"""

    def __init__(self, client: IBClient) -> None:
        self.client = client

    async def get_historical_data(
        self,
        symbol: str,
        duration: str = "10 Y",
        bar_size: str = "1 day",
        what_to_show: str = "TRADES",
    ) -> list[dict[str, Any]]:
        """获取历史股价，支持自定义时间跨度。"""
        if not await self.client.ensure_connection() or self.client.ib is None:
            return []

        try:
            contract = self.client.ib.Stock(symbol, "SMART", "USD")
            bars = await asyncio.wait_for(
                self.client.ib.reqHistoricalDataAsync(
                    contract,
                    endDateTime="",
                    durationStr=duration,
                    barSizeSetting=bar_size,
                    whatToShow=what_to_show,
                    useRTH=True,
                    formatDate=1,
                ),
                timeout=30,
            )
            payload = [
                {
                    "symbol": symbol,
                    "trade_date": bar.date.strftime("%Y-%m-%d") if isinstance(bar.date, datetime) else str(bar.date),
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume),
                    "adjusted_close": float(bar.close),
                }
                for bar in bars
            ]
            logger.info("%s 历史数据条数: %s", symbol, len(payload))
            return payload
        except Exception as exc:  # pragma: no cover
            logger.exception("获取 %s 历史数据失败: %s", symbol, exc)
            return []

    async def get_current_price(self, symbol: str) -> float | None:
        """获取标的当前价格。"""
        if not await self.client.ensure_connection() or self.client.ib is None:
            return None

        try:
            contract = self.client.ib.Stock(symbol, "SMART", "USD")
            ticker = self.client.ib.reqMktData(contract, "", False, False)
            await asyncio.sleep(2)
            price = ticker.marketPrice()
            return float(price) if price is not None else None
        except Exception as exc:  # pragma: no cover
            logger.exception("获取 %s 实时价格失败: %s", symbol, exc)
            return None
