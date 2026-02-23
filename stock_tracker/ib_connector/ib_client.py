"""IB 客户端封装，提供异步连接与重试能力。"""

import asyncio
import logging
from typing import Any

try:
    from ib_insync import IB
except ImportError:  # pragma: no cover
    IB = None  # type: ignore


logger = logging.getLogger(__name__)


class IBClient:
    """对 ib_insync.IB 的轻量封装。"""

    def __init__(self, host: str, port: int, client_id: int, timeout: float = 10.0) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id
        self.timeout = timeout
        self.ib = IB() if IB else None

    async def connect(self) -> bool:
        """连接到 TWS/Gateway，支持最多 3 次重试。"""
        if self.ib is None:
            logger.error("ib_insync 未安装，无法连接 IB。")
            return False

        for retry in range(1, 4):
            try:
                await asyncio.wait_for(
                    self.ib.connectAsync(self.host, self.port, clientId=self.client_id),
                    timeout=self.timeout,
                )
                logger.info("成功连接 IB: %s:%s", self.host, self.port)
                return True
            except asyncio.TimeoutError as exc:
                logger.error("连接 IB 超时（第 %s/3 次）: %s", retry, exc)
                await asyncio.sleep(1)
            except Exception as exc:  # pragma: no cover
                logger.exception("连接 IB 失败（第 %s/3 次）: %s", retry, exc)
                await asyncio.sleep(1)
        return False

    async def disconnect(self) -> None:
        """断开连接。"""
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            logger.info("已断开 IB 连接")

    async def ensure_connection(self) -> bool:
        """确保连接在线，断开时自动重连。"""
        if self.ib is None:
            return False
        if self.ib.isConnected():
            return True
        logger.warning("检测到 IB 断开，尝试重连。")
        return await self.connect()

    async def get_accounts(self) -> list[str]:
        """获取账户列表。"""
        if not await self.ensure_connection() or self.ib is None:
            return []
        accounts: list[str] = self.ib.managedAccounts()
        logger.info("获取到账户数量: %s", len(accounts))
        return accounts

    async def get_positions(self, account: str = "") -> list[dict[str, Any]]:
        """获取并标准化持仓数据。"""
        if not await self.ensure_connection() or self.ib is None:
            return []

        rows: list[dict[str, Any]] = []
        for pos in self.ib.positions(account):
            rows.append(
                {
                    "account_id": pos.account,
                    "symbol": pos.contract.symbol,
                    "quantity": float(pos.position),
                    "avg_cost": float(pos.avgCost),
                    "market_value": None,
                    "unrealized_pnl": None,
                }
            )
        logger.info("账户 %s 持仓数量: %s", account or "ALL", len(rows))
        return rows
