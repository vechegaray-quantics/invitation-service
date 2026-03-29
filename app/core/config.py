from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Invitation Service"
    app_version: str = "0.1.0"
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    resend_api_key: str = ""
    email_from: str = "Quantics <onboarding@resend.dev>"
    public_interview_base_url: str = "https://encuestas-490902.web.app/interview"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()