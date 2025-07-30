import importlib

_EXPORTS = {
    "dbclient": "dbtools.dbclient",
    "SQLParser": "dbtools.sql_parser",
}

_SUBMODULES = ["dbtools"]

__all__ = list(_EXPORTS.keys()) + _SUBMODULES

__version__ = "0.1.0"


def __getattr__(name: str):
    """懒加载所有模块"""
    if name in _EXPORTS:
        module_path = f".{_EXPORTS[name]}"
        module = importlib.import_module(module_path, __name__)
        return getattr(module, name)
    if name in _SUBMODULES:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    """返回IDE可识别的顶层列表"""
    return __all__
