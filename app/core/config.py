from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    APP_NAME: str = 'Stepic FastAPI Project'
    APP_DESCRIPTION: str = 'Stepic FastAPI Project'
    APP_VERSION: str = '0.0.1'


    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

config = Config()