from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Invitation Service"
    app_version: str = "0.1.0"
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    resend_api_key: str = ""
    email_from: str = "Research <noreply@mail.quantics.cl>"
    public_interview_base_url: str = "https://encuestas-490902.web.app/interview"

    email_logo_url: str = "https://dummyimage.com/180x52/0d1b2a/ffffff.png&text=Quantics"
    email_hero_image_url: str = "https://images.unsplash.com/photo-1527689368864-3a821dbccc34?auto=format&fit=crop&w=1200&q=80"
    email_support_email: str = "hola@quantics.cl"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()