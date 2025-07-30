"""
dbtools 抽象层
Version 0.1.0
"""
from abc import ABC, abstractmethod
from typing import Sequence, Any
from enum import IntEnum


class DBErrorCode(IntEnum):
    GENERAL = 1000
    CONNECTION = 1001
    EXECUTION = 1002
    PARSE = 1003
    TOOLS = 1004


class DBToolsError(Exception):
    """
    DBToolsError - 数据库工具通用异常基类
    """

    def __init__(self, message: str, *, code: int = DBErrorCode.GENERAL):
        self.code = code
        self.message = message
        super().__init__(message)


class DBConnectionError(DBToolsError):
    def __init__(self, source: str, db_type: str, message: str = "Database connection error"):
        full_message = (
            f"\n\t[Source] \t {source}\n"
            f"\t[Database Type]: {db_type}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=DBErrorCode.CONNECTION)


class SQLExecutionError(DBToolsError):
    def __init__(self, source: str, sql: str, message: str = "SQL execute error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[SQL] : '{sql[:200]}{'...' if len(sql) >= 200 else ''}'\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=DBErrorCode.EXECUTION)


class SQLParseError(DBToolsError):
    def __init__(self, source: str, sql: str, message: str = "SQL parse error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[SQL] : '{sql[:200]}{'...' if len(sql) >= 200 else ''}'\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=DBErrorCode.PARSE)


class ClientOrToolError(DBToolsError):
    def __init__(self, source: str, message: str = "DB tools error"):
        full_message = (
            f"\n\t[Source] \t {source}\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=DBErrorCode.TOOLS)


class BaseDBClient(ABC):
    """
    BaseDBClient - 数据库客户端抽象基类
    所有数据库客户端都应继承该类并实现指定方法
    """

    @abstractmethod
    def connect(self, **kwargs):
        """连接数据库"""
        pass

    @abstractmethod
    def execute(self, sql: str, **kwargs) -> Any:
        """执行单条 SQL 语句"""
        pass

    @abstractmethod
    def executemany(self, sqls: Sequence[str], **kwargs) -> Any:
        """顺序执行多个不同 SQL 语句"""
        pass

    @abstractmethod
    def close(self):
        """关闭数据库连接"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
