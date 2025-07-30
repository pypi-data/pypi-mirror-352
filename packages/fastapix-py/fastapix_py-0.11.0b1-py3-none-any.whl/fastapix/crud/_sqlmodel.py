# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : sqlmodel.py
# @Time     : 2023/10/29 18:47
import ipaddress
import types
import uuid
from datetime import datetime, date, timedelta, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Optional, Union, AbstractSet, Mapping, Sequence,
    Any, Callable, Dict, List, Set, Tuple, Type, cast, get_origin,
)

from pydantic import BaseConfig, BaseModel, EmailStr
from sqlalchemy import (
    Column, inspect, DefaultClause,
    Integer, Boolean, false, true, Enum as sa_Enum, Float, DateTime, Date,
    Interval, Time, LargeBinary, Numeric, ForeignKey, Uuid
)
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import (
    ColumnProperty,
    declared_attr,
    relationship, registry, Mapped,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.util import classproperty, memoized_property
from sqlmodel import AutoString
from sqlmodel._compat import (
    get_annotations, get_config_value,
    set_config_value,
    is_table_model_class, get_relationship_to,
    IS_PYDANTIC_V2, UndefinedType,
    ModelMetaclass, finish_init, SQLModelConfig
)
from sqlmodel.main import FieldInfo as _FieldInfo, SQLModel as _SQLModel, NoArgAnyCallable
from sqlmodel.main import RelationshipInfo as RelationshipInfo
from sqlmodel.main import SQLModelMetaclass as _SQLModelMetaclass

from fastapix.pkg.pydantic import (
    Undefined, ModelField, FieldInfo,
    model_fields as get_model_fields,
    get_type_from_field,
    is_field_noneable, sqlmodel_init
)
from fastapix.crud._sqltypes import AutoJson

try:
    from functools import cached_property
except ImportError:
    cached_property = memoized_property

SaColumnTypes = (
    Column,
    ColumnProperty,
    hybrid_property,
    declared_attr,
)

__sqlmodel_ignored_types__ = (classproperty, cached_property, memoized_property, hybrid_method, *SaColumnTypes)


def get_column_from_field(field: ModelField) -> Column:  # type: ignore
    sa_column = getattr(field.field_info, "sa_column", Undefined)
    if isinstance(sa_column, (Column, SaColumnTypes)):
        return sa_column
    if field.default and isinstance(field.default, SaColumnTypes):
        return field.default
    sa_type = get_sqlalchemy_type(field)
    primary_key = getattr(field.field_info, "primary_key", Undefined)

    if primary_key is Undefined:
        primary_key = False
    index = getattr(field.field_info, "index", Undefined)
    if index is Undefined:
        index = False
    nullable = not primary_key and is_field_noneable(field)
    # Override derived nullability if the nullable property is set explicitly
    # on the field
    field_nullable = getattr(field.field_info, "nullable", Undefined)  # noqa: B009
    if field_nullable is not Undefined:
        assert not isinstance(field_nullable, UndefinedType)
        nullable = field_nullable
    args = []
    foreign_key = getattr(field.field_info, "foreign_key", Undefined)
    if foreign_key is Undefined:
        foreign_key = None
    unique = getattr(field.field_info, "unique", Undefined)
    if unique is Undefined:
        unique = False
    if foreign_key:
        args.append(ForeignKey(foreign_key))
    kwargs = {
        "primary_key": primary_key,
        "nullable": nullable,
        "index": index,
        "unique": unique,
    }
    sa_default = Undefined
    if field.field_info.default_factory:
        sa_default = field.field_info.default_factory
    elif field.field_info.default is not Undefined:
        sa_default = field.field_info.default
    if sa_default is not Undefined:
        kwargs["default"] = sa_default
    sa_column_args = getattr(field.field_info, "sa_column_args", Undefined)
    if sa_column_args is not Undefined:
        args.extend(list(cast(Sequence[Any], sa_column_args)))
    sa_column_kwargs = getattr(field.field_info, "sa_column_kwargs", Undefined)
    if sa_column_kwargs is not Undefined:
        kwargs.update(cast(Dict[Any, Any], sa_column_kwargs))
    return Column(sa_type, *args, **kwargs)  # type: ignore


class _SQLModelBasesInfo:
    def __init__(self, bases):
        self.is_table = False
        self.tablename = None
        self.columns = {}
        self.sqlmodel_relationships = {}
        for base in bases:
            config = getattr(base, "__config__", None)
            if config and getattr(config, "table", False):
                self.is_table = True
                self.tablename = base.__tablename__
                # noinspection PyProtectedMember
                self.columns.update(base.__table__.columns._index)
                self.sqlmodel_relationships.update(base.__sqlmodel_relationships__)


class SQLModelMetaclass(_SQLModelMetaclass):
    # From Pydantic
    def __new__(
            cls,
            name: str,
            bases: Tuple[Type[Any], ...],
            class_dict: Dict[str, Any],
            **kwargs: Any,
    ) -> Any:
        relationships: Dict[str, RelationshipInfo] = {}
        dict_for_pydantic = {}
        original_annotations = get_annotations(class_dict)
        pydantic_annotations = {}
        relationship_annotations = {}
        for k, v in class_dict.items():
            if isinstance(v, RelationshipInfo):
                relationships[k] = v
            else:
                dict_for_pydantic[k] = v
        for k, v in original_annotations.items():
            if k in relationships:
                relationship_annotations[k] = v
            else:
                pydantic_annotations[k] = v
        dict_used = {
            **dict_for_pydantic,
            "__weakref__": None,
            "__sqlmodel_relationships__": relationships,
            "__annotations__": pydantic_annotations,
        }
        # Duplicate logic from Pydantic to filter config kwargs because if they are
        # passed directly including the registry Pydantic will pass them over to the
        # superclass causing an error
        allowed_config_kwargs: Set[str] = {
            key
            for key in dir(BaseConfig)
            if not (
                    key.startswith("__") and key.endswith("__")
            )  # skip dunder methods and attributes
        }
        config_kwargs = {
            key: kwargs[key] for key in kwargs.keys() & allowed_config_kwargs
        }
        new_cls = super().__new__(cls, name, bases, dict_used, **config_kwargs)
        new_cls.__annotations__ = {
            **relationship_annotations,
            **pydantic_annotations,
            **new_cls.__annotations__,
        }

        def get_config(name: str) -> Any:
            config_class_value = get_config_value(
                model=new_cls, parameter=name, default=Undefined
            )
            if config_class_value is not Undefined:
                return config_class_value
            kwarg_value = kwargs.get(name, Undefined)
            if kwarg_value is not Undefined:
                return kwarg_value
            return Undefined

        config_table = get_config("table")
        if config_table is True:
            # If it was passed by kwargs, ensure it's also set in config
            set_config_value(model=new_cls, parameter="table", value=config_table)
            for k, v in get_model_fields(new_cls).items():
                if not hasattr(new_cls, k):
                    col = get_column_from_field(v)
                    setattr(new_cls, k, col)
            # Set a config flag to tell FastAPI that this should be read with a field
            # in orm_mode instead of preemptively converting it to a dict.
            # This could be done by reading new_cls.model_config['table'] in FastAPI, but
            # that's very specific about SQLModel, so let's have another config that
            # other future tools based on Pydantic can use.
            set_config_value(
                model=new_cls, parameter="read_from_attributes", value=True
            )
            # For compatibility with older versions
            # TODO: remove this in the future
            set_config_value(model=new_cls, parameter="read_with_orm_mode", value=True)

        config_registry = get_config("registry")
        if config_registry is not Undefined:
            config_registry = cast(registry, config_registry)
            # If it was passed by kwargs, ensure it's also set in config
            set_config_value(model=new_cls, parameter="registry", value=config_table)
            setattr(new_cls, "_sa_registry", config_registry)  # noqa: B010
            setattr(new_cls, "metadata", config_registry.metadata)  # noqa: B010
            setattr(new_cls, "__abstract__", True)  # noqa: B010
        return new_cls

    # Override SQLAlchemy, allow both SQLAlchemy and plain Pydantic models
    def __init__(
            cls, classname: str, bases: Tuple[type, ...], dict_: Dict[str, Any], **kw: Any
    ) -> None:
        # Only one of the base classes (or the current one) should be a table model
        # this allows FastAPI cloning a SQLModel for the response_model without
        # trying to create a new SQLAlchemy, for a new table, with the same name, that
        # triggers an error
        _bases = _SQLModelBasesInfo(bases)
        if is_table_model_class(cls):
            for rel_name, rel_info in cls.__sqlmodel_relationships__.items():
                if rel_info.sa_relationship:
                    # There's a SQLAlchemy relationship declared, that takes precedence
                    # over anything else, use that and continue with the next attribute
                    setattr(cls, rel_name, rel_info.sa_relationship)  # Fix #315
                    continue
                raw_ann = cls.__annotations__[rel_name]
                origin = get_origin(raw_ann)
                if origin is Mapped:
                    ann = raw_ann.__args__[0]
                else:
                    ann = raw_ann
                    # Plain forward references, for models not yet defined, are not
                    # handled well by SQLAlchemy without Mapped, so, wrap the
                    # annotations in Mapped here
                    cls.__annotations__[rel_name] = Mapped[ann]  # type: ignore[valid-type]
                relationship_to = get_relationship_to(
                    name=rel_name, rel_info=rel_info, annotation=ann
                )
                rel_kwargs: Dict[str, Any] = {}
                if rel_info.back_populates:
                    rel_kwargs["back_populates"] = rel_info.back_populates
                if rel_info.link_model:
                    ins = inspect(rel_info.link_model)
                    local_table = getattr(ins, "local_table")  # noqa: B009
                    if local_table is None:
                        raise RuntimeError(
                            "Couldn't find the secondary table for "
                            f"model {rel_info.link_model}"
                        )
                    rel_kwargs["secondary"] = local_table
                rel_args: List[Any] = []
                if rel_info.sa_relationship_args:
                    rel_args.extend(rel_info.sa_relationship_args)
                if rel_info.sa_relationship_kwargs:
                    rel_kwargs.update(rel_info.sa_relationship_kwargs)
                rel_value = relationship(relationship_to, *rel_args, **rel_kwargs)
                setattr(cls, rel_name, rel_value)  # Fix #315
            # SQLAlchemy no longer uses dict_
            # Ref: https://github.com/sqlalchemy/sqlalchemy/commit/428ea01f00a9cc7f85e435018565eb6da7af1b77
            # Tag: 1.4.36
            DeclarativeMeta.__init__(cls, classname, bases, dict_, **kw)
            if _bases.is_table:
                cls.__sqlmodel_relationships__.update(cls._bases.sqlmodel_relationships)
        else:
            ModelMetaclass.__init__(cls, classname, bases, dict_)


class SQLModel(_SQLModel, metaclass=SQLModelMetaclass):
    __table_args__ = {"extend_existing": True}
    if IS_PYDANTIC_V2:
        model_config = SQLModelConfig(
            from_attributes=True,
            ignored_types=__sqlmodel_ignored_types__,
        )
    else:
        class Config:
            orm_mode = True
            keep_untouched = __sqlmodel_ignored_types__

    def __init__(__pydantic_self__, **data: Any) -> None:
        if finish_init.get():
            sqlmodel_init(self=__pydantic_self__, data=data)


class FieldInfo(_FieldInfo):

    def __init__(self, default: Any = Undefined, **kwargs: Any) -> None:
        primary_key = kwargs.pop("primary_key", False)
        nullable = kwargs.pop("nullable", Undefined)
        foreign_key = kwargs.pop("foreign_key", Undefined)
        unique = kwargs.pop("unique", False)
        index = kwargs.pop("index", Undefined)
        sa_type = kwargs.pop("sa_type", Undefined)
        sa_column = kwargs.pop("sa_column", Undefined)
        sa_column_args = kwargs.pop("sa_column_args", Undefined)
        sa_column_kwargs = kwargs.pop("sa_column_kwargs", Undefined)
        create = kwargs.pop("create", True)
        read = kwargs.pop("read", True)
        update = kwargs.pop("update", True)
        query = kwargs.pop("query", True)
        if sa_column is not Undefined:
            if sa_column_args is not Undefined:
                raise RuntimeError(
                    "Passing sa_column_args is not supported when "
                    "also passing a sa_column"
                )
            if sa_column_kwargs is not Undefined:
                raise RuntimeError(
                    "Passing sa_column_kwargs is not supported when "
                    "also passing a sa_column"
                )
            if primary_key is not Undefined:
                raise RuntimeError(
                    "Passing primary_key is not supported when "
                    "also passing a sa_column"
                )
            if nullable is not Undefined:
                raise RuntimeError(
                    "Passing nullable is not supported when " "also passing a sa_column"
                )
            if foreign_key is not Undefined:
                raise RuntimeError(
                    "Passing foreign_key is not supported when "
                    "also passing a sa_column"
                )
            if unique is not Undefined:
                raise RuntimeError(
                    "Passing unique is not supported when also passing a sa_column"
                )
            if index is not Undefined:
                raise RuntimeError(
                    "Passing index is not supported when also passing a sa_column"
                )
            if sa_type is not Undefined:
                raise RuntimeError(
                    "Passing sa_type is not supported when also passing a sa_column"
                )
        super().__init__(default=default, **kwargs)
        self.primary_key = primary_key
        self.nullable = nullable
        self.foreign_key = foreign_key
        self.unique = unique
        self.index = index
        self.sa_type = sa_type
        self.sa_column = sa_column
        self.sa_column_args = sa_column_args
        self.sa_column_kwargs = sa_column_kwargs
        self.create = create
        self.read = read
        self.update = update
        self.query = query

        self.gt = kwargs.get("gt", Undefined)
        self.ge = kwargs.get("ge", Undefined)
        self.lt = kwargs.get("lt", Undefined)
        self.le = kwargs.get("le", Undefined)
        self.min_length = kwargs.get("min_length", Undefined)
        self.max_length = kwargs.get("max_length", Undefined)
        self.max_digits = kwargs.get("max_digits", Undefined)
        self.decimal_places = kwargs.get("decimal_places", Undefined)


def Field(
        default: Any = Undefined,
        *,
        default_factory: Optional[NoArgAnyCallable] = None,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        exclude: Union[
            AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
        ] = None,
        include: Union[
            AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
        ] = None,
        const: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        max_digits: Optional[int] = None,
        decimal_places: Optional[int] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        allow_mutation: bool = True,
        regex: Optional[str] = None,
        discriminator: Optional[str] = None,
        repr: bool = True,
        primary_key: Union[bool, UndefinedType] = Undefined,
        foreign_key: Any = Undefined,
        unique: Union[bool, UndefinedType] = Undefined,
        nullable: Union[bool, UndefinedType] = Undefined,
        index: Union[bool, UndefinedType] = Undefined,
        sa_type: Union[Type[Any], UndefinedType] = Undefined,
        sa_column: Union[Column, UndefinedType] = Undefined,  # type: ignore
        sa_column_args: Union[Sequence[Any], UndefinedType] = Undefined,
        sa_column_kwargs: Union[Mapping[str, Any], UndefinedType] = Undefined,
        create: bool = True,
        read: bool = True,
        update: bool = True,
        query: bool = True,
        **kwargs
) -> Any:
    current_schema_extra = kwargs or {}
    if isinstance(default, Callable):
        default_factory = default
        default = Undefined
    if default is Undefined:
        if isinstance(sa_column, types.FunctionType):  # lambda
            sa_column_ = sa_column()
        else:
            sa_column_ = sa_column

        # server_default -> default
        if isinstance(sa_column_, Column) and isinstance(
                sa_column_.server_default, DefaultClause
        ):
            default_value = sa_column_.server_default.arg
            if issubclass(type(sa_column_.type), Integer) and isinstance(
                    default_value, str
            ):
                default = int(default_value)
            elif issubclass(type(sa_column_.type), Boolean):
                if default_value is false():
                    default = False
                elif default_value is true():
                    default = True
                elif isinstance(default_value, str):
                    if default_value == "1":
                        default = True
                    elif default_value == "0":
                        default = False

    field_info = FieldInfo(
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        discriminator=discriminator,
        repr=repr,
        primary_key=primary_key,
        foreign_key=foreign_key,
        unique=unique,
        nullable=nullable,
        index=index,
        sa_type=sa_type,
        sa_column=sa_column,
        sa_column_args=sa_column_args,
        sa_column_kwargs=sa_column_kwargs,
        create=create,
        read=read,
        update=update,
        query=query,
        **current_schema_extra,
    )
    return field_info


def get_sqlalchemy_type(field: ModelField) -> Any:
    sa_type = getattr(field.field_info, "sa_type", Undefined)  # noqa: B009
    if sa_type is not Undefined:
        return sa_type
    type_ = get_type_from_field(field)

    # Check enums first as an enum can also be a str, needed by Pydantic/FastAPI
    if issubclass(type_, Enum):
        return sa_Enum(type_)
    if issubclass(type_, str):
        max_length = getattr(field.field_info, 'max_length', None)
        if max_length:
            return AutoString(length=max_length)
        return AutoString
    if issubclass(type_, float):
        return Float
    if issubclass(type_, bool):
        return Boolean
    if issubclass(type_, int):
        return Integer
    if issubclass(type_, datetime):
        return DateTime
    if issubclass(type_, date):
        return Date
    if issubclass(type_, timedelta):
        return Interval
    if issubclass(type_, time):
        return Time
    if issubclass(type_, bytes):
        return LargeBinary
    if issubclass(type_, Decimal):
        return Numeric(
            precision=getattr(field.field_info, 'max_digits', Undefined),
            scale=getattr(field.field_info, 'decimal_places', Undefined),
        )
    if issubclass(type_, ipaddress.IPv4Address):
        return AutoString
    if issubclass(type_, ipaddress.IPv4Network):
        return AutoString
    if issubclass(type_, ipaddress.IPv6Address):
        return AutoString
    if issubclass(type_, ipaddress.IPv6Network):
        return AutoString
    if issubclass(type_, Path):
        return AutoString
    if issubclass(type_, EmailStr):
        return AutoString
    if issubclass(type_, uuid.UUID):
        return Uuid
    if issubclass(type_, (list, tuple, set)):
        return AutoJson(none_as_null=True)
    if issubclass(type_, (dict, BaseModel)):
        return AutoJson(none_as_null=True)
    raise ValueError(f"{type_} has no matching SQLAlchemy type")


