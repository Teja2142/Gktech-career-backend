# Career Submission FastAPI Application

A robust, production-ready FastAPI application for handling career form submissions, uploading resumes to Amazon S3, and saving applicant data to a PostgreSQL database (RDS-ready). Includes Swagger/OpenAPI support for easy API exploration.

## Features
- Upload resumes to Amazon S3
- Store applicant data in PostgreSQL (RDS-ready)
- SQLAlchemy ORM
- Pydantic validation
- Environment-based configuration
- CORS enabled
- Swagger UI (OpenAPI) at `/docs`

## Folder Structure
```
career_form_api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── schemas.py
│   ├── s3_utils.py
│   └── database.py
├── requirements.txt
├── README.md
├── .env
```

## Prerequisites
- Python 3.9+
- AWS S3 bucket and IAM credentials
- PostgreSQL database (RDS or self-hosted)

## Environment Variables (`.env`)
```
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_secret
AWS_BUCKET_NAME=your_bucket
AWS_REGION=your_region
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Installation
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
uvicorn app.main:app --reload
```

## API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Deployment
- Ready for Docker, EC2, Fly.io, Render, etc.
- Add logging, error handling, and admin dashboard as needed.

---

**Built with industry best practices for security, scalability, and maintainability.**
