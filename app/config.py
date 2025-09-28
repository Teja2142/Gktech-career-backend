from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()


class Settings:
    """Configuration settings for the application.

    Reads environment variables via `python-dotenv`. If a full `DATABASE_URL`
    is not provided, it will be constructed from individual DB components.
    """

    # AWS legacy keys (kept for compatibility)
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")

    # MinIO settings (for local object storage)
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")
    MINIO_SECURE = os.getenv("MINIO_SECURE")

    # Database: accept either a full DATABASE_URL or individual components
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    # Optional driver prefix for SQLAlchemy (example: 'mysql+pymysql')
    DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")

    @property
    def effective_database_url(self) -> str:
        """Return a usable DATABASE_URL. If `DATABASE_URL` is set, return it.

        Otherwise, attempt to construct one from individual DB_* values.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # require all components to construct URL
        if all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME]):
            user = quote_plus(self.DB_USER)
            password = quote_plus(self.DB_PASSWORD)
            return f"{self.DB_DRIVER}://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # fallback to None to allow downstream code to raise useful error
        return None


settings = Settings()
