from typing import Annotated, Literal

from pydantic import (
    AnyUrl, UrlConstraints, RedisDsn, SecretStr,
    model_validator, PostgresDsn, MySQLDsn, Field,
    AliasChoices, BaseModel
)


class SecretAnyUrl(AnyUrl):
    def __repr__(self):
        auth = f'{self.username if self.username else ""}:{"**********" if self.password else ""}@' if self.username or self.password else ''
        host_port = f"{f'{self.host}:{self.port}' if self.port else self.host}" if self.host else ''
        return f'{self.__class__.__name__}({self.scheme}://{auth}{host_port}{self.path})'


SQLiteSecretDsn = Annotated[
    SecretAnyUrl,
    UrlConstraints(
        allowed_schemes=[
            'sqlite',
            'sqlite+aiosqlite',
        ],
    ),
]

AnyUrl.__repr__ = SecretAnyUrl.__repr__


class RDBSettings(BaseModel, extra='ignore'):
    TYPE: Literal['sqlite', "mysql", "postgresql"] = Field(
        'sqlite', validation_alias=AliasChoices('type', 'driver', 'driver_name')
    )
    HOST: str = 'localhost'
    PORT: int | None = None
    USER: str | None = None
    PASSWORD: SecretStr | None = None
    DB: str | None = None

    URL: PostgresDsn | MySQLDsn | SQLiteSecretDsn | None = Field(None)

    @model_validator(mode='after')
    def init_url(self):
        if self.URL is None:
            self.URL = self.__get_dns()
        else:
            self.HOST = self.URL.host
            self.PORT = self.URL.port
            self.USER = self.URL.username
            self.PASSWORD = SecretStr(self.URL.password) if self.URL.password else None
            self.DB = self.URL.path.lstrip('/') if self.URL.path else None
        return self

    def __get_dns(self) -> PostgresDsn | MySQLDsn | SQLiteSecretDsn:

        if self.TYPE == 'sqlite':
            return SQLiteSecretDsn(f'sqlite+aiosqlite:///{self.DB}')
        if self.TYPE == 'mysql':
            return MySQLDsn.build(
                scheme="mysql+aiomysql",
                username=self.USER,
                password=self.PASSWORD.get_secret_value() if self.PASSWORD else None,
                host=self.HOST,
                port=self.PORT,
                path=self.DB,
            )
        elif self.TYPE == 'postgresql':
            return PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.USER,
                password=self.PASSWORD.get_secret_value() if self.PASSWORD else None,
                host=self.HOST,
                port=self.PORT,
                path=self.DB,
            )
        else:
            return SQLiteSecretDsn(f'sqlite+aiosqlite:///{self.DB or 'sqlite.db'}')

    def __str__(self):
        return str(self.URL)


class RedisSettings(BaseModel, extra='ignore'):
    HOST: str = 'localhost'
    PORT: int | None = None
    USER: str | None = None
    PASSWORD: SecretStr | None = None
    DB: int | None = None

    URL: RedisDsn | None = None

    @model_validator(mode='after')
    def init_url(self):
        if self.URL is None:
            self.URL = self.__get_dns()
        else:
            self.HOST = self.URL.host
            self.PORT = self.URL.port
            self.USER = self.URL.username
            self.PASSWORD = SecretStr(self.URL.password) if self.URL.password else None
            self.DB = int(self.URL.path.lstrip('/')) if self.URL.path else None
        return self

    def __get_dns(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            username=self.USER,
            password=self.PASSWORD.get_secret_value() if self.PASSWORD else None,
            host=self.HOST,
            port=self.PORT,
            path=str(self.DB) if self.DB else None,
        )

    def __str__(self):
        return str(self.URL)
