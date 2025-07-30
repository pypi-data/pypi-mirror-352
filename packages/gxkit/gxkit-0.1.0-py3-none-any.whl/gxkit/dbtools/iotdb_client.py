import logging
import re
import pandas as pd
from typing import Optional, List, Tuple, Iterator, Sequence, Union, Any
from iotdb import SessionPool
from iotdb.SessionPool import create_session_pool, PoolConfig
from gxkit.dbtools._base import BaseDBClient, DBConnectionError, SQLExecutionError
from gxkit.dbtools.sql_parser import SQLParser


class IoTDBClient(BaseDBClient):
    """
    IoTDBClient - Apache IoTDB 原生客户端
    Version: 0.1.0
    """

    def __init__(self, host: str, port: int, user: str, password: str, max_pool_size: int = 10,
                 wait_timeout_in_ms: int = 3000, **kwargs):
        self.pool: Optional[SessionPool] = None
        self.db_type = "iotdb"
        self.connect(host, port, user, password, max_pool_size, wait_timeout_in_ms, **kwargs)

    def connect(self, host: str, port: int, user: str, password: str, max_pool_size: int, wait_timeout_in_ms: int,
                **kwargs) -> None:
        try:
            config = PoolConfig(host=host, port=str(port), user_name=user, password=password, **kwargs)
            self.pool = create_session_pool(config, max_pool_size=max_pool_size, wait_timeout_in_ms=wait_timeout_in_ms)
            session = self.pool.get_session()
            session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
            self.pool.put_back(session)
        except Exception as e:
            raise DBConnectionError("dbtools.IoTDBClient.connect", "iotdb", str(e)) from e

    def execute(self, sql: str, auto_decision: bool = False, stream: bool = False, batch_size: int = 10000,
                prefix_path: int = 1, use_native: bool = False, max_retry: int = 3) -> Union[
        pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        if self.pool is None:
            raise DBConnectionError("dbtools.IoTDBClient.execute", "iotdb", "Database not connected")
        parsed_sql = SQLParser(sql, db_type="iotdb")
        sql_type = parsed_sql.sql_type()
        session = self.pool.get_session()

        if sql_type == "statement" and stream:
            logging.warning(
                "[dbtools.IoTDBClient.execute] | Stream function unsupported for this SQL. Using normal execution.")
            stream = False

        try:
            if auto_decision and sql_type == "query":
                need_page, limit_size = self._decision(session, parsed_sql, prefix_path)
                if need_page:
                    if stream:
                        batch_size = self._adjust_batch_size_for_limit(batch_size, limit_size, context="execute")
                        return self._stream_paged(session, parsed_sql, batch_size, prefix_path, use_native)
                    return self._execute_paged(session, parsed_sql, prefix_path, use_native, limit_size)
            if stream and sql_type == "query":
                return self._stream_core(session, sql, batch_size, prefix_path, use_native)
            return self._execute_core(session, sql, sql_type, prefix_path, use_native)
        except Exception as e:
            raise SQLExecutionError("dbtools.IoTDBClient.execute", sql, str(e)) from e
        finally:
            self.pool.put_back(session)

    def executemany(self, sqls: Sequence[str], auto_decision: bool = False, stream: bool = False,
                    batch_size: int = 10000, collect_results: bool = True, prefix_path: int = 1,
                    use_native: bool = False, max_retry: int = 3) -> Optional[list]:
        if self.pool is None:
            raise DBConnectionError("dbtools.IoTDBClient.executemany", "iotdb", "Not connected")

        session = self.pool.get_session()
        results = []
        try:
            for sql in sqls:
                parsed = SQLParser(sql, db_type="iotdb")
                sql_type = parsed.sql_type()
                if auto_decision and sql_type == "query":
                    need_page, limit_size = self._decision(session, parsed, prefix_path)
                    if need_page:
                        if stream:
                            batch_size = self._adjust_batch_size_for_limit(batch_size, limit_size,
                                                                           context="executemany")
                            result = self._stream_paged(session, parsed, batch_size, prefix_path, use_native)
                        else:
                            result = self._execute_paged(session, parsed, prefix_path, use_native, limit_size)
                    else:
                        result = self._stream_core(session, sql, batch_size, prefix_path, use_native) if stream else \
                            self._execute_core(session, sql, sql_type, prefix_path, use_native)
                else:
                    result = self._stream_core(session, sql, batch_size, prefix_path, use_native) if (
                            stream and sql_type == "query") else \
                        self._execute_core(session, sql, sql_type, prefix_path, use_native)
                if collect_results and sql_type == "query":
                    results.append(result)
            return results if collect_results else None
        except Exception as e:
            raise SQLExecutionError("dbtools.IoTDBClient.executemany", "\n".join(sqls), str(e)) from e
        finally:
            self.pool.put_back(session)

    def close(self) -> None:
        if self.pool:
            self.pool.close()
            self.pool = None

    def _execute_core(self, session, sql: str, sql_type: str, prefix_path: int, use_native: bool) -> Union[
        pd.DataFrame, int, None]:
        if sql_type != "query":
            session.execute_non_query_statement(sql)
            return 1
        result_set, col_mapping, columns = self._get_result_set(session, sql, prefix_path)

        rows = [self._build_row(record, col_mapping, use_native) for record in iter(result_set.next, None)]
        result_set.close_operation_handle()
        if not rows:
            return None
        return pd.DataFrame(rows, columns=columns)

    def _stream_core(self, session, sql: str, batch_size: int, prefix_path: int, use_native: bool) -> Optional[
        Iterator[pd.DataFrame]]:
        result_set, col_mapping, columns = self._get_result_set(session, sql, prefix_path)

        first_record = result_set.next()
        if first_record is None:
            result_set.close_operation_handle()
            return None

        def generator():
            batch = [self._build_row(first_record, col_mapping, use_native)]
            has_yielded = False
            for record in iter(result_set.next, None):
                batch.append(self._build_row(record, col_mapping, use_native))
                if len(batch) >= batch_size:
                    yield pd.DataFrame(batch, columns=columns)
                    has_yielded = True
                    batch.clear()
            if batch:
                yield pd.DataFrame(batch, columns=columns)
                has_yielded = True
            result_set.close_operation_handle()

            if not has_yielded:
                return None

        return generator()

    def _get_result_set(self, session, sql: str, prefix_path: int) -> Tuple[pd.DataFrame, List, List]:
        result_set = session.execute_query_statement(sql)
        raw_cols = result_set.get_column_names()
        col_mapping = self._build_col_mapping(raw_cols, prefix_path)
        columns = [short for _, short in col_mapping]
        return result_set, col_mapping, columns

    def _paged_generator(self, session, parsed_sql: SQLParser, limit: int, prefix_path: int,
                         use_native: bool) -> Iterator[pd.DataFrame]:
        seg_where = parsed_sql.segments('where').get('where')
        original_where = seg_where[0] if seg_where else None
        # 初始化时间边界
        start_ts = None
        end_ts = None
        if original_where:
            # 提取原始 WHERE 中的时间限制
            match_start = re.search(r"(?i)\bTime\s*(>=|>)\s*(\d+|'[^']+'|\"[^\"]+\")", original_where)
            match_end = re.search(r"(?i)\bTime\s*(<=|<)\s*(\d+|'[^']+'|\"[^\"]+\")", original_where)

            if match_start:
                start_ts = match_start.group(2).strip("'\"")
            if match_end:
                end_ts = match_end.group(2).strip("'\"")

        last_ts = start_ts
        while True:
            # step1 构建分页 where 条件
            if original_where:
                where_clause = original_where.strip()
                cond = f"Time > {last_ts}" if last_ts else None
                if cond:
                    if re.search(r"(?i)\btime\s*>\s*", where_clause):
                        # 如果原句已有 Time >，不重复加
                        final_where = where_clause
                    else:
                        final_where = f"{where_clause} AND {cond}"
                else:
                    final_where = where_clause
            else:
                final_where = f"Time > {last_ts}" if last_ts else None
            # step2 替换 WHERE 和 LIMIT
            replacements = {"limit": str(limit)}
            if final_where:
                replacements["where"] = final_where
            page_sql = parsed_sql.change_segments(replacements)
            # step3 执行分页 SQL
            df = self._execute_core(session, page_sql, "query", prefix_path, use_native)
            if df is None or df.empty:
                break
            yield df
            # step4 更新时间游标
            if len(df) < limit:
                break
            last_ts = df["timestamp"].max()
            # 如果设置了 end_ts，判断是否超过结束时间
            if end_ts is not None:
                try:
                    if float(last_ts) >= float(end_ts):
                        break
                except ValueError:
                    pass

    def _execute_paged(self, session, parsed_sql: SQLParser, prefix_path: int, use_native: bool,
                       limit: int) -> Optional[pd.DataFrame]:
        dfs = list(self._paged_generator(session, parsed_sql, limit, prefix_path, use_native))
        if not dfs:
            return None
        return pd.concat(dfs, ignore_index=True)

    def _stream_paged(self, session, parsed_sql: SQLParser, batch_size: int, prefix_path: int,
                      use_native: bool) -> Optional[Iterator[pd.DataFrame]]:
        generator = self._paged_generator(session, parsed_sql, batch_size, prefix_path, use_native)

        try:
            first_batch = next(generator)
        except StopIteration:
            return None

        def stream_generator():
            yield first_batch
            for batch in generator:
                yield batch

        return stream_generator()

    def _decision(self, session, parsed_sql: SQLParser, prefix_path: int) -> Tuple[bool, int]:
        column_limit = 20
        cell_limit = 1_000_000
        default_line_limit = 10_000  # 程序默认的 fallback

        sql_type = parsed_sql.sql_type()
        if sql_type != "query":
            return False, default_line_limit
        operation = parsed_sql.operation()
        select_ops = {"select", "union", "intersect", "except", "with"}
        if operation not in select_ops:
            return False, default_line_limit
        try:
            columns = self._get_columns(session, parsed_sql, prefix_path)
            column_count = len(columns)

            if not columns:
                return False, default_line_limit
            # 尽量选取真实列进行 count，而非 timestamp
            count_column = columns[1].split(".")[-1] if len(columns) > 1 else columns[0].split(".")[-1]
            line_count = self._get_lines(session, parsed_sql, count_column)

            line_limit = cell_limit // max(1, column_count)
            if line_count:
                line_limit = min(line_limit, line_count)
            line_limit = max(1, line_limit)

            need_page = column_count >= column_limit or line_count > line_limit
            return need_page, line_limit
        except Exception as e:
            raise SQLExecutionError("dbtools.IoTDBClient._decision", parsed_sql.sql, str(e)) from e

    def _get_columns(self, session, parsed_sql: SQLParser, prefix_path: int) -> Optional[List[str]]:
        column_sql = parsed_sql.change_segments({"limit": "10"})
        _, _, columns = self._get_result_set(session, column_sql, prefix_path)
        return columns

    def _get_lines(self, session, parsed_sql: SQLParser, column: str) -> int:
        limit = parsed_sql.segments("limit").get("limit")
        count_limit = None if not limit else int(limit[0].split()[1])
        try:
            count_sql = SQLParser(parsed_sql.change_columns(f"count({column})"), db_type="iotdb").sql()
        except Exception:
            inner_sql = parsed_sql.sql()
            count_sql = f"SELECT count(*) FROM ({inner_sql})"
        count_df = self._execute_core(session, count_sql, "query", prefix_path=1, use_native=False)
        count_lines = int(count_df.iloc[0, 0]) if count_df is not None else 0
        return min(count_limit, count_lines) if count_limit else count_lines

    @staticmethod
    def _build_col_mapping(raw_cols: List[str], prefix_path: int) -> List[tuple[bool, str]]:
        return [
            (col.lower() == "time", "timestamp" if col.lower() == "time" else ".".join(col.split(".")[-prefix_path:]))
            for col in raw_cols]

    @staticmethod
    def _build_row(record, col_mapping: List[tuple[bool, str]], use_native: bool) -> List[Any]:
        fields = record.get_fields()
        row = []
        field_idx = 0
        for is_time, _ in col_mapping:
            if is_time:
                row.append(record.get_timestamp())
            else:
                if field_idx < len(fields):
                    field = fields[field_idx]
                    row.append(
                        field.get_long_value() if use_native and field.get_data_type() == 0 else field.get_string_value())
                    field_idx += 1
                else:
                    row.append(None)
        return row

    @staticmethod
    def _adjust_batch_size_for_limit(batch_size: int, limit_size: int, context: str = "execute") -> int:
        if batch_size > limit_size:
            logging.warning(
                f"[IoTDBClient.{context}] | batch_size ({batch_size}) exceeds optimal limit ({limit_size}). "
                f"Using limit_size instead.")
            return limit_size
        return batch_size
