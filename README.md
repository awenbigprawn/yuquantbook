# 股票记账自动化系统（Stock Tracker）

本项目是一个本地命令行应用，用于通过 Interactive Brokers (IB) 自动获取持仓和股价，并存储到 SQLite，支持定时任务与报表导出。

## 项目特性

- 自动连接/重连 IB TWS/Gateway（异步 + 重试）
- 支持多账户持仓抓取并保存每日快照
- 支持历史股价抓取与批量写入 SQLite
- 支持导出 Excel（xlsx）和 CSV（utf-8-sig）
- 使用 APScheduler 进行定时自动化
- 使用 pydantic + dotenv 做配置管理

## 目录结构

```text
stock_tracker/
├── config/
├── database/
├── ib_connector/
├── exporter/
├── scheduler/
├── utils/
├── tests/
└── main.py
```

## 安装步骤

1. 创建 Python 3.10+ 环境
2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

```bash
cp .env.example .env
```

## 配置说明

`.env` 支持以下参数：

- `IB_HOST`：IB 地址
- `IB_PORT`：IB 端口（常见 7497/4002）
- `CLIENT_ID`：IB 客户端 ID
- `DB_PATH`：SQLite 文件路径
- `EXPORT_DIR`：导出目录
- `LOG_LEVEL`：日志等级

## 使用方法

### 启动定时任务（阻塞）

```bash
python -m stock_tracker.main --mode run
```

### 单次执行任务

```bash
python -m stock_tracker.main --mode snapshot   # 每日持仓
python -m stock_tracker.main --mode weekly     # 周度股价更新
python -m stock_tracker.main --mode export     # 月度导出
python -m stock_tracker.main --mode reconnect  # IB 重连检查
python -m stock_tracker.main --mode jobs       # 查看任务状态
```

## 定时任务说明（北京时间）

- 每日 04:30：持仓快照
- 周日 10:00：历史股价更新
- 每月 1 日 09:00：月度报表导出
- 每日 15:05：IB 重连检查

## 常见问题

1. **无法连接 IB**
   - 确认 TWS/Gateway 已启动
   - 确认 API 权限已开启
   - 检查 `IB_HOST/IB_PORT/CLIENT_ID` 是否正确

2. **导出文件乱码**
   - CSV 已使用 `utf-8-sig` 编码，直接用 Excel 打开即可

3. **数据库写入慢**
   - 已启用 SQLite WAL + executemany 批量写入

## 测试

```bash
pytest stock_tracker/tests -q
```

## 说明

- 本项目不依赖 Web 框架，不使用云服务，全部本地运行。
- 可进一步扩展 PostgreSQL 适配层。
