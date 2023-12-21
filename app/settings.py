import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '.env',
        ),
        env_file_encoding='utf-8',
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
            f'{self.user}:{self.password}'
            f'@{self.host}/{self.name}'
        )


class Settings(AppSettings):
    ROOT_PATH: str = '/api'
    DB: DBConfig = DBConfig()
    DB_URL: str = DB.generate_db_url()
    CBR_API_URL: str = Field('CBR_API_URL')


settings = Settings()
