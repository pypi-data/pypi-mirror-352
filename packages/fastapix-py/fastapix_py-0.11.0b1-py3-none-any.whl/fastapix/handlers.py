# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : exception_handlers.py
# @Time     : 2023/10/30 13:48
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.openapi import utils as fu
from fastapi.requests import Request

from fastapix.exceptions import FastapixException
from fastapix.responses import DataResponse

fu.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "code": {
            "title": "code",
            "type": "integer",
            "default": 422
        },
        "message": {
            "title": "Message",
            "type": "string",
            "default": ""
        },
    },
    "required": ["code", "message"],
}


async def http_exception_default_handler(
        request: Request,
        exc: HTTPException
) -> DataResponse:
    return DataResponse(message=exc.detail, status_code=exc.status_code, exclude_none=True, code=exc.status_code)


async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError
) -> DataResponse:
    """
    捕捉422报错并进行自定义处理
    :param request:
    :param exc:
    :return:
    """
    messages = [f'{msg["type"]}:{msg["loc"]}({msg.get("input", None)}):{msg["msg"]}' for msg in
                jsonable_encoder(exc.errors())]
    message = ", ".join(messages)
    return DataResponse(message=message, status_code=422, exclude_none=True, code=422)


async def fastapix_exception_default_handler(
        request: Request,
        exc: FastapixException
) -> DataResponse:
    return DataResponse(message=exc.message, status_code=exc.code, exclude_none=True, code=exc.code)


def register_exception_handlers(fastapi: FastAPI):
    fastapi.add_exception_handler(FastapixException, fastapix_exception_default_handler)
    fastapi.add_exception_handler(HTTPException, http_exception_default_handler)
    fastapi.add_exception_handler(404, http_exception_default_handler)
    fastapi.add_exception_handler(RequestValidationError, request_validation_exception_handler)
