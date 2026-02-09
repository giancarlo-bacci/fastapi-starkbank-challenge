from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    starkbank_project_id: str
    starkbank_private_key_path: str | None = None
    starkbank_environment: str = "sandbox"
    starkbank_private_key: str | None = None
    enable_scheduler: bool = True
    invoice_interval_minutes: int = 180

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",   # ← recomendo MUITO
    )

settings = Settings()
