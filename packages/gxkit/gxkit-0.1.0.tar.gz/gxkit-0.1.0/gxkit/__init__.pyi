from typing import Union, Optional
from .dbtools.mysql_client import MySQLClient
from .dbtools.clickhouse_client import ClickHouseClient
from .dbtools.iotdb_client import IoTDBClient
from .dbtools.sql_parser import SQLParser as _SQLParser

__all__ = ["dbclient", "SQLParser"]

# 静态文件类型声明 for IDE/Linux -- PEP484/561

SQLParser: type[_SQLParser]


def dbclient(db_type: str, host: str, port: int, user: str, password: str, database: Optional[str] = None, **kwargs) -> \
        Union[MySQLClient, ClickHouseClient, IoTDBClient]: ...
