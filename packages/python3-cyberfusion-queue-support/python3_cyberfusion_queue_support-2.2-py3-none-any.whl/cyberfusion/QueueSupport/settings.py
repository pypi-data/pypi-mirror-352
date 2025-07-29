from pydantic import BaseSettings


class Settings(BaseSettings):
    database_path: str = "sqlite:///./queue-support.db"
    alembic_config_file_path: str = "alembic.ini"

    class Config:
        env_prefix = "queue_support_"

        env_file = ".env", "/etc/queue-support.conf"


settings = Settings()
