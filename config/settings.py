import os


class Settings:
    APP_NAME: str = "Python Blog API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://debankush:12345@localhost:5432/blogdb"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mysecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Default admin account, created on startup if missing
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@123")


settings = Settings()
