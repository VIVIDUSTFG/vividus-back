import secrets
from pathlib import Path
from typing import Any, List, Optional, Union

from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):

    APP_DIR: Path = APP_DIR

    STAGING: bool

    PROJECT_NAME: str
    PROJECT_VERSION: str
    API_STR: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_REFRESH_SECRET_KEY: str = secrets.token_urlsafe(32)

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: str

    SERVER_HOST: Optional[str] = None
    SERVER_PORT: Optional[int] = None

    # TMP_DIR: str = "/tmp_inference"
    # INFER_DIR: str = "/infer_models"

    TMP_DIR: str = str(APP_DIR / "tmp_inference")
    INFER_DIR: str = str(APP_DIR / "infer_models")
    DATASETS_DIR: str = str(APP_DIR / "datasets")

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
            cls, v: Union[str, List[str], List[AnyHttpUrl]]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid input for BACKEND_CORS_ORIGINS: {v}")

    PSQL_USER: str | None = "root"
    PSQL_PASSWORD: str | None = "rootpass"
    PSQL_HOST: str | None = "localhost"
    PSQL_PORT: int | None = 5432
    PSQL_DB: str = "test_db"
    PSQL_DATABASE_URL: Optional[PostgresDsn] | str = None

    REDIS_HOST: str | None = "localhost"
    REDIS_PORT: int | None = 6379
    REDIS_PASSWORD: str | None = None

    @field_validator("PSQL_DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(  # pylint: disable=no-member
            scheme="postgresql+asyncpg",
            username=values.data.get("PSQL_USER"),
            password=values.data.get("PSQL_PASSWORD"),
            host=values.data.get("PSQL_HOST"),
            port=values.data.get("PSQL_PORT"),
            path=f"{values.data.get('PSQL_DB') or ''}",
        )

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """Creates dictionary of values to pass to FastAPI app
        as **kwargs.

        Returns:
            dict: This can be unpacked as **kwargs to pass to FastAPI app.
        """

        fastapi_kwargs = {
            "title": self.PROJECT_NAME,
            "version": self.PROJECT_VERSION,
            "openapi_url": f"{self.API_STR}openapi.json",
            "default_response_class": JSONResponse,
        }

        if self.STAGING:
            fastapi_kwargs.update(
                {
                    "openapi_url": None,
                    "openapi_prefix": None,
                    "docs_url": None,
                    "redoc_url": None,
                }
            )
        return fastapi_kwargs

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')


settings = Settings()
