import logging
from typing import Optional, List, Iterator, Sequence, Union, Tuple
import pandas as pd
from clickhouse_driver import Client
from gxkit.dbtools._base import BaseDBClient, DBConnectionError, SQLExecutionError
from gxkit.dbtools.sql_parser import SQLParser


class ClickHouseClient(BaseDBClient):
    """
    ClickHouseClient - ClickHouse 原生客户端
    Version: 0.1.0
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str, **kwargs):
        self.client: Optional[Client] = None
        self.db_type: str = "clickhouse"
        self.connect(host, port, user, password, database, **kwargs)

    def connect(self, host: str, port: int, user: str, password: str, database: str, **kwargs) -> None:
        try:
            self.client = Client(host=host, port=port, user=user, password=password, database=database, **kwargs)
            self.client.execute("SELECT 1")
        except Exception as e:
            raise DBConnectionError("dbtools.ClickHouseClient.connect", "clickhouse", str(e)) from e

    def execute(self, sql: str, stream: bool = False, batch_size: int = 10000) -> Union[
        pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        if self.client is None:
            raise DBConnectionError("dbtools.ClickHouseClient.execute", "clickhouse", "Not connected")
        parsed_sql = SQLParser(sql, db_type="clickhouse")
        sql_type = parsed_sql.sql_type()
        operation = parsed_sql.operation()
        if stream and sql_type == "statement":
            logging.warning(
                "[dbtools.ClickHouseClient.execute] | Stream function unsupported for this SQL. Using default.")
        elif stream and sql_type == "query":
            return self._stream_core(sql, operation, parsed_sql, batch_size)
        return self._execute_core(sql, sql_type)

    def executemany(self, sqls: Sequence[str], stream: bool = False, batch_size: int = 10000,
                    collect_results: bool = True) -> List[Union[pd.DataFrame, int, None]]:
        if not isinstance(sqls, Sequence) or isinstance(sqls, str) or not sqls:
            raise SQLExecutionError("dbtools.ClickHouseClient._execute_core", sqls, "unsupported sqls type")
        results = []
        try:
            for sql in sqls:
                parsed_sql = SQLParser(sql)
                sql_type = parsed_sql.sql_type()
                result = self.execute(sql, stream=stream, batch_size=batch_size)
                if collect_results and sql_type == "query":
                    results.append(result)
            return results if collect_results else []
        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient.executemany", ";".join(sqls), str(e)) from e

    def close(self) -> None:
        if self.client:
            self.client.disconnect()
            self.client = None

    def _execute_core(self, sql: str, sql_type: str) -> Union[pd.DataFrame, int, None]:
        try:
            if sql_type == "query":
                result, meta = self.client.execute(sql, with_column_types=True)
                if not result:
                    return None
                columns = [col[0] for col in meta]
                return pd.DataFrame(result, columns=columns)
            else:
                self.client.execute(sql)
                return 1
        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient._execute_core", sql, str(e)) from e

    def _stream_core(self, sql: str, operation: str, parsed_sql: SQLParser, batch_size: int) -> Optional[
        Iterator[pd.DataFrame]]:
        try:
            columns = self._get_columns(operation, parsed_sql)
            if columns is None:
                return None
            iter_rows = self.client.execute_iter(sql)

            def generator():
                batch = []
                for row in iter_rows:
                    batch.append(row)
                    if len(batch) >= batch_size:
                        yield pd.DataFrame(batch, columns=columns)
                        batch.clear()
                if batch:
                    yield pd.DataFrame(batch, columns=columns)

            return generator()
        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient._stream_core", sql, str(e)) from e

    def _get_columns(self, operation: str, parsed_sql: SQLParser) -> Optional[List[str]]:
        if operation == "select":
            column_sql = parsed_sql.change_segments({"limit": "10"})
            test, meta = self.client.execute(column_sql, with_column_types=True)
            return [col[0] for col in meta] if test else None
        else:
            return parsed_sql.columns(mode="alias")
