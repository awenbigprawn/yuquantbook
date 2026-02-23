"""IB 客户端模块测试。"""

import asyncio

import pytest

from stock_tracker.ib_connector.ib_client import IBClient


class FakeIB:
    """模拟 IB 对象。"""

    def __init__(self):
        self.connected = False

    async def connectAsync(self, host, port, clientId):
        self.connected = True

    def isConnected(self):
        return self.connected

    def disconnect(self):
        self.connected = False

    def managedAccounts(self):
        return ["DU1", "DU2"]

    def positions(self, account):
        class Contract:
            symbol = "AAPL"

        class Position:
            def __init__(self):
                self.account = account or "DU1"
                self.contract = Contract()
                self.position = 1
                self.avgCost = 100

        return [Position()]


@pytest.mark.asyncio
async def test_connect_disconnect():
    """测试连接与断开。"""
    client = IBClient("127.0.0.1", 7497, 1)
    client.ib = FakeIB()
    ok = await client.connect()
    assert ok is True
    await client.disconnect()
    assert client.ib.isConnected() is False


@pytest.mark.asyncio
async def test_get_positions():
    """测试持仓获取标准化结果。"""
    client = IBClient("127.0.0.1", 7497, 1)
    client.ib = FakeIB()
    await client.connect()
    positions = await client.get_positions("DU1")
    assert len(positions) == 1
    assert positions[0]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_retry_timeout():
    """测试超时重试。"""

    class TimeoutIB(FakeIB):
        async def connectAsync(self, host, port, clientId):
            await asyncio.sleep(0.2)

    client = IBClient("127.0.0.1", 7497, 1, timeout=0.01)
    client.ib = TimeoutIB()
    ok = await client.connect()
    assert ok is False
