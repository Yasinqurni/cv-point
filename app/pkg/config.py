from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # app config
    app_name: str = Field("cv-point", env="APP_NAME")
    env: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG_MODE")
    port: int = Field(8000, env="APP_PORT")
    host: str = Field("0.0.0.0", env="APP_HOST")

    # database config
    db_name: str = Field(..., env="DB_NAME")
    db_host: str = Field(..., env="DB_HOST")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_port: str = Field(..., env="DB_PORT")
    db_user: str = Field(..., env="DB_USER")

     # RabbitMQ
    rabbitmq_host: str = Field("localhost", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field("guest", env="RABBITMQ_USER")
    rabbitmq_password: str = Field("guest", env="RABBITMQ_PASSWORD")

    # Gemini
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field(..., env="GEMINI_MODEL")

    # Cloudinary
    cloudinary_cloud_name: str = Field(..., env="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(..., env="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(..., env="CLOUDINARY_API_SECRET")


@lru_cache
def get_config() -> "Config":
    return Config()

