from dotenv import load_dotenv
import os

load_dotenv() 

class Settings:
    """Configuration settings for the application."""

    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")


settings = Settings()
