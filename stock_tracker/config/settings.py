"""配置管理模块，负责加载和校验环境变量。"""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    """应用配置定义。"""

    ib_host: str = Field(default="127.0.0.1", alias="IB_HOST")
    ib_port: int = Field(default=7497, alias="IB_PORT")
    client_id: int = Field(default=1, alias="CLIENT_ID")
    db_path: str = Field(default="stock_tracker.db", alias="DB_PATH")
    export_dir: str = Field(default="exports", alias="EXPORT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    position_snapshot_hour: int = 4
    position_snapshot_minute: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def export_path(self) -> Path:
        """返回导出目录并保证存在。"""
        export_path = Path(self.export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取单例配置对象。"""
    return Settings()
