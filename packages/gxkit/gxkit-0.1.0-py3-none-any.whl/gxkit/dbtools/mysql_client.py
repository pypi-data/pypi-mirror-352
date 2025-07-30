import logging
import pandas as pd
import pymysql
from datetime import datetime, timedelta
from pymysql.cursors import Cursor, SSCursor
from typing import Optional, List, Iterator, Sequence, Union
from gxkit.dbtools._base import BaseDBClient, DBConnectionError, SQLExecutionError
from gxkit.dbtools.sql_parser import SQLParser


class MySQLClient(BaseDBClient):
    """
    MySQLClient - MySQLClient 原生客户端
    Version: 0.1.0
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str, **kwargs):
        self.client: Optional[pymysql.connect] = None
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay: timedelta = timedelta(minutes=10)
        self.database = database
        self._connection_params = dict(host=host, port=port, user=user, password=password, database=database, **kwargs)
        self.connect()

    def connect(self) -> None:
        try:
            self.client = pymysql.connect(**self._connection_params)
            with self.client.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            raise DBConnectionError("dbtools.MySQLClient.connect", "mysql", str(e)) from e

    def execute(self, sql: str, stream: bool = False, batch_size: int = 10000) -> Union[
        pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        if self.client is None:
            raise DBConnectionError("dbtools.MySQLClient.connect", "mysql", "Database not connected")
        parsed_sql = SQLParser(sql,db_type="mysql")
        sql_type = parsed_sql.sql_type()
        if stream and sql_type == "statement":
            logging.warning(
                "[dbtools.MySQLClient.execute] | Stream function unsupported for this SQL. Using normal execution.")
        elif stream and sql_type == "query":
            return self._stream_core(sql, batch_size)
        return self._execute_core(sql, sql_type, autocommit=True)

    def executemany(self, sqls: Sequence[str], wrapper: bool = True, collect_results: bool = True) -> List[
        Union[pd.DataFrame, int, None]]:
        if not isinstance(sqls, Sequence) or isinstance(sqls, str) or not sqls:
            raise SQLExecutionError("dbtools.MySQLClient._execute_core", sqls, "unsupported sqls type")
        results = []
        try:
            if wrapper:
                self.client.begin()
            for sql in sqls:
                parsed_sql = SQLParser(sql, db_type="mysql")
                sql_type = parsed_sql.sql_type()
                result = self._execute_core(sql, sql_type=sql_type, autocommit=not wrapper)
                if collect_results:
                    results.append(result)
            if wrapper:
                self.client.commit()
            return results if collect_results else []
        except Exception as e:
            if wrapper:
                try:
                    self.client.rollback()
                except:
                    pass
            raise SQLExecutionError("dbtools.MySQLClient.executemany", ";".join(sqls), str(e)) from e

    def close(self):
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None

    def _execute_core(self, sql: str, sql_type: str, autocommit: bool = True) -> Union[pd.DataFrame, int, None]:
        self._check_and_reconnect()
        try:
            with self.client.cursor(Cursor) as cursor:
                if sql_type == "query":
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if not result:
                        return None
                    column_names = [desc[0] for desc in cursor.description]
                    self._last_success_time = datetime.now()
                    return pd.DataFrame(result, columns=column_names)
                else:
                    if autocommit:
                        self.client.begin()
                    cursor.execute(sql)
                    if autocommit:
                        self.client.commit()
                    self._last_success_time = datetime.now()
                    return 1
        except (pymysql.err.OperationalError, pymysql.err.InterfaceError):
            logging.warning("dbtools.MySQLClient._execute_core Connection error, attempting retry...")
            self.close()
            self.connect()
            return self._execute_core(sql, sql_type, autocommit)
        except Exception as e:
            if sql_type == "statement" and autocommit:
                try:
                    self.client.rollback()
                except:
                    pass
            raise SQLExecutionError("dbtools.MySQLClient._execute_core", sql, str(e)) from e

    def _stream_core(self, sql: str, batch_size: int) -> Optional[Iterator[pd.DataFrame]]:
        self._check_and_reconnect()
        try:
            cursor = self.client.cursor(SSCursor)
            cursor.execute(sql)
            column_names = [desc[0] for desc in cursor.description]
            first_batch = cursor.fetchmany(batch_size)

            if not first_batch:
                cursor.close()
                return None
            self._last_success_time = datetime.now()

            def generator():
                try:
                    yield pd.DataFrame(first_batch, columns=column_names)
                    while True:
                        batch = cursor.fetchmany(batch_size)
                        if not batch:
                            break
                        self._last_success_time = datetime.now()
                        yield pd.DataFrame(batch, columns=column_names)
                finally:
                    cursor.close()

            return generator()
        except (pymysql.err.OperationalError, pymysql.err.InterfaceError):
            logging.warning("[dbtools.MySQLClient._stream_core] | Connection error, attempting retry...")
            self.close()
            self.connect()
            return self._stream_core(sql, batch_size)
        except Exception as e:
            raise SQLExecutionError("dbtools.MySQLClient._stream_core", sql, str(e)) from e

    def _check_and_reconnect(self):
        if self.client is None or self._last_success_time is None:
            return

        now = datetime.now()
        if now - self._last_success_time > self._reconnect_delay:
            try:
                logging.info("[dbtools.MySQLClient] Reconnecting due to inactivity timeout")
                self.client.ping(reconnect=True)
                self._last_success_time = now
            except Exception:
                logging.warning("[dbtools.MySQLClient] Ping failed, reconnecting from scratch...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()
