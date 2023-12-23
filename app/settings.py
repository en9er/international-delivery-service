import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../.env',
        ),
        env_file_encoding='utf-8',
        extra='allow'
    )


class DBConfig(AppSettings):
    host: str = Field('HOST')
    port: str = Field('PORT')
    user: str = Field('USER')
    password: str = Field('PASS')
    name: str = Field('NAME')
    echo: bool = Field('ECHO')
    model_config = SettingsConfigDict(env_prefix='DB_')

    def generate_db_url(
        self,
    ) -> str:
        return (
            f'mysql+asyncmy://'
            f'{self.user}:'
            f'@{self.host}/{self.name}'
        )


class CelerySettings(AppSettings):
    CELERY_BROKER_URL: str = Field('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: str = Field('CELERY_RESULT_BACKEND')


class Settings(AppSettings):
    ROOT_PATH: str = '/api'
    # DB
    DB: DBConfig = DBConfig()
    DB_URL: str = DB.generate_db_url()

    CBR_API_URL: str = Field('CBR_API_URL')
    EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES: int = (
        Field('EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES')
    )

    # Redis
    REDIS_HOST: str = Field('REDIS_HOST')

    CELERY: CelerySettings = CelerySettings()
    DEBUG_MODE: bool = Field('DEBUG_MODE')


settings = Settings()
