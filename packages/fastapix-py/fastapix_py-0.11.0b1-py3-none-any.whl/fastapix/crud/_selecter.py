# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _selecter.py
# @Time     : 2023/10/29 15:15
import re
from datetime import date, datetime
from enum import Enum  # noqa: F401
from re import Pattern
from typing import Optional, Type, Union, List, Tuple

from fastapi import Depends, Query  # noqa: F401
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy import desc, cast, func, not_, String, exists, select, text, or_, and_
from sqlmodel import SQLModel
from typing_extensions import Annotated

from fastapix.pkg import markdown
from fastapix.pkg.json import json_validator
from fastapix.pkg.pydantic import (
    model_fields, ModelField, Undefined,
    parse_date, parse_datetime,
    get_type_from_field,

)
from fastapix.crud._models import get_foreign_models
from fastapix.crud._sqltypes import AutoJson


def split_str_comma(string: str) -> List[str]:
    """

    :param string:
    :return:
    """
    placeholder = "{placeholder_comma}"
    brackets_content = re.findall(r'\[.*?]|{.*?}', string)
    if brackets_content:
        for content in brackets_content:
            string = string.replace(content, placeholder, 1)

    parts = string.split(',')

    final_parts = []
    for part in parts:
        if part == placeholder and brackets_content:
            final_parts.append(brackets_content.pop(0))  # 使用pop(0)确保顺序
        else:
            final_parts.append(part)

    return final_parts


def get_modelfield_by_alias(table_model: Type[SQLModel], alias: str) -> Optional[ModelField]:
    fields = model_fields(table_model).values()
    for field in fields:
        if field.alias == alias or getattr(fields, 'serialization_alias', None) == alias:
            return field
    return None


def required_parser_str_set_list(primary_key: Union[int, str]) -> List[str]:
    if isinstance(primary_key, int):
        return [str(primary_key)]
    elif not isinstance(primary_key, str):
        return []
    return list(set(split_str_comma(primary_key)))


RequiredPrimaryKeyListDepend = Annotated[List[str], Depends(required_parser_str_set_list)]


def parser_ob_str_set_list(order_by: Optional[str] = None) -> List[str]:
    return required_parser_str_set_list(order_by)


OrderByListDepend = Annotated[List[str], Depends(parser_ob_str_set_list)]


def get_python_type_parse(field: ModelField):
    try:
        python_type = get_type_from_field(field)
        if issubclass(python_type, date):
            if issubclass(python_type, datetime):
                return parse_datetime
            return parse_date
        return python_type
    except NotImplementedError:
        return str


def _python_to_table_json(value):
    value = json_validator(value)
    return cast(value, AutoJson)


def _is_json_type(python_type):
    if type(python_type) is type:
        return issubclass(python_type, (list, tuple, set, dict, BaseModel))
    else:
        return False


def _is_str_type(python_type):
    if type(python_type) is type:
        return issubclass(python_type, str)
    else:
        return False


def equal_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[=]` : 等于, `abc` or `[=]abc`, 等于空字符串：`[=]`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        elif dialect_type in ['sqlite']:
            python_type = json_validator
        else:
            python_type = str
    value = python_type(value)
    return column.__eq__(value)


def not_equal_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[!=]` : 不等, `[!]abc` or `[!=]abc`, 不等于空字符串：`[!]` or `[!=]`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        elif dialect_type in ['sqlite']:
            python_type = json_validator
        else:
            python_type = str
    value = python_type(value)
    return column.__ne__(value)


def equal_null_query(
        column, value, python_type=str, dialect_type='sqlite'
) -> Tuple[Optional[str], Union[tuple, None]]:
    """
    `[?]` : 空值查询, `[=?]` or `[?]`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    return column.is_(None)


def not_equal_null_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[!?]` : 非空查询, `[!?]` or `[!=?]`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    return column.is_not(None)


def like_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[~]` : 模糊查询, like, `[~]abc`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if dialect_type in ['postgresql'] and _is_json_type(python_type):
        # SELECT * FROM :table_name WHERE EXISTS
        # (SELECT count(*) FROM jsonb_array_elements_text(:column_name) WHERE value like '%2%')
        value = cast(f"%{value}%", String)
        tmp = func.jsonb_array_elements_text(column).table_valued("value")
        return exists(select(tmp).where(tmp.c.value.like(value)))
    if _is_json_type(python_type) or _is_str_type(python_type):
        value = cast(f"%{value}%", String)
        return column.like(value)
    else:
        return None


def not_like_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[!~]` : 模糊查询, not like, `[!~]abc`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if dialect_type in ['postgresql'] and _is_json_type(python_type):
        # SELECT * FROM :table_name WHERE NOT EXISTS
        # (SELECT count(*) FROM jsonb_array_elements_text(:column_name) WHERE value like '%2%')
        value = cast(f"%{value}%", String)
        tmp = func.jsonb_array_elements_text(column).table_valued("value")
        return not_(exists(select(tmp).where(tmp.c.value.like(value))))
    if _is_json_type(python_type) or _is_str_type(python_type):
        value = cast(f"%{value}%", String)
        return column.not_like(value)
    else:
        return None


def in_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[*]` : 在范围内, in, `[*]abc,def,gh`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        else:
            python_type = str
    value = list(map(python_type, set(split_str_comma(value))))
    return column.in_(value)


def not_in_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[!*]` : 不在范围内, not in, `[!*]abc,def,gh`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        else:
            python_type = str
    value = list(map(python_type, set(split_str_comma(value))))
    return column.not_in(value)


def less_than_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[<]` : 小于, `[<]100`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        return None
    value = python_type(value)
    return column.__lt__(value)


def less_equal_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[<=]` : 小于等于, `[<=]100`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        return None
    value = python_type(value)
    return column.__le__(value)


def greater_than_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[>]` : 大于, `[>]100`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        return None
    value = python_type(value)
    return column.__gt__(value)


def greater_equal_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[>=]` : 大于等于, `[>=]100`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        return None
    value = python_type(value)
    return column.__ge__(value)


def between_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[-]` : 范围查询, between, `[-]100,300`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        return None
    value = split_str_comma(value)[:2]
    if len(value) < 2:
        value = [0, *value]
    value = tuple(map(python_type, value))
    return column.between(*value)


def startswith_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[^]` : 以...开头, `[^]abc`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_str_type(python_type):
        return column.startswith(value)
    else:
        return None


def endswith_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[$]` : 以...结尾, `[$]abc`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_str_type(python_type):
        return column.endswith(value)
    else:
        return None


def regex_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[$]` : 以...结尾, `[$]abc`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_str_type(python_type):
        return column.regexp_match(value)
    else:
        return None


def json_contains_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[@]` : Json包含, json_contains, `[@]abc,[def,gh],{asd,add}`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        elif dialect_type in ['sqlite']:
            python_type = json_validator
        value = list(map(python_type, set(split_str_comma(value))))

        if dialect_type in ['mysql']:
            ws = [func.json_contains(column, v) for v in value]
            return or_(*ws)
        if dialect_type in ['postgresql']:
            ws = [func.jsonb_contains(column, v) for v in value]
            return or_(*ws)
        if dialect_type in ['sqlite']:
            ws = []
            for v in value:
                if isinstance(v, list):
                    ws.append(text(
                        f"(SELECT count(*) FROM json_each({column.name}) WHERE value IN {tuple(v)}) = {len(v)}"
                    ))
                else:
                    ws.append(text(
                        f"EXISTS (SELECT * FROM json_each({column.name}) WHERE value = {v})"
                    ))

            return or_(*ws)
        else:
            return None
    else:
        return None


def not_json_contains_value_query(column, value, python_type=str, dialect_type='sqlite'):
    """
    `[!@]` : Json不包含, not json_contains, `[!@]abc,[def,gh],{asd,add}`
    :param column:
    :param value:
    :param python_type:
    :param dialect_type:
    :return:
    """
    if _is_json_type(python_type):
        if dialect_type in ['mysql', 'postgresql']:
            python_type = _python_to_table_json
        elif dialect_type in ['sqlite']:
            python_type = json_validator
        value = list(map(python_type, set(split_str_comma(value))))

        if dialect_type in ['mysql']:
            ws = [not_(func.json_contains(column, v)) for v in value]
            return and_(*ws)
        if dialect_type in ['postgresql']:
            ws = [not_(func.jsonb_contains(column, v)) for v in value]
            return and_(*ws)
        if dialect_type in ['sqlite']:
            ws = []
            for v in value:
                if isinstance(v, list):
                    ws.append(text(
                        f"(SELECT count(*) FROM json_each({column.name}) WHERE value IN {tuple(v)}) != {len(v)}"
                    ))
                else:
                    ws.append(text(
                        f"NOT EXISTS (SELECT * FROM json_each({column.name}) WHERE value = {v})"
                    ))
            return and_(*ws)
        else:
            return None
    else:
        return None


sql_operator_pattern: Pattern = re.compile(r"^\[(=|<=|<|>|>=|!|!=|<>|\*|!\*|~|!~|-|\^|\$|#|\?|=\?|!\?|!=\?|@|!@)]")
sql_operator_map: dict = {
    "=": equal_value_query,
    "<=": less_equal_value_query,
    "<": less_than_value_query,
    ">": greater_than_value_query,
    ">=": greater_equal_value_query,
    "!": not_equal_value_query,
    "!=": not_equal_value_query,
    "<>": not_equal_value_query,
    "*": in_value_query,
    "!*": not_in_value_query,
    "~": like_value_query,
    "!~": not_like_value_query,
    "-": between_value_query,
    "^": startswith_value_query,
    "$": endswith_value_query,
    "#": regex_value_query,
    "?": equal_null_query,
    "=?": equal_null_query,
    "!?": not_equal_null_query,
    "!=?": not_equal_null_query,
    "@": json_contains_value_query,
    "!@": not_json_contains_value_query,
}
__sql_operator_docs = """
## 查询条件：
`[=]` : 等于, `abc` or `[=]abc`, 等于空字符串：`[=]`
`[!=]` : 不等, `[!]abc` or `[!=]abc`, 不等于空字符串：`[!]` or `[!=]`
`[?]` : 空值查询, `[=?]` or `[?]`
`[!?]` : 非空查询, `[!?]` or `[!=?]`
`[~]` : 模糊查询, like, `[~]abc`
`[!~]` : 模糊查询, not like, `[!~]abc`
`[*]` : 在范围内, in, `[*]abc,def,gh`
`[!*]` : 不在范围内, not in, `[!*]abc,def,gh`
`[@]` : Json包含, json_contains, `[@]abc,[def,gh],{asd,add}`
`[!@]` : Json不包含, not json_contains, `[!@]abc,[def,gh],{asd,add}`
`[<]` : 小于, `[<]100`
`[<=]` : 小于等于, `[<=]100`
`[>]` : 大于, `[>]100`
`[>=]` : 大于等于, `[>=]100`
`[-]` : 范围查询, between, `[-]100,300`
`[^]` : 以...开头, `[^]abc`
`[$]` : 以...结尾, `[$]abc`
`[#]` : 正则查询, `[#]regex`
## 排序
`+` : 正序, `create_time` or `+create_time`
`-` : 倒序, `-create_time`
`,` : 多字段, `create_time,-id`
"""

sql_operator_docs = markdown.fold_contents(markdown.str2markdown(__sql_operator_docs), "查询参数示例")


class Selector:
    Model: Type[SQLModel]

    def __call__(self, *args, **kwargs):
        pass

    def calc_filter_clause(self, dialect_type='sqlite'):
        queries = []
        errors = []
        for name, value in self.__dict__.items():
            if value:
                model_field = model_fields(self.Model).get(name, None)
                python_type = get_python_type_parse(model_field)
                column = getattr(self.Model, name)

                try:
                    match = sql_operator_pattern.match(value)
                    op_key = match.group(1) if match else '='
                    query_func = sql_operator_map.get(op_key)
                    value = value.replace(f"[{op_key}]", "")
                    query = query_func(column, value, python_type, dialect_type)
                    if query is not None:
                        queries.append(query)
                except ValueError as e:
                    errors.append(
                        {
                            "type": "type_error",
                            "loc": ("query", name),
                            "msg": "JSON decode error",
                            "input": f"Input should be a valid {python_type}, invalid {value}",
                            "ctx": {"error": e},
                        }
                    )
        if errors:
            raise RequestValidationError(errors)
        return queries


class Paginator:
    def __init__(
            self,
            page_size_default: int = 1,
            page_size_max: int = None,
    ):
        self.page_size_default = page_size_default
        self.page_size_max = page_size_max

        self.page: int = 1
        self.page_size: int = page_size_default
        self.show_total: bool = True
        self.order_by = None

    def __call__(self):
        page_size_default = self.page_size_default
        page_size_max = self.page_size_max

        def paginate(
                page: int = Query(1, ge=1, title='page'),
                page_size: int = Query(page_size_default, title='page size', ge=1, le=page_size_max),
                order_by: OrderByListDepend = None,
                show_total: bool = Query(True, title='show total?'),
        ):
            self.page = page
            self.page_size = page_size
            self.order_by = order_by
            self.show_total = show_total
            return self

        return paginate

    def calc_ordering(self):
        order = []
        for ob in self.order_by:
            if isinstance(ob, str) and ob.startswith("-"):
                order.append(desc(ob[1:]))
            elif isinstance(ob, str) and ob.startswith("+"):
                order.append(ob[1:])
            else:
                order.append(ob)

        return order


class Foreign:
    Model: Type[SQLModel]
    inner_foreign_models: List[Type[SQLModel]]
    foreign: List[Type[SQLModel]] = []

    def __call__(self, *args, **kwargs):
        pass


def sqlmodel_to_foreign(
        model: Type[SQLModel],
) -> Type[Foreign]:
    inner_foreign_models = get_foreign_models(model)
    foreign_model_name_enums = {fm.__tablename__: fm.__tablename__ for fm in inner_foreign_models}
    if foreign_model_name_enums:
        func = f"""
def call(
    self,
    join: List[Enum("enum", {foreign_model_name_enums})] = Query(None, title='外连接', description=f'`join`')
):
    if join is None:
        self.foreign = []
        return self
    foreign_models = [foreign.name for foreign in join]
    self.foreign = [fm for fm in self.inner_foreign_models if fm.__tablename__ in foreign_models]
    return self
    """
    else:
        func = f"""
def call(
    self,
):
    self.foreign = []
    return self
    """
    exec(func, globals())

    return type(
        f'{model.__name__}Foreign',
        (Foreign,),
        {
            'Model': model,
            'inner_foreign_models': inner_foreign_models.keys(),
            '__call__': call  # type: ignore
        }
    )


def sqlmodel_to_selector(
        base_model: Type[SQLModel],
) -> Type[Selector]:
    params = []
    methods = []
    for name, field in model_fields(base_model).items():
        field_info = field.field_info
        if getattr(field_info, 'query', False) is False:
            continue
        if getattr(field_info, 'primary_key', False) is True:
            params.append(f"{name}: str = Query(None, alias='primary_key', "
                          f"description='`{base_model.__name__}.{name}`: 主键')")
            methods.append(f"self.{name} = {name}")
        else:
            params.append(
                f"""{name}: str = Query(None,
                    gt={getattr(field_info, 'gt', None)},
                    ge={getattr(field_info, 'ge', None)},
                    lt={getattr(field_info, 'lt', None)},
                    le={getattr(field_info, 'le', None)},
                    min_length={getattr(field_info, 'min_length', None)},
                    max_length={getattr(field_info, 'max_length', None)},
                    max_digits={getattr(field_info, 'max_digits', Undefined)},
                    decimal_places={getattr(field_info, 'decimal_places', Undefined)},
                  description="`{base_model.__name__}.{name}`: {field_info.title}")"""
            )
            methods.append(f"self.{name} = {name}")
    func = f"""
def call(
    self,
    {",".join(set(params))}
):
    {";".join(set(methods))}
    return self
    """
    exec(func, globals())

    return type(
        f'{base_model.__name__}Selector',
        (Selector,),
        {
            'Model': base_model,
            '__call__': call  # type: ignore
        }
    )
