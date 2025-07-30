# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : database.py
# @Time     : 2024/5/14 下午4:31
# @Desc     :
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Generator,
    Mapping,
    Optional,
    TypeVar,
    Union,
)

from sqlalchemy.engine import URL, Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from typing_extensions import Concatenate, ParamSpec

from fastapix.crud._abc_database import AbcAsyncDatabase, to_thread

_P = ParamSpec("_P")
_T = TypeVar("_T")
_R = TypeVar("_R")


class AsyncDatabase(AbcAsyncDatabase):

    def __init__(
            self,
            engine: AsyncEngine,
            commit_on_exit: bool = True,
            **session_options,
    ):

        self.engine: AsyncEngine = engine

        self.commit_on_exit: bool = commit_on_exit
        session_options.setdefault("class_", AsyncSession)
        self.session_maker: Callable[..., AsyncSession] = sessionmaker(self.engine, **session_options)

        self._session_scope: ContextVar[Union[str, AsyncSession, None]] = ContextVar(
            f"_session_context_var_{id(self)}", default=None
        )
        self.scoped_session: async_scoped_session = async_scoped_session(
            self.session_maker, scopefunc=self._session_scope.get
        )
        super().__init__(engine)

    @property
    def session(self) -> AsyncSession:
        return self.scoped_session()

    @property
    def scoped(self) -> bool:
        return bool(self._session_scope.get())

    def __call__(self, scope: Any = None):
        return AsyncSessionContextVarManager(self, scope=scope)

    @classmethod
    def create(
            cls, url: Union[str, URL], *, commit_on_exit: bool = True, session_options: Mapping[str, Any] = None,
            **kwargs
    ) -> "AsyncDatabase":
        kwargs.setdefault("future", True)
        engine = create_async_engine(url, **kwargs)
        session_options = session_options or {}
        return cls(engine, commit_on_exit=commit_on_exit, **session_options)

    @asynccontextmanager
    async def session_generator(self) -> AsyncGenerator[AsyncSession, Any]:
        if self.scoped:
            yield self.session
        else:
            async with self.session_maker() as session:
                yield session
                if self.commit_on_exit:
                    await session.commit()

    async def run(
            self,
            fn: Callable[[Concatenate[Union[Session, Connection], _P]], _T],
            *args: _P.args,
            is_session: bool = True,
            **kwargs: _P.kwargs,
    ) -> Union[_T, _R]:
        if is_session:
            async with self.session_generator() as session:
                return await session.run_sync(fn, *args, **kwargs)
        async with self.engine.begin() as conn:
            return await conn.run_sync(fn, *args, **kwargs)


class Database(AbcAsyncDatabase):

    def __init__(self, engine: Engine, commit_on_exit: bool = True, **session_options):
        self.engine: Engine = engine
        self.commit_on_exit: bool = commit_on_exit
        session_options.setdefault("class_", Session)
        self.session_maker: Callable[..., Session] = sessionmaker(self.engine, **session_options)
        self._session_scope: ContextVar[Union[str, Session, None]] = ContextVar(
            f"_session_context_var_{id(self)}", default=None
        )
        self.scoped_session: scoped_session = scoped_session(self.session_maker, scopefunc=self._session_scope.get)
        super().__init__(engine)

    @property
    def session(self) -> Session:
        return self.scoped_session()

    @property
    def scoped(self) -> bool:
        return bool(self._session_scope.get())

    def __call__(self, scope: Any = None):
        return SessionContextVarManager(self, scope=scope)

    @classmethod
    def create(
            cls, url: Union[str, URL], *, commit_on_exit: bool = True,
            session_options: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> "Database":
        kwargs.setdefault("future", True)
        engine = create_engine(url, **kwargs)
        session_options = session_options or {}
        return cls(engine, commit_on_exit=commit_on_exit, **session_options)

    @contextmanager
    def session_generator(self) -> Generator[Session, Any, None]:
        if self.scoped:
            yield self.session
        else:
            with self.session_maker() as session:
                yield session
                if self.commit_on_exit:
                    session.commit()

    def run(
            self,
            fn: Callable[[Concatenate[Union[Session, Connection], _P]], _T],
            *args: _P.args,
            is_session: bool = True,
            **kwargs: _P.kwargs,
    ) -> Union[_T, _R]:
        if is_session:
            with self.session_generator() as session:
                return fn(session, *args, **kwargs)
        with self.engine.begin() as conn:
            return fn(conn, *args, **kwargs)


class SessionContextVarManager:
    _SessionCls = Session

    def __init__(self, db: Database, scope: Any = None):
        self.db = db
        self._token = None
        self._scope = scope

    def __enter__(self):
        if not self._scope:
            session = self.db.session_maker()
            self._token = self.db._session_scope.set(session)
            self.db.scoped_session.registry.set(session)
        elif isinstance(self._scope, self._SessionCls):
            self._token = self.db._session_scope.set(self._scope)
            self.db.scoped_session.registry.set(self._scope)
        else:
            self._token = self.db._session_scope.set(self._scope)
        return self.db.session

    def _close_session(self, session: Session, exc_type):
        try:
            if exc_type is not None:
                session.rollback()
            elif self.db.commit_on_exit:
                session.commit()
        finally:
            session.close()

    def __exit__(self, exc_type, exc_value, traceback):
        if not (self._scope and isinstance(self._scope, self._SessionCls)):
            self._close_session(self.db.session, exc_type)
        self.db.scoped_session.registry.clear()
        self.db._session_scope.reset(self._token)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not (self._scope and isinstance(self._scope, self._SessionCls)):
            await to_thread(self._close_session, self.db.session, exc_type)
        self.db.scoped_session.registry.clear()
        self.db._session_scope.reset(self._token)


class AsyncSessionContextVarManager(SessionContextVarManager):
    _SessionCls = AsyncSession

    def __init__(self, db: AsyncDatabase, scope: Any = None):
        super().__init__(db, scope)  # type: ignore

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError("AsyncSessionContextVarManager does not support sync context manager.")

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.db: AsyncDatabase
        if not (self._scope and isinstance(self._scope, self._SessionCls)):
            session = self.db.session
            try:
                if exc_type is not None:
                    await session.rollback()
                elif self.db.commit_on_exit:
                    await session.commit()
            finally:
                await session.close()
        self.db.scoped_session.registry.clear()
        self.db._session_scope.reset(self._token)


SqlalchemyDatabase = Union[Engine, AsyncEngine, Database, AsyncDatabase]


def EngineDatabase(engine: SqlalchemyDatabase) -> Union[Database, AsyncDatabase]:
    if isinstance(engine, (Database, AsyncDatabase)):
        return engine
    if isinstance(engine, Engine):
        return Database(engine)
    if isinstance(engine, AsyncEngine):
        return AsyncDatabase(engine)
    raise TypeError(f"Unknown engine type: {type(engine)}")
