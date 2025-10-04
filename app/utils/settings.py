from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    mongodb_uri: str = Field(alias="MONGODB_URI", default="mongodb://localhost:27017")
    mongodb_db: str = Field(alias="MONGODB_DB", default="da2_listings")
    jwt_secret: str = Field(alias="JWT_SECRET", default="change_me")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM", default="HS256")
    jwt_expires_minutes: int = Field(alias="JWT_EXPIRES_MINUTES", default=60)
    enable_semantic_search: bool = Field(alias="ENABLE_SEMANTIC_SEARCH", default=False)
    embedding_model: str = Field(alias="EMBEDDING_MODEL", default="sentence-transformers/all-MiniLM-L6-v2")
    cors_origins: List[str] = Field(alias="CORS_ORIGINS", default_factory=lambda: [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

    # Image storage
    storage_provider: str = Field(alias="STORAGE_PROVIDER", default="local")  # local | s3
    local_images_dir: str = Field(alias="LOCAL_IMAGES_DIR", default="app/listings_images")
    # S3 placeholders
    s3_bucket: str = Field(alias="S3_BUCKET", default="")
    s3_region: str = Field(alias="S3_REGION", default="")
    s3_base_url: str = Field(alias="S3_BASE_URL", default="")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8",
    }


settings = Settings()
