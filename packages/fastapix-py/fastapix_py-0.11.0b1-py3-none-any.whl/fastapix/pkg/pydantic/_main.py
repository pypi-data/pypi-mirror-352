import types
from enum import Enum
from typing import Any, Dict, Optional, Sequence, Set, Type, Union

from fastapi._compat import (  # noqa: F401
    ModelField,
    FieldInfo,
    sequence_annotation_to_type,
    lenient_issubclass,
)
from fastapi.utils import create_cloned_field
from pydantic import BaseModel, ConfigDict, create_model, BaseConfig, ValidationError
from pydantic.version import VERSION as PYDANTIC_VERSION
from sqlmodel._compat import is_table_model_class
from typing_extensions import Annotated, get_args, get_origin, TypeVar, Literal

UnionType = getattr(types, "UnionType", Union)
NoneType = type(None)
_TSQLModel = TypeVar("_TSQLModel", bound="SQLModel")

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic._internal._fields import PydanticMetadata  # noqa: F401
    from pydantic.v1.datetime_parse import parse_date, parse_datetime  # noqa: F401
    from pydantic_settings import BaseSettings  # noqa: F401

    GenericModel = BaseModel
    from pydantic import model_validator  # noqa: F401
    from pydantic.v1.typing import is_literal_type, is_none_type, is_union  # noqa: F401

    from pydantic_core import PydanticUndefined, PydanticUndefinedType, InitErrorDetails  # noqa: F401

    from pydantic_core import to_jsonable_python as pydantic_encoder  # noqa: F401

    Undefined = PydanticUndefined
    UndefinedType = PydanticUndefinedType


    class AllowExtraModelMixin(BaseModel):
        model_config = ConfigDict(extra="allow")


    class ORMModelMixin(BaseModel):
        model_config = ConfigDict(from_attributes=True)


    def create_model_by_fields(
            name: str,
            fields: Sequence[ModelField],
            *,
            __config__: ConfigDict = None,
            set_none: bool = False,
            extra: str = "ignore",
            mode: Literal["read", "create", "update"] = "create",
            **kwargs,
    ) -> Type[BaseModel]:
        if kwargs.pop("orm_mode", False):
            kwargs.setdefault("from_attributes", True)
        __config__ = marge_model_config(__config__, {"extra": extra, **kwargs})
        __validators__ = None

        for f in fields:
            if mode == 'read':
                f.field_info.validation_alias = None
            else:
                f.field_info.serialization_alias = None
        if set_none:
            for f in fields:
                f.field_info.annotation = Optional[f.field_info.annotation]
                f.field_info.default = None
        field_params = {f.name: (f.field_info.annotation, f.field_info) for f in fields}
        model: Type[BaseModel] = create_model(name, __config__=__config__, __validators__=__validators__,
                                              **field_params)
        return model


    def model_update_forward_refs(model: Type[BaseModel]):
        model.model_rebuild()  # noqa: F401


    def field_json_schema_extra(field: ModelField) -> Dict[str, Any]:
        return field.field_info.json_schema_extra or {}  # noqa: F401


    def field_outer_type(field: ModelField) -> Any:
        return field.field_info.annotation  # noqa: F401


    def field_allow_none(field: ModelField) -> bool:
        if is_union(field.field_info.annotation):  # noqa: F401
            for t in get_args(field.field_info.annotation):  # noqa: F401
                if is_none_type(t):
                    return True
        return False


    def model_fields(model: Type[BaseModel]) -> Dict[str, ModelField]:
        fields = {}
        for field_name, field in model.model_fields.items():
            fields[field_name] = ModelField(field_info=field, name=field_name)
        return fields


    def model_config(model: Type[BaseModel]) -> Union[type, Dict[str, Any]]:
        return model.model_config  # noqa: F401


    def marge_model_config(config: Union[ConfigDict, BaseConfig], update: Dict[str, Any]) -> Union[
        type, Dict[str, Any]]:
        if config is None:
            config = AllowExtraModelMixin.model_config
        if isinstance(config, BaseConfig):
            return {**config.__dict__, **update}
        return {**config, **update}  # noqa: F401


    def model_config_attr(model: Type[BaseModel], name: str, default: Any = None) -> Any:
        return model.model_config.get(name, default)  # noqa: F401


    def model_dump(model: BaseModel, *args, **kwargs) -> Dict[str, Any]:
        return model.model_dump(*args, **kwargs)  # noqa: F401


    def model_validate(schema: Type[BaseModel], obj: Any, *args, **kwargs) -> BaseModel:
        return schema.model_validate(obj, *args, **kwargs)  # noqa: F401


    def model_dump_json(schema: Type[BaseModel], *args, **kwargs) -> str:
        return schema.model_dump_json(*args, **kwargs)  # noqa: F401


    def get_type_from_field(field: ModelField) -> Any:
        type_: Any = field.field_info.annotation
        # Resolve Optional fields
        if type_ is None:
            raise ValueError("Missing field type")

        def _get_origin(type_):
            origin = get_origin(type_)
            if origin is None:
                return type_
            if origin is UnionType or origin is Union or origin is Annotated:
                bases = get_args(type_)
                type_ = bases[0] if bases[0] is not NoneType else bases[1]
                return _get_origin(type_)
            return origin

        origin = _get_origin(type_)
        return origin


    def is_field_noneable(field: ModelField) -> bool:
        field_info = field.field_info
        if getattr(field_info, "nullable", Undefined) is not Undefined:
            return field_info.nullable  # type: ignore
        origin = get_origin(field_info.annotation)
        if origin is not None and (origin is UnionType or origin is Union):
            args = get_args(field_info.annotation)
            if any(arg is NoneType for arg in args):
                return True
        if not field_info.is_required():
            if field_info.default is Undefined:
                return False
            if field_info.annotation is None or field_info.annotation is NoneType:  # type: ignore[comparison-overlap]
                return True
            return False
        return False


    def sqlmodel_table_construct(
            *,
            self_instance: _TSQLModel,
            values: Dict[str, Any],
            _fields_set: Union[Set[str], None] = None,
    ) -> _TSQLModel:
        # Copy from SQLModel's _compat.sqlmodel_table_construct Ref:
        # https://github.com/tiangolo/sqlmodel/blob/0c7def88b5d9652bf9288738e2e9276d9dd24b5f/sqlmodel/_compat.py#L210
        cls = type(self_instance)
        old_dict = self_instance.__dict__.copy()

        fields_values: Dict[str, Any] = {}
        defaults: Dict[
            str, Any
        ] = {}  # keeping this separate from `fields_values` helps us compute `_fields_set`
        # SQLModel override BaseModel, value BaseModel.validate
        errs = []
        for name, field in model_fields(cls).items():
            field_alias = field.field_info.alias or field.field_info.validation_alias
            if field_alias and field_alias in values:
                _v = values.get(field_alias)
                fields_values[name], err = field.validate(_v)
                if err:
                    if getattr(field.field_info, "primary_key", None) and err[0].get('input') is None:
                        # 主键默认None, 将自动生成主键值
                        continue
                    for e in err:
                        if e['loc']:
                            e['loc'] = [f"{name}.{loc}" for loc in e['loc']]
                        else:
                            e['loc'] = e['loc'] or (name,)
                    errs.extend(err)
            elif name in values:
                _v = values.get(name)
                fields_values[name], err = field.validate(_v)
                if err:
                    if getattr(field.field_info, "primary_key", None) is True and err[0].get('input') is None:
                        # 主键默认None, 将自动生成主键值
                        continue
                    for e in err:
                        if e['loc']:
                            e['loc'] = [f"{name}.{loc}" for loc in e['loc']]
                        else:
                            e['loc'] = (name,)
                    errs.extend(err)
            elif not field.required:
                _v = field.get_default()
                defaults[name], err = field.validate(_v)
                if err:
                    if getattr(field.field_info, "primary_key", None) is True and err[0].get('input') is None:
                        # 主键默认None, 将自动生成主键值
                        continue
                    for e in err:
                        if e['loc']:
                            e['loc'] = [f"{name}.{loc}" for loc in e['loc']]
                        else:
                            e['loc'] = (name,)
                    errs.extend(err)
            elif field.required:
                if getattr(field.field_info, "primary_key", None) is True:
                    # 主键默认None, 将自动生成主键值
                    continue
                errs.extend([InitErrorDetails(type='missing', loc=(name,), input=values)])
        if errs:
            raise ValidationError.from_exception_data(
                title=self_instance.__class__.__name__,
                line_errors=[InitErrorDetails(**err) for err in errs],
            )
        # End SQLModel override
        if _fields_set is None:
            _fields_set = set(fields_values.keys())
        fields_values.update(defaults)
        _extra: Union[Dict[str, Any], None] = None
        if cls.model_config.get("extra") == "allow":
            _extra = {}
            for k, v in values.items():
                _extra[k] = v
        for key, value in {**old_dict, **fields_values}.items():
            setattr(self_instance, key, value)
        object.__setattr__(self_instance, "__pydantic_fields_set__", _fields_set)
        if not cls.__pydantic_root_model__:
            object.__setattr__(self_instance, "__pydantic_extra__", _extra)

        if cls.__pydantic_post_init__:
            self_instance.model_post_init(None)
        elif not cls.__pydantic_root_model__:
            object.__setattr__(self_instance, "__pydantic_private__", None)
        for key in self_instance.__sqlmodel_relationships__:
            value = values.get(key, Undefined)
            if value is not Undefined:
                setattr(self_instance, key, value)
        return self_instance


    def sqlmodel_init(*, self: "SQLModel", data: Dict[str, Any]) -> None:
        # Copy sqlmodel._compat
        old_dict = self.__dict__.copy()
        if not is_table_model_class(self.__class__):
            self.__pydantic_validator__.validate_python(
                data,
                self_instance=self,
            )
        else:
            sqlmodel_table_construct(
                self_instance=self,
                values=data,
            )
        object.__setattr__(
            self,
            "__dict__",
            {**old_dict, **self.__dict__},
        )

else:
    from pydantic.datetime_parse import parse_date, parse_datetime  # noqa: F401
    from pydantic.fields import ModelField  # noqa: F401
    from pydantic.generics import GenericModel  # noqa: F401
    from pydantic.typing import is_literal_type, is_none_type, is_union  # noqa: F401
    from pydantic.fields import UndefinedType as UndefinedType, Undefined as Undefined  # noqa: F401
    from pydantic.fields import (
        SHAPE_SINGLETON,  # noqa: F401
        SHAPE_LIST, SHAPE_SET, SHAPE_TUPLE, SHAPE_SEQUENCE,  # noqa: F401
        SHAPE_DICT, SHAPE_DEFAULTDICT  # noqa: F401
    )
    from pydantic.json import pydantic_encoder  # noqa: F401
    from pydantic.main import validate_model
    from pydantic import BaseSettings  # noqa: F401

    PydanticUndefined = Undefined
    PydanticUndefinedType = UndefinedType


    class AllowExtraModelMixin(BaseModel):
        class Config:
            extra = "allow"


    class ORMModelMixin(BaseModel):
        class Config:
            orm_mode = True


    def create_model_by_fields(
            name: str,
            fields: Sequence[ModelField],
            *,
            __config__=None,
            set_none: bool = False,
            extra: str = "ignore",
            orm_mode=True,
            **kwargs,
    ) -> Type[BaseModel]:
        __config__ = marge_model_config(__config__, {"extra": extra, 'orm_mode': orm_mode, **kwargs})
        __validators__ = None
        if set_none:
            for f in fields:
                f.required = False
                f.allow_none = True
        model = create_model(name, __config__=__config__, __validators__=__validators__)  # type: ignore
        model.__fields__ = {f.name: f for f in fields}
        return model


    def model_update_forward_refs(model: Type[BaseModel]):
        model.update_forward_refs()


    def field_json_schema_extra(field: ModelField) -> Dict[str, Any]:
        return field.field_info.extra or {}


    def field_outer_type(field: ModelField) -> Any:
        return field.outer_type_


    def field_allow_none(field: ModelField) -> bool:
        return field.allow_none


    def model_fields(model: Type[BaseModel]) -> Dict[str, ModelField]:
        return model.__fields__


    def model_config(model: Type[BaseModel]) -> Union[type, Dict[str, Any]]:
        return model.Config


    def marge_model_config(config: Type[BaseConfig], update: Dict[str, Any]) -> Union[type, Dict[str, Any]]:
        if config is None:
            config = AllowExtraModelMixin
        return type("Config", (config,), update)


    def model_config_attr(model: Type[BaseModel], name: str, default: Any = None) -> Any:
        return getattr(model.Config, name, default)


    def model_dump(model: BaseModel, *args, **kwargs) -> Dict[str, Any]:
        return model.dict(*args, **kwargs)


    def model_validate(model: BaseModel, obj: Any, *args, **kwargs) -> BaseModel:
        return model.from_orm(obj)


    def model_dump_json(model: BaseModel, *args, **kwargs) -> str:
        return model.json(*args, **kwargs)


    def get_type_from_field(field: ModelField) -> Any:
        if isinstance(field.type_, type) and field.shape == SHAPE_SINGLETON:
            return field.type_
        elif isinstance(field.type_, type) and field.shape in (SHAPE_LIST, SHAPE_SET, SHAPE_TUPLE, SHAPE_SEQUENCE):
            return list
        elif isinstance(field.type_, type) and field.shape in (SHAPE_DICT, SHAPE_DEFAULTDICT):
            return dict


    def is_field_noneable(field: ModelField) -> bool:
        if not field.required:  # type: ignore[attr-defined]
            # Taken from [Pydantic](https://github.com/samuelcolvin/pydantic/blob/v1.8.2/pydantic/fields.py#L946-L947)
            return field.allow_none and (  # type: ignore[attr-defined]
                    field.shape != SHAPE_SINGLETON or not field.sub_fields  # type: ignore[attr-defined]
            )
        return field.allow_none  # type: ignore[no-any-return, attr-defined]


    def sqlmodel_init(*, self: "SQLModel", data: Dict[str, Any]) -> None:
        # Copy sqlmodel._compat
        values, fields_set, validation_error = validate_model(self.__class__, data)
        # Only raise errors if not a SQLModel model
        if (
                not is_table_model_class(self.__class__)  # noqa
                and validation_error
        ):
            raise validation_error
        if not is_table_model_class(self.__class__):
            object.__setattr__(self, "__dict__", values)
        else:
            # Do not set values as in Pydantic, pass them through setattr, so
            # SQLAlchemy can handle them
            for key, value in values.items():
                setattr(self, key, value)
        object.__setattr__(self, "__fields_set__", fields_set)
        non_pydantic_keys = data.keys() - values.keys()

        if is_table_model_class(self.__class__):
            for key in non_pydantic_keys:
                if key in self.__sqlmodel_relationships__:
                    setattr(self, key, data[key])


def annotation_outer_type(tp: Any) -> Any:
    """Get the base type of the annotation."""
    if tp is Ellipsis:
        return Any
    origin = get_origin(tp)
    if origin is None:
        return tp
    elif is_union(origin) or origin is Annotated:
        pass
    elif origin in sequence_annotation_to_type:
        return sequence_annotation_to_type[origin]
    elif origin in {Dict, dict}:
        return dict
    elif lenient_issubclass(origin, BaseModel):
        return origin
    args = get_args(tp)
    for arg in args:
        if is_literal_type(tp):
            arg = type(arg)
        if is_none_type(arg):
            continue
        return annotation_outer_type(arg)
    return tp


def scalar_sequence_inner_type(tp: Any) -> Any:
    origin = get_origin(tp)
    if origin is None:
        return Any
    elif is_union(origin) or origin is Annotated:  # Return the type of the first element
        return scalar_sequence_inner_type(get_args(tp)[0])
    args = get_args(tp)
    return annotation_outer_type(args[0]) if args else Any


def validator_skip_blank(v, type_: type):
    if isinstance(v, str):
        if not v:
            if issubclass(type_, Enum):
                if "" not in type_._value2member_map_:
                    return None
                return ""
            if not issubclass(type_, str):
                return None
            return ""
        if issubclass(type_, int):
            v = int(v)
    elif isinstance(v, int) and issubclass(type_, str):
        v = str(v)
    return v


def root_validator_skip_blank(cls, values: Dict[str, Any]):
    fields = model_fields(cls)

    def get_field_by_alias(alias: str) -> Optional[ModelField]:
        for f in fields.values():
            if f.alias == alias:
                return f
        return None

    for k, v in values.items():
        field = get_field_by_alias(k)
        if field:
            values[k] = validator_skip_blank(v, annotation_outer_type(field.type_))
    return values


def create_model_by_model(
        model: Type[BaseModel],
        name: str,
        *,
        include: Set[str] = None,
        exclude: Set[str] = None,
        set_none: bool = False,
        __config__=None,
        **kwargs,
) -> Type[BaseModel]:
    """Create a new model by the BaseModel."""
    fields = model_fields(model)
    keys = set(fields.keys())
    if include:
        keys &= include
    if exclude:
        keys -= exclude
    fields = {name: create_cloned_field(field) for name, field in fields.items() if name in keys}
    return create_model_by_fields(name, list(fields.values()), set_none=set_none, __config__=__config__, **kwargs)
