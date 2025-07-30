# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _models.py
# @Time     : 2023/10/29 15:45
from typing import Type, Union, Dict

from pydantic import BaseModel
from sqlmodel import SQLModel

from fastapix.pkg.pydantic import (
    PYDANTIC_V2, ModelField,
    create_model_by_fields, model_fields, PydanticUndefined
)


def create_schema_read(model: Type[SQLModel], foreign_models: Dict[Type[SQLModel], str] = None) -> Type[BaseModel]:
    fields = []
    for name, field in model_fields(model).items():
        if foreign_models and name in foreign_models.values():
            foreign_key = getattr(field.field_info, "foreign_key", PydanticUndefined)
            field.field_info.annotation = Union[field.field_info.annotation, create_schema_read(foreign_key.class_)]
            mf = ModelField(
                field_info=field.field_info,
                name=field.name
            )
            fields.append(mf)
        if getattr(field.field_info, 'read', True):
            fields.append(field)
    return create_model_by_fields(
        name=f"{model.__name__}Read",
        fields=fields,
        orm_mode=True,
        extra="allow",
        mode="read",
        __config__=model.model_config if PYDANTIC_V2 else model.Config
    )


def create_schema_update(model: Type[SQLModel]) -> Type[BaseModel]:
    fields = [
        field
        for name, field in model_fields(model).items()
        if getattr(field.field_info, 'update', True)
    ]
    return create_model_by_fields(
        name=f"{model.__name__}Update",
        fields=fields,
        set_none=True,
        __config__=model.model_config if PYDANTIC_V2 else model.Config
    )


def create_schema_create(model: Type[SQLModel]) -> Type[BaseModel]:
    fields = [
        field
        for name, field in model_fields(model).items()
        if getattr(field.field_info, 'create', True)
    ]
    return create_model_by_fields(
        name=f"{model.__name__}Create",
        fields=fields,
        __config__=model.model_config if PYDANTIC_V2 else model.Config
    )


def get_foreign_models(model: Type[SQLModel]) -> Dict[Type[SQLModel], str]:
    foreign_models = {}
    for name, field in model_fields(model).items():
        foreign_key = getattr(field.field_info, "foreign_key", PydanticUndefined)
        if foreign_key is not PydanticUndefined:
            foreign_models[foreign_key.class_] = name
    return foreign_models
