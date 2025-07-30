import os
from pathlib import Path
from typing import Mapping

from pydantic.types import PathType
from pydantic_settings import BaseSettings, DotEnvSettingsSource as DotEnvSettingsSource
from pydantic_settings.sources.utils import parse_env_vars


class SecretsSettingsSource(DotEnvSettingsSource):
    def __init__(
            self,
            settings_cls: type[BaseSettings],
            secrets_dir: PathType | None = None,
            case_sensitive: bool | None = None,
            env_prefix: str | None = None,
            env_ignore_empty: bool | None = None,
            env_parse_none_str: str | None = None,
            env_parse_enums: bool | None = None,
            env_nested_delimiter: str | None = None,
            env_nested_max_split: int | None = None,
    ) -> None:
        super().__init__(
            settings_cls=settings_cls,
            env_file=secrets_dir,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
            env_nested_max_split=env_nested_max_split,
            env_ignore_empty=env_ignore_empty,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums
        )


    def _read_env_files(self) -> Mapping[str, str | None]:
        secrets_dirs = self.env_file
        if secrets_dirs is None:
            return {}

        if isinstance(secrets_dirs, (str, os.PathLike)):
            secrets_dirs = [secrets_dirs]

        dotenv_vars: dict[str, str | None] = {}
        for secrets_dir in secrets_dirs:
            secrets_dir_path = Path(secrets_dir).expanduser()
            if secrets_dir_path.is_dir():
                dotenv_vars.update(self._read_env_file(secrets_dir_path))
        return dotenv_vars

    @staticmethod
    def _static_read_env_file(
            secrets_dir_path: Path,
            *,
            encoding: str | None = None,
            case_sensitive: bool = False,
            ignore_empty: bool = False,
            parse_none_str: str | None = None,
    ) -> Mapping[str, str | None]:
        file_vars: dict[str, str | None] = {}
        for secrets_path in secrets_dir_path.iterdir():
            file_vars.update({secrets_path.name: secrets_path.read_text(encoding=encoding).strip()})
        return parse_env_vars(file_vars, case_sensitive, ignore_empty, parse_none_str)
