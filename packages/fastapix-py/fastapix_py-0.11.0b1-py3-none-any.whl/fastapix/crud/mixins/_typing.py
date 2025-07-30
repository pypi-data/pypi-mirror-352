# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : kasm-user
# @FILE     : _typing.py
# @Time     : 2024/1/26 下午2:45
# @Desc     :
from datetime import datetime

from typing_extensions import Annotated

from fastapix.pkg.pydantic import PYDANTIC_V2


def convert_datetime_to_chinese(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def convert_datetime_to_timestamp(dt: datetime) -> float:
    return dt.timestamp()


if PYDANTIC_V2:
    from pydantic.functional_serializers import PlainSerializer

    DATETIME = Annotated[datetime, PlainSerializer(convert_datetime_to_chinese, when_used='json')]
    TIMESTAMP = Annotated[datetime, PlainSerializer(convert_datetime_to_timestamp, when_used='json')]
else:
    DATETIME = datetime
    TIMESTAMP = datetime
