# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : responses.py
# @Time     : 2023/10/29 15:30
from typing import Any, Dict, Optional, Generic, TypeVar

from fastapi.responses import JSONResponse
from pydantic import Field

from fastapix.pkg.pydantic import model_dump_json, GenericModel

Data = TypeVar('Data')


class GenericData(GenericModel, Generic[Data]):
    code: int = 200
    message: Optional[str] = Field(None)
    data: Optional[Data] = None


class DataResponse(JSONResponse):
    """
    Json: {
        "code": 200,
        "message": None,
        "data": None
    }
    """

    def __init__(self, content=None, *, status_code: int = 200,
                 headers: Optional[dict] = None,
                 media_type: Optional[str] = None,
                 background=None, **kwargs):
        self.exclude_none = kwargs.pop('exclude_none', False)
        self.exclude_unset = kwargs.pop('exclude_unset', False)
        self.by_alias = kwargs.pop('by_alias', True)

        self.code = kwargs.get('code', status_code)
        if content is None:
            content = kwargs or None

        super().__init__(
            status_code=status_code, headers=headers,
            media_type=media_type, background=background,
            content=content
        )

    def render(self, content: Any) -> bytes:
        if isinstance(content, Dict):

            return model_dump_json(
                GenericData(**content),
                exclude_none=self.exclude_none,
                exclude_unset=self.exclude_unset,
                by_alias=self.by_alias,
            ).encode("utf-8")
        elif isinstance(content, GenericData):
            return model_dump_json(
                content,
                exclude_none=self.exclude_none,
                exclude_unset=self.exclude_unset,
                by_alias=self.by_alias,
            ).encode("utf-8")
        else:
            return model_dump_json(
                GenericData(code=self.code, data=content),
                exclude_none=self.exclude_none,
                exclude_unset=self.exclude_unset,
                by_alias=self.by_alias,
            ).encode('utf-8')
