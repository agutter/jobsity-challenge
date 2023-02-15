from pydantic import BaseSettings

#Type definitions for pydantic settings in .env file.
class Settings(BaseSettings):
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    CLIENT_ORIGIN: str

    class Config:
        env_file = './.env'

#Load and create the settings.
settings = Settings()
