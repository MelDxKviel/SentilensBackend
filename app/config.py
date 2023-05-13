from pydantic import BaseSettings


class Settings(BaseSettings):
    auth_key: str
    pg_address: str

    class Config:
        env_file = ".env"


global_settings = Settings()
