# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : router.py
# @Time     : 2023/10/12 9:48
from typing import List, Type, TypeVar, Generic, Optional

from fastapi import APIRouter, Body, Path, Depends, Query
from fastapi.requests import Request
from pydantic import BaseModel
from typing_extensions import Annotated

from fastapix.pkg.pydantic import (
    GenericModel, Undefined,
    model_fields, get_type_from_field
)
from fastapix.crud._selecter import (
    RequiredPrimaryKeyListDepend, Paginator, Selector,
    sqlmodel_to_selector, sql_operator_docs, Foreign,
    sqlmodel_to_foreign
)
from fastapix.crud._sqlmodel import SQLModel
from fastapix.responses import GenericData, DataResponse

ReadModel = TypeVar('ReadModel')


class InnerItemsData(GenericModel, Generic[ReadModel]):
    items: List[ReadModel]
    total: int


class CrudRouterManager:

    def __init__(
            self,
            crud: "SQLAlchemyCrud",
    ):
        self.crud = crud

        self.Selector: Type[Selector] = sqlmodel_to_selector(crud.Model)
        self.Foreign: Type[Foreign] = sqlmodel_to_foreign(crud.Model)

        self.inner_tag = f"{self.crud.Model.__name__}{f':{self.crud.Model.__doc__}' if self.crud.Model.__doc__ else ''}"
        self.self_prefix = f"/{self.crud.name.lower()}"

    def json_schema_router(
            cls,
    ) -> APIRouter:
        """
        获取 model schema
        :return:
        """
        router = APIRouter(prefix=f"{cls.self_prefix}/json/schema", tags=[cls.inner_tag])

        @router.get(
            "",
            response_model=GenericData[dict],
            name=f'get {cls.crud.name} schema',
        )
        async def __get_schema(
        ):
            return DataResponse(data=cls.crud.Model.schema())

        return router

    def create_object_router(
            cls,
    ) -> APIRouter:
        """
        创建数据
        :return:
        """
        router = APIRouter(prefix=cls.self_prefix, tags=[cls.inner_tag])
        docs = []
        for name, f in model_fields(cls.crud.CreateModel).items():
            required = ''
            if f.default is Undefined:
                required = '<font color=red><sup><b>*</b> required</sup></font>'
            docs.append(f"""`{cls.crud.Model.__name__}.{name}`{required}：{f.field_info.title}""")
            type_ = get_type_from_field(f)
            if issubclass(type_, (BaseModel, SQLModel)):
                for _name, _f in model_fields(type_).items():
                    _required = ''
                    if _f.default is Undefined:
                        _required = '<font color=red><sup><b>*</b> required</sup></font>'
                    docs.append(f"""`{cls.crud.Model.__name__}.{name}.{_name}`{_required}：{_f.field_info.title}""")

        @router.post(
            "",
            response_model=GenericData[InnerItemsData[cls.crud.ReadModel]],
            name=f'create {cls.crud.name}',
            description="\n\n".join(docs)
        )
        async def __create_object(
                request: Request,
                objs: List[cls.crud.CreateModel] = Body(...),
        ):
            objs: List[cls.crud.ReadModel] = await cls.crud.create_items(items=objs, request=request)
            return DataResponse(data=InnerItemsData(
                items=objs,
                total=len(objs)
            ))

        return router

    def read_object_router(
            cls,
            page_size_default: Optional[int] = None,
            page_size_max: Optional[int] = None,
    ) -> APIRouter:
        """
        读取数据
        :param: page_size_default: None or <=0 不限制 limit
        :return:
        """
        router = APIRouter(prefix=cls.self_prefix, tags=[cls.inner_tag])

        @router.get(
            "",
            response_model=GenericData[InnerItemsData[cls.crud.ReadModel]],
            name=f'get {cls.crud.name} all',
            description=sql_operator_docs
        )
        async def __get_objects(
                request: Request,
                selector: Annotated[cls.Selector, Depends(cls.Selector())],
                foreign: Annotated[cls.Foreign, Depends(cls.Foreign())],
                paginator: Annotated[Paginator, Depends(Paginator(page_size_default, page_size_max)())],
        ):
            objs, total = await cls.crud.read_items(
                request=request, selector=selector, paginator=paginator, foreign=foreign
            )
            return DataResponse(data=InnerItemsData(
                items=objs,
                total=total
            ))

        @router.get(
            f"/{{{cls.crud.pk_name}}}",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'get {cls.crud.name} by primary_key({cls.crud.pk_name})'
        )
        async def __get_object(
                request: Request,
                primary_key: cls.crud.pk_modelfield.type_ = Path(..., alias=cls.crud.pk_name)
        ):
            obj = await cls.crud.read_item_by_primary_key(primary_key=primary_key, request=request)
            return DataResponse(data=obj)

        return router

    def update_object_router(
            cls,
    ) -> APIRouter:
        """
        更新数据
        :return:
        """
        router = APIRouter(prefix=cls.self_prefix, tags=[cls.inner_tag])

        @router.patch(
            f"/{{{cls.crud.pk_name}}}",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'update {cls.crud.name} by primary_key({cls.crud.pk_name})',
            include_in_schema=False
        )
        @router.put(
            f"/{{{cls.crud.pk_name}}}",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'update {cls.crud.name} by primary_key({cls.crud.pk_name})',
        )
        async def __update_object(
                request: Request,
                primary_key: cls.crud.pk_modelfield.type_ = Path(..., alias=cls.crud.pk_name),
                obj_update: cls.crud.UpdateModel = Body(...),
        ):
            obj = await cls.crud.update_items(primary_key=[primary_key], item=obj_update, request=request)
            return DataResponse(data=obj)

        @router.patch(
            "",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'update {cls.crud.name}s by primary_keys({cls.crud.pk_name})',
            include_in_schema=False
        )
        @router.put(
            "",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'update {cls.crud.name}s by primary_keys({cls.crud.pk_name})',
        )
        async def __update_object(
                request: Request,
                primary_key: List[cls.crud.pk_modelfield.type_] = Query(..., alias=cls.crud.pk_name),
                obj_update: cls.crud.UpdateModel = Body(...),
        ):
            obj = await cls.crud.update_items(primary_key=primary_key, item=obj_update, request=request)
            return DataResponse(data=obj)


        return router

    def delete_object_router(
            cls,
    ) -> APIRouter:
        """
        删除数据
        :return:
        """
        router = APIRouter(prefix=cls.self_prefix, tags=[cls.inner_tag])

        @router.delete(
            f"/{{{cls.crud.pk_name}}}",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'delete {cls.crud.name} by primary_key({cls.crud.pk_name})',
        )
        async def __delete_object(
                request: Request,
                primary_key: cls.crud.pk_modelfield.type_ = Path(..., alias=cls.crud.pk_name),
        ):
            objs = await cls.crud.delete_items(request=request, primary_key=[primary_key])
            return DataResponse(data=objs)

        @router.delete(
            "",
            response_model=GenericData[cls.crud.ReadModel],
            name=f'delete {cls.crud.name}s by primary_keys({cls.crud.pk_name})',
        )
        async def __delete_object(
                request: Request,
                primary_key: List[cls.crud.pk_modelfield.type_] = Query(..., alias=cls.crud.pk_name),
        ):
            objs = await cls.crud.delete_items(request=request, primary_key=primary_key)
            return DataResponse(data=objs)
        return router
