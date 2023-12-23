import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings, validator
from pydantic.error_wrappers import ErrorWrapper, ValidationError


class Settings(BaseSettings):
    PORT: int
    DB_TYPE: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    DB_DSN: str = ""

    @validator("DB_DSN", pre=True)
    def assemble_db_connection(cls, v: str, values: Dict[str, Any]) -> Any:
        # v is current field that are being validated, while values are the entire Settings class # noqa: E501
        if values.get("DB_TYPE") == "postgresql":
            HOST = values.get("DB_HOST")
            PORT = values.get("DB_PORT")
            USER = values.get("DB_USER")
            PASSWORD = values.get("DB_PASSWORD")
            NAME = values.get("DB_NAME")
            return f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"
        else:
            raise ValidationError(
                errors=[
                    ErrorWrapper(
                        Exception("unsupported db type for DB_TYPE"),
                        loc="DB_TYPE",
                    )
                ],
                model=None,
            )

    class Config:
        if "APP_CONFIG_FILE" in os.environ:
            env_file = (
                Path(__file__).parent / f"config/{os.environ['APP_CONFIG_FILE']}.env"
            )
            case_sensitive = True


settings = Settings.parse_obj({})
