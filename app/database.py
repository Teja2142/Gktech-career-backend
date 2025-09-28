from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

database_url = settings.effective_database_url
if not database_url:
	raise RuntimeError(
		"Database connection not configured. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME in environment."
	)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
