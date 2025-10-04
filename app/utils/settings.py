from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    mongodb_uri: str = Field(alias="MONGODB_URI", default="mongodb://localhost:27017")
    mongodb_db: str = Field(alias="MONGODB_DB", default="da2_listings")
    jwt_secret: str = Field(alias="JWT_SECRET", default="change_me")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM", default="HS256")
    jwt_expires_minutes: int = Field(alias="JWT_EXPIRES_MINUTES", default=60)

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8",
    }


settings = Settings()
