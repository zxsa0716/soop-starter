"""환경 변수 → Pydantic settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Claude ---
    anthropic_api_key: str
    claude_model: str = "claude-opus-4-7"

    # --- data.go.kr API keys ---
    kfs_frsas1_key: str = ""
    law_go_kr_oc: str = "zxsa0716@kookmin.ac.kr"
    law_go_kr_key: str = ""
    vworld_api_key: str = ""
    vworld_domain: str = "localhost"
    komis_api_key: str = ""
    kosis_api_key: str = ""
    kma_grid_api_key: str = ""
    realestate_api_key: str = ""
    kfs_parcel_daily_key: str = ""
    forest_business_api_key: str = ""

    # --- GEE ---
    gee_service_account_email: str = ""
    gee_project_id: str = ""
    gee_service_account_key_path: str = "./gee-service-account.json"

    # --- Dadream BYOA ---
    dadream_base_url: str = "https://gis.kofpi.or.kr/dad_user"

    # --- Storage ---
    postgres_user: str = "soop"
    postgres_password: str = "change_me_in_local"
    postgres_db: str = "soop"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_ttl_seconds: int = 604_800  # 7d

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "soop"
    minio_secret_key: str = "change_me_in_local"
    minio_bucket_raw: str = "soop-raw"
    minio_bucket_models: str = "soop-models"

    chroma_host: str = "chroma"
    chroma_port: int = 8000

    # --- Backend ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # --- Observability ---
    log_level: str = "INFO"
    sentry_dsn: str = ""

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
