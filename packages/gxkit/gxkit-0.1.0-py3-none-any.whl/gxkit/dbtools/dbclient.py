"""
dbclient - SQL客户端工厂函数
Version: 0.1.0
"""
from typing import Union
from gxkit.dbtools._base import ClientOrToolError
from gxkit.dbtools.mysql_client import MySQLClient
from gxkit.dbtools.clickhouse_client import ClickHouseClient
from gxkit.dbtools.iotdb_client import IoTDBClient


def dbclient(db_type: str, host: str, port: int, user: str, password: str, database: str = None,
             **kwargs) -> Union[MySQLClient, ClickHouseClient, IoTDBClient]:

    db_type = db_type.lower()
    if db_type == "mysql":
        return MySQLClient(host=host, port=port, user=user, password=password, database=database, **kwargs)

    elif db_type == "clickhouse":
        return ClickHouseClient(host=host, port=port, user=user, password=password, database=database, **kwargs)

    elif db_type == "iotdb":
        return IoTDBClient(host=host, port=port, user=user, password=password, **kwargs)

    else:
        raise ClientOrToolError("[dbtools.dbclient]", f"Unknown client type: {db_type}")
