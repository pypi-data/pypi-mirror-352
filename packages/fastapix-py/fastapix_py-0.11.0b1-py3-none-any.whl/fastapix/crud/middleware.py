# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : middleware.py
# @Time     : 2024/5/14 下午4:15
# @Desc     :
from contextlib import AsyncExitStack

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from fastapix.crud.database import SqlalchemyDatabase, EngineDatabase


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            db: SqlalchemyDatabase,
    ):
        super().__init__(app)

        self.db = EngineDatabase(db)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        scope = request.scope
        if not scope.get(f"__fastapix_database__:{id(self.db)}", False):
            exception = None
            async with AsyncExitStack() as async_stack:
                await async_stack.enter_async_context(self.db(scope=id(scope)))
                scope[f"__fastapix_database__:{id(self.db)}"] = self.db
                try:
                    response = await call_next(request)
                except Exception as e:
                    exception = e
                    await self.db.async_rollback()

            if exception:
                raise exception
        return response
