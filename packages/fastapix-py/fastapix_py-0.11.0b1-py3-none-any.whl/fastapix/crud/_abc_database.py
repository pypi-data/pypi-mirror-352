# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _abc_database.py
# @Time     : 2024/5/15 下午3:32
# @Desc     :
import abc
import asyncio
import functools
from typing import Callable, Dict, TypeVar, Union

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import Engine
from sqlalchemy.orm import scoped_session

try:
    from asyncio import to_thread  # python 3.9+
except ImportError:
    import contextvars

    from typing_extensions import ParamSpec

    _P = ParamSpec("_P")
    _R = TypeVar("_R")

    async def to_thread(func: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> _R:  # noqa: E303
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)


class AbcAsyncDatabase(metaclass=abc.ABCMeta):  # noqa: B024

    _instances: Dict[str, "AbcAsyncDatabase"] = None

    def __new__(cls, engine: Union[Engine, AsyncEngine], *args, **kwargs):
        """Create a new instance of the database class.Each engine url corresponds to a database instance,
        and if it already exists, it is directly returned, otherwise a new instance is created.
        """
        cls._instances = cls._instances or {}
        if engine.url not in cls._instances:
            cls._instances[engine.url] = super().__new__(cls)
        return cls._instances[engine.url]

    def __init__(self, engine: Union[Engine, AsyncEngine], *args, **kwargs) -> None:
        for func_name in {
            "run",
            "begin",
            "begin_nested",
            "close",
            "commit",
            "connection",
            "delete",
            "execute",
            "flush",
            "get",
            "merge",
            "refresh",
            "rollback",
            "scalar",
            "scalars",
            "add",
            "add_all",
            "expire",
            "expire_all",
            "expunge",
            "expunge_all",
            "get_bind",
            "is_modified",
        }:
            func = getattr(self, func_name, None)
            if not func:
                func = getattr(self.scoped_session, func_name)  # type: ignore
                setattr(self, func_name, func)
            if func_name in {
                "add",
                "add_all",
                "expire",
                "expire_all",
                "expunge",
                "expunge_all",
                "get_bind",
                "is_modified",
            }:
                continue
            if (not asyncio.iscoroutinefunction(func) and
                    isinstance(self.scoped_session, scoped_session)):  # type: ignore
                func = functools.partial(to_thread, func)
            setattr(self, f"async_{func_name}", func)

    @property
    def asgi_middleware(self):
        """
        Example:
            ```Python
            app = FastAPI()
            db = Database.create("sqlite:///test.db")
            app.add_middleware(db.asgi_middleware)
            ```
        """

        def asgi_decorator(app):
            @functools.wraps(app)
            async def wrapped_app(scope, receive, send):
                if scope.get(f"__sqlalchemy_database__:{id(self)}", False):
                    return await app(scope, receive, send)
                    # bind session to request
                async with self.__call__(scope=id(scope)):
                    scope[f"__sqlalchemy_database__:{id(self)}"] = self
                    await app(scope, receive, send)

            return wrapped_app

        return asgi_decorator
