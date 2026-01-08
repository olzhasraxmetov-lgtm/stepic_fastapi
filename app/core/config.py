from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    ADMIN_SECRET_KEY: str

    APP_NAME: str = 'Stepic FastAPI Project'
    APP_DESCRIPTION: str = 'Stepic FastAPI Project'
    APP_VERSION: str = '0.0.1'

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM : str

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
    )

config = Config()