import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = pathlib.Path(__file__).parent.parent


class Settings(BaseSettings):
    # Base
    jwt_secret: str
    jwt_leeway: float = 30.0
    optscale_auth_api_base_url: str
    optscale_rest_api_base_url: str
    optscale_cluster_secret: str
    debug: bool = False
    default_request_timeout: int = 10  # API Client

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="ffc_modifier_",
    )
