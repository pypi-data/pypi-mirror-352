# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : json.py
# @Time     : 2023/11/30 0:46
from fastapix.pkg.pydantic import pydantic_encoder


try:
    from ujson import dumps
    from ujson import loads
except ImportError:
    from json import dumps
    from json import loads

json_serializer = dumps
json_validator = loads


def pydantic_json_serializer(*args, **kwargs) -> str:
    """
    解决 <BaseModel> is not JSON serializable
    engine: AsyncEngine = create_async_engine(database_url, json_serializer=pydantic_json_serializer)
    engine: Engine = create_engine(database_url, json_serializer=pydantic_json_serializer)
    :param args:
    :param kwargs:
    :return:
    """
    return json_serializer(*args, default=pydantic_encoder, **kwargs)
