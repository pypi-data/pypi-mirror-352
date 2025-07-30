# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _sqlalchemy.py.py
# @Time     : 2023/10/11 16:11
from typing import List, Dict, Any, TypeVar, Optional, Type, Tuple, Union, Mapping, Sequence

from fastapi.requests import Request
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, Result, Executable, Dialect, Select, Row
from sqlalchemy.orm import object_session, InstrumentedAttribute
from sqlmodel import SQLModel, select, Session

from fastapix.pkg.pydantic import model_validate, model_dump, model_fields, ModelField
from fastapix.crud._models import create_schema_create, create_schema_read, create_schema_update, get_foreign_models
from fastapix.crud._selecter import get_modelfield_by_alias, Selector, Paginator, Foreign
from fastapix.crud.database import SqlalchemyDatabase, EngineDatabase

TableModel = TypeVar('TableModel', bound=SQLModel)

EMPTY_LIST: list = []


class SQLAlchemyCrud:

    def __init__(
            self, model: Type[TableModel], engine: SqlalchemyDatabase,
    ):
        self.Model = model
        assert self.Model, "model is None"
        assert hasattr(self.Model, "__table__"), "model must be has __table__ attribute."
        self.__table__ = self.Model.__table__  # type: ignore
        self.__fields__ = model_fields(self.Model)
        self.pk_name: str = self.__table__.primary_key.columns.keys()[0]
        self.pk: InstrumentedAttribute = self.Model.__dict__[self.pk_name]
        self.pk_modelfield: ModelField = self.__fields__[self.pk_name]

        self.db = EngineDatabase(engine)
        self.dialect: Dialect = self.db.engine.dialect

        self.name = model.__name__
        logger.info(f"Building table {{{self.name}}} RESTful API...")
        self.CreateModel: Type[BaseModel] = create_schema_create(model)
        self.foreign_models = get_foreign_models(self.Model)
        self.ReadModel: Type[BaseModel] = create_schema_read(model, self.foreign_models)
        self.UpdateModel: Type[BaseModel] = create_schema_update(model)

    def select(self, foreign: List[Type[SQLModel]] = None) -> Select:
        if foreign:
            sel = select(self.Model, *foreign)
            for model in foreign:
                sel = sel.join(model)
        else:
            sel = select(self.Model)
        return sel

    def _fetch_item_scalars(self, session: Session, query=None) -> Sequence[TableModel]:
        sel = self.select()
        if query is not None:
            sel = sel.filter(query)
        return session.scalars(sel).all()

    def pyobj_to_table(self, item: BaseModel) -> TableModel:
        return self.Model(**model_dump(item))

    def table_to_pyobj(self, obj: Union[TableModel, Row], foreign: list = None) -> BaseModel:
        if isinstance(obj, Row):
            obj, *f = obj
            if foreign:
                foreign = {self.foreign_models.get(k): v for k, v in zip(foreign, f)}
                obj = obj.dict()
                obj.update(foreign)
        return model_validate(self.ReadModel, obj, from_attributes=True)

    def _update_item(self, obj: TableModel, values: Dict[str, Any]):
        if isinstance(obj, dict):
            for k, v in values.items():
                obj[k] = v
        else:
            for k, v in values.items():
                field = get_modelfield_by_alias(self.Model, k)
                if not field and not hasattr(obj, k):
                    continue
                name = field.name if field else k
                setattr(obj, name, v)
        return obj

    def _delete_item(self, obj: TableModel) -> None:
        object_session(obj).delete(obj)

    def _create_items(self, session: Session, items: List[BaseModel]) -> List[BaseModel]:
        if not items:
            return []
        objs = [self.pyobj_to_table(item) for item in items]
        session.add_all(objs)
        session.flush()
        results = [self.table_to_pyobj(obj) for obj in objs]
        return results

    async def create_items(
            self, items: List[BaseModel], request: Request = None,
    ) -> List[BaseModel]:
        results = await self.db.async_run(self._create_items, items)
        return results

    def _read_items(self, session: Session, query=None) -> List[BaseModel]:
        items = self._fetch_item_scalars(session, query)
        return [self.table_to_pyobj(obj) for obj in items]

    async def read_item_by_primary_key(self, primary_key: Any) -> BaseModel:
        query = self.pk == primary_key
        items = await self.db.async_run(self._read_items, query)
        return items[0] if len(items) == 1 else None

    async def read_items(
            self,
            selector: Selector = None,
            paginator: Paginator = None,
            foreign: Foreign = None,
    ) -> Tuple[List[BaseModel], int]:
        sel = self.select(foreign.foreign if foreign else [])
        if selector:
            selector = selector.calc_filter_clause(self.dialect.name)
            if selector:
                sel = sel.filter(*selector)
        total = -1
        if paginator:
            if paginator.show_total:
                total = await self.db.async_scalar(
                    select(func.count("*")).select_from(sel.with_only_columns(self.pk).subquery())
                )

            order_by = paginator.calc_ordering()
            if order_by:
                sel = sel.order_by(*order_by)
            if paginator.page_size and paginator.page_size > 0:
                sel = sel.limit(paginator.page_size).offset((paginator.page - 1) * paginator.page_size)

        results = await self.db.async_execute(sel)
        results = results.all()
        results = [self.table_to_pyobj(r, foreign.foreign) for r in results]
        return results, total

    def _update_items(
            self, session: Session, primary_key: List[Any], values: Dict[str, Any], query=None
    ) -> Sequence[BaseModel]:
        query = query or self.pk.in_(primary_key)
        objs = self._fetch_item_scalars(session, query)
        results = []
        for obj in objs:
            self._update_item(obj, values)
            results.append(self.table_to_pyobj(obj))
        return results

    async def update_items(
            self, primary_key: List[Any], item: BaseModel,
    ) -> List[BaseModel]:
        results = await self.db.async_run(
            self._update_items, primary_key, model_dump(item, exclude_unset=True), None
        )
        return results

    def _delete_items(self, session: Session, primary_key: List[Any]) -> Sequence[BaseModel]:
        query = self.pk.in_(primary_key)
        objs = self._fetch_item_scalars(session, query)
        results = []
        for obj in objs:
            self._delete_item(obj)
            results.append(self.table_to_pyobj(obj))
        return results

    async def delete_items(
            self, primary_key: List[Any],
            request: Request = None
    ) -> List[BaseModel]:
        results = await self.db.async_run(self._delete_items, primary_key)
        return results

    async def async_execute(
            self,
            statement: Executable,
            params: Optional[Union[Mapping[Any, Any], List[Mapping[Any, Any]]]] = None,
            execution_options: Optional[Mapping[Any, Any]] = None,
            bind_arguments: Optional[Mapping[str, Any]] = None,
            **kwargs: Any,
    ) -> Result:
        return await self.db.async_execute(
            statement=statement, params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments, **kwargs
        )

