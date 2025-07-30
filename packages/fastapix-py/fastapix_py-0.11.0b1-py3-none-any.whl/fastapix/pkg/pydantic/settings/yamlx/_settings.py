from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic._internal._utils import deep_update
from pydantic.fields import FieldInfo
from pydantic.types import PathType
from pydantic_settings import (
    BaseSettings, PydanticBaseSettingsSource, CliSettingsSource,
    DotEnvSettingsSource, EnvSettingsSource, InitSettingsSource
)
from pydantic_settings.sources import ENV_FILE_SENTINEL, DotenvType, DefaultSettingsSource, ConfigFileSourceMixin
from pydantic_settings.sources.providers.yaml import import_yaml
from pydantic_settings.sources.types import DEFAULT_PATH
from pydantic_settings.sources.utils import _get_alias_names

from fastapix.pkg.pydantic.settings._secrets import SecretsSettingsSource
from fastapix.pkg.pydantic.settings.yamlx._include import load


class YamlSettings(BaseSettings):

    def __init__(
            __pydantic_self__,
            _case_sensitive: bool | None = None,
            _nested_model_default_partial_update: bool | None = None,
            _env_prefix: str | None = None,
            _env_file: DotenvType | None = ENV_FILE_SENTINEL,
            _env_file_encoding: str | None = None,
            _env_ignore_empty: bool | None = None,
            _env_nested_delimiter: str | None = None,
            _env_nested_max_split: int | None = None,
            _env_parse_none_str: str | None = None,
            _env_parse_enums: bool | None = None,
            _cli_prog_name: str | None = None,
            _cli_parse_args: bool | list[str] | tuple[str, ...] | None = None,
            _cli_settings_source: CliSettingsSource[Any] | None = None,
            _cli_parse_none_str: str | None = None,
            _cli_hide_none_type: bool | None = None,
            _cli_avoid_json: bool | None = None,
            _cli_enforce_required: bool | None = None,
            _cli_use_class_docs_for_groups: bool | None = None,
            _cli_exit_on_error: bool | None = None,
            _cli_prefix: str | None = None,
            _cli_flag_prefix_char: str | None = None,
            _cli_implicit_flags: bool | None = None,
            _cli_ignore_unknown_args: bool | None = None,
            _cli_kebab_case: bool | None = None,
            _secrets_dir: PathType | None = None,
            _yaml_file: str | None = None,
            _yaml_file_encoding: str | None = None,
            **values: Any,
    ) -> None:
        super().__init__(
            **__pydantic_self__._settings_build_values(
                values,
                _case_sensitive=_case_sensitive,
                _nested_model_default_partial_update=_nested_model_default_partial_update,
                _env_prefix=_env_prefix,
                _env_file=_env_file,
                _env_file_encoding=_env_file_encoding,
                _env_ignore_empty=_env_ignore_empty,
                _env_nested_delimiter=_env_nested_delimiter,
                _env_nested_max_split=_env_nested_max_split,
                _env_parse_none_str=_env_parse_none_str,
                _env_parse_enums=_env_parse_enums,
                _cli_prog_name=_cli_prog_name,
                _cli_parse_args=_cli_parse_args,
                _cli_settings_source=_cli_settings_source,
                _cli_parse_none_str=_cli_parse_none_str,
                _cli_hide_none_type=_cli_hide_none_type,
                _cli_avoid_json=_cli_avoid_json,
                _cli_enforce_required=_cli_enforce_required,
                _cli_use_class_docs_for_groups=_cli_use_class_docs_for_groups,
                _cli_exit_on_error=_cli_exit_on_error,
                _cli_prefix=_cli_prefix,
                _cli_flag_prefix_char=_cli_flag_prefix_char,
                _cli_implicit_flags=_cli_implicit_flags,
                _cli_ignore_unknown_args=_cli_ignore_unknown_args,
                _cli_kebab_case=_cli_kebab_case,
                _secrets_dir=_secrets_dir,
                _yaml_file=_yaml_file,
                _yaml_file_encoding=_yaml_file_encoding,
            )
        )

    @classmethod
    def __settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            yaml_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, env_settings, dotenv_settings, file_secret_settings, yaml_settings

    def _settings_build_values(
            self,
            init_kwargs: dict[str, Any],
            _case_sensitive: bool | None = None,
            _nested_model_default_partial_update: bool | None = None,
            _env_prefix: str | None = None,
            _env_file: DotenvType | None = None,
            _env_file_encoding: str | None = None,
            _env_ignore_empty: bool | None = None,
            _env_nested_delimiter: str | None = None,
            _env_nested_max_split: int | None = None,
            _env_parse_none_str: str | None = None,
            _env_parse_enums: bool | None = None,
            _cli_prog_name: str | None = None,
            _cli_parse_args: bool | list[str] | tuple[str, ...] | None = None,
            _cli_settings_source: CliSettingsSource[Any] | None = None,
            _cli_parse_none_str: str | None = None,
            _cli_hide_none_type: bool | None = None,
            _cli_avoid_json: bool | None = None,
            _cli_enforce_required: bool | None = None,
            _cli_use_class_docs_for_groups: bool | None = None,
            _cli_exit_on_error: bool | None = None,
            _cli_prefix: str | None = None,
            _cli_flag_prefix_char: str | None = None,
            _cli_implicit_flags: bool | None = None,
            _cli_ignore_unknown_args: bool | None = None,
            _cli_kebab_case: bool | None = None,
            _secrets_dir: PathType | None = None,
            _yaml_file: str | None = None,
            _yaml_file_encoding: str | None = None,
    ) -> dict[str, Any]:
        # Determine settings config values
        case_sensitive = _case_sensitive if _case_sensitive is not None else self.model_config.get('case_sensitive')
        env_prefix = _env_prefix if _env_prefix is not None else self.model_config.get('env_prefix')
        nested_model_default_partial_update = (
            _nested_model_default_partial_update
            if _nested_model_default_partial_update is not None
            else self.model_config.get('nested_model_default_partial_update')
        )
        env_file = _env_file if _env_file != ENV_FILE_SENTINEL else self.model_config.get('env_file')
        env_file_encoding = (
            _env_file_encoding if _env_file_encoding is not None else self.model_config.get('env_file_encoding')
        )
        env_ignore_empty = (
            _env_ignore_empty if _env_ignore_empty is not None else self.model_config.get('env_ignore_empty')
        )
        env_nested_delimiter = (
            _env_nested_delimiter
            if _env_nested_delimiter is not None
            else self.model_config.get('env_nested_delimiter')
        )
        env_nested_max_split = (
            _env_nested_max_split
            if _env_nested_max_split is not None
            else self.model_config.get('env_nested_max_split')
        )
        env_parse_none_str = (
            _env_parse_none_str if _env_parse_none_str is not None else self.model_config.get('env_parse_none_str')
        )
        env_parse_enums = _env_parse_enums if _env_parse_enums is not None else self.model_config.get('env_parse_enums')

        cli_prog_name = _cli_prog_name if _cli_prog_name is not None else self.model_config.get('cli_prog_name')
        cli_parse_args = _cli_parse_args if _cli_parse_args is not None else self.model_config.get('cli_parse_args')
        cli_settings_source = (
            _cli_settings_source if _cli_settings_source is not None else self.model_config.get('cli_settings_source')
        )
        cli_parse_none_str = (
            _cli_parse_none_str if _cli_parse_none_str is not None else self.model_config.get('cli_parse_none_str')
        )
        cli_parse_none_str = cli_parse_none_str if not env_parse_none_str else env_parse_none_str
        cli_hide_none_type = (
            _cli_hide_none_type if _cli_hide_none_type is not None else self.model_config.get('cli_hide_none_type')
        )
        cli_avoid_json = _cli_avoid_json if _cli_avoid_json is not None else self.model_config.get('cli_avoid_json')
        cli_enforce_required = (
            _cli_enforce_required
            if _cli_enforce_required is not None
            else self.model_config.get('cli_enforce_required')
        )
        cli_use_class_docs_for_groups = (
            _cli_use_class_docs_for_groups
            if _cli_use_class_docs_for_groups is not None
            else self.model_config.get('cli_use_class_docs_for_groups')
        )
        cli_exit_on_error = (
            _cli_exit_on_error if _cli_exit_on_error is not None else self.model_config.get('cli_exit_on_error')
        )
        cli_prefix = _cli_prefix if _cli_prefix is not None else self.model_config.get('cli_prefix')
        cli_flag_prefix_char = (
            _cli_flag_prefix_char
            if _cli_flag_prefix_char is not None
            else self.model_config.get('cli_flag_prefix_char')
        )
        cli_implicit_flags = (
            _cli_implicit_flags if _cli_implicit_flags is not None else self.model_config.get('cli_implicit_flags')
        )
        cli_ignore_unknown_args = (
            _cli_ignore_unknown_args
            if _cli_ignore_unknown_args is not None
            else self.model_config.get('cli_ignore_unknown_args')
        )
        cli_kebab_case = _cli_kebab_case if _cli_kebab_case is not None else self.model_config.get('cli_kebab_case')

        secrets_dir = _secrets_dir if _secrets_dir is not None else self.model_config.get('secrets_dir')

        yaml_file = _yaml_file if _yaml_file is not None else self.model_config.get('yaml_file')
        yaml_file_encoding = (
            _yaml_file_encoding if _yaml_file_encoding is not None else self.model_config.get('yaml_file_encoding')
        )

        # Configure built-in sources
        default_settings = DefaultSettingsSource(
            self.__class__, nested_model_default_partial_update=nested_model_default_partial_update
        )
        init_settings = InitSettingsSource(
            self.__class__,
            init_kwargs=init_kwargs,
            nested_model_default_partial_update=nested_model_default_partial_update,
        )
        env_settings = EnvSettingsSource(
            self.__class__,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
            env_nested_max_split=env_nested_max_split,
            env_ignore_empty=env_ignore_empty,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums,
        )
        dotenv_settings = DotEnvSettingsSource(
            self.__class__,
            env_file=env_file,
            env_file_encoding=env_file_encoding,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
            env_nested_max_split=env_nested_max_split,
            env_ignore_empty=env_ignore_empty,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums,
        )

        yaml_settings = YamlIncludeConfigSettingsSource(
            self.__class__,
            yaml_file=yaml_file,
            yaml_file_encoding=yaml_file_encoding,
        )

        file_secret_settings = SecretsSettingsSource(
            self.__class__,
            secrets_dir=secrets_dir,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
            env_nested_max_split=env_nested_max_split,
            env_ignore_empty=env_ignore_empty,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums,
        )
        # Provide a hook to set built-in sources priority and add / remove sources
        sources = self.__settings_customise_sources(
            self.__class__,
            init_settings=init_settings,
            env_settings=env_settings,
            dotenv_settings=dotenv_settings,
            yaml_settings=yaml_settings,
            file_secret_settings=file_secret_settings,
        ) + (default_settings,)
        if not any([source for source in sources if isinstance(source, CliSettingsSource)]):
            if isinstance(cli_settings_source, CliSettingsSource):
                sources = (cli_settings_source,) + sources
            elif cli_parse_args is not None:
                cli_settings = CliSettingsSource[Any](
                    self.__class__,
                    cli_prog_name=cli_prog_name,
                    cli_parse_args=cli_parse_args,
                    cli_parse_none_str=cli_parse_none_str,
                    cli_hide_none_type=cli_hide_none_type,
                    cli_avoid_json=cli_avoid_json,
                    cli_enforce_required=cli_enforce_required,
                    cli_use_class_docs_for_groups=cli_use_class_docs_for_groups,
                    cli_exit_on_error=cli_exit_on_error,
                    cli_prefix=cli_prefix,
                    cli_flag_prefix_char=cli_flag_prefix_char,
                    cli_implicit_flags=cli_implicit_flags,
                    cli_ignore_unknown_args=cli_ignore_unknown_args,
                    cli_kebab_case=cli_kebab_case,
                    case_sensitive=case_sensitive,
                )
                sources = (cli_settings,) + sources
        if sources:
            state: dict[str, Any] = {}
            states: dict[str, dict[str, Any]] = {}
            for source in sources:
                if isinstance(source, PydanticBaseSettingsSource):
                    source._set_current_state(state)
                    source._set_settings_sources_data(states)

                source_name = source.__name__ if hasattr(source, '__name__') else type(source).__name__
                source_state = source()

                states[source_name] = source_state
                state = deep_update(source_state, state)
            return state
        else:
            # no one should mean to do this, but I think returning an empty dict is marginally preferable
            # to an informative error and much better than a confusing error
            return {}


class YamlInitSettingsSource(PydanticBaseSettingsSource):
    """
    Source class for loading values provided during settings class initialization.
    """

    def __init__(
            self,
            settings_cls: type[BaseSettings],
            init_kwargs: dict[str, Any],
            case_sensitive: bool | None = None,
            nested_model_default_partial_update: bool | None = None,
    ):
        self.init_kwargs = self.update_model_value(settings_cls, init_kwargs, case_sensitive)
        super().__init__(settings_cls)
        self.nested_model_default_partial_update = (
            nested_model_default_partial_update
            if nested_model_default_partial_update is not None
            else self.config.get('nested_model_default_partial_update', False)
        )

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, '', False

    def __call__(self) -> dict[str, Any]:
        return (
            TypeAdapter(dict[str, Any]).dump_python(self.init_kwargs)
            if self.nested_model_default_partial_update
            else self.init_kwargs
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(init_kwargs={self.init_kwargs!r})'

    def update_model_value(self, model_cls, init_kwargs, case_sensitive: bool | None = None):
        result_init_kwargs = {}
        if not case_sensitive:
            init_kwargs = {key.lower(): val for key, val in init_kwargs.items()}
        init_kwarg_names = set(init_kwargs.keys())
        for field_name, field_info in model_cls.model_fields.items():
            alias_names, *_ = _get_alias_names(field_name, field_info)
            if not case_sensitive:
                init_kwarg_name = init_kwarg_names & {key.lower() for key in alias_names}
            else:
                init_kwarg_name = init_kwarg_names & set(alias_names)
            if init_kwarg_name:
                preferred_alias = alias_names[0]
                init_kwarg_names -= init_kwarg_name
                if issubclass(field_info.annotation, BaseModel):
                    result_init_kwargs[preferred_alias] = self.update_model_value(field_info.annotation,
                                                                                  init_kwargs[init_kwarg_name.pop()])
                else:
                    result_init_kwargs[preferred_alias] = init_kwargs[init_kwarg_name.pop()]
        result_init_kwargs.update({key: val for key, val in init_kwargs.items() if key in init_kwarg_names})
        return result_init_kwargs


class YamlIncludeConfigSettingsSource(YamlInitSettingsSource, ConfigFileSourceMixin):
    """
    A source class that loads variables from a yaml file
    """

    def __init__(
            self,
            settings_cls: type[BaseSettings],
            yaml_file: PathType | None = DEFAULT_PATH,
            yaml_file_encoding: str | None = None,
    ):
        self.yaml_file_path = yaml_file if yaml_file != DEFAULT_PATH else settings_cls.model_config.get('yaml_file')
        self.yaml_file_encoding = (
            yaml_file_encoding
            if yaml_file_encoding is not None
            else settings_cls.model_config.get('yaml_file_encoding')
        )
        self.yaml_data = self._read_files(self.yaml_file_path)
        super().__init__(settings_cls, self.yaml_data)

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        import_yaml()
        return load(file_path) or {}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(yaml_file={self.yaml_file_path})'
