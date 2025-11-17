# Digital Mentorship Log - Backend API

A comprehensive FastAPI backend for managing healthcare mentorship activities, tracking action items, and generating operational reports. Built to digitize the ACE2 PDF mentorship form for efficient mentorship documentation and monitoring.

## Overview

The Digital Mentorship Log API provides a complete solution for:
- Managing mentorship visit documentation
- Tracking facilities and healthcare personnel
- Recording skills transfer and capacity building activities
- Managing follow-up action items
- Generating operational reports
- Handling file attachments for documentation
- User authentication and role-based access control

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Testing**: pytest with 87.95% code coverage
- **Storage**: Local filesystem (uploads directory)
- **Python**: 3.11+

## Features

### Core Functionality
- User management with role-based access control (Admin, Supervisor, Mentor)
- Facility management and tracking
- Comprehensive mentorship log creation following ACE2 form structure
- Skills transfer documentation with competency assessment
- Follow-up action item tracking with status workflows
- File attachment support (images, documents, spreadsheets)
- Operational reporting and analytics

### Security
- JWT-based authentication with token refresh
- Password hashing using bcrypt
- Role-based permissions (Admin, Supervisor, Mentor)
- SQL injection protection via SQLAlchemy ORM
- CORS middleware configuration
- Request validation with Pydantic schemas
- Secure file upload with type and size restrictions

### Testing
- Comprehensive test suite with 201 passing tests
- 87.95% code coverage
- Integration tests for all endpoints
- Authentication and permission testing
- Pytest fixtures for consistent test data

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas for request/response validation
│   ├── dependencies.py      # Dependency injection (auth, permissions)
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── users.py         # User management
│       ├── facilities.py    # Facility management
│       ├── mentorship_logs.py  # Mentorship log CRUD
│       ├── follow_ups.py    # Follow-up action items
│       ├── reports.py       # Operational reports
│       └── attachments.py   # File upload/download
├── tests/                   # Test suite (201 tests, 87.95% coverage)
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and configuration
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_facilities.py
│   ├── test_mentorship_logs.py
│   ├── test_follow_ups.py
│   ├── test_reports.py
│   └── test_attachments.py
├── alembic/                 # Database migration scripts
│   ├── versions/
│   └── env.py
├── uploads/                 # File attachment storage (gitignored)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore
├── alembic.ini             # Alembic configuration
├── API_DOCUMENTATION.md    # Detailed API reference
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Supabase recommended)
- pip for package management

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Update the `.env` file with your configuration:

```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database_name

# For Supabase:
# DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS Configuration (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate a secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 3. Database Setup

```bash
# Run migrations to create all tables
alembic upgrade head
```

**Verify database tables:**
```bash
python -c "from app.database import engine; from sqlalchemy import inspect; print([t for t in inspect(engine).get_table_names()])"
```

Expected tables:
- users
- facilities
- mentorship_logs
- skills_transfers
- follow_ups
- attachments

### 4. Run Development Server

```bash
# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Access interactive documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Create First Admin User

After starting the server, register an admin user:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword",
    "name": "System Admin",
    "designation": "Administrator",
    "region_state": "Nigeria",
    "role": "admin"
  }'
```

## API Documentation

For comprehensive API documentation including all endpoints, request/response schemas, authentication details, and examples, see:

**[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**

### Quick API Overview

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

#### User Management (Admin/Supervisor)
- `GET /api/users` - List users with filtering
- `GET /api/users/{id}` - Get user details
- `POST /api/users` - Create user (Admin only)
- `PUT /api/users/{id}` - Update user
- `PUT /api/users/{id}/activate` - Activate user (Admin only)
- `PUT /api/users/{id}/deactivate` - Deactivate user (Admin only)
- `DELETE /api/users/{id}` - Delete user (Admin only)

#### Facility Management
- `GET /api/facilities` - List facilities
- `GET /api/facilities/{id}` - Get facility
- `POST /api/facilities` - Create facility (Admin only)
- `PUT /api/facilities/{id}` - Update facility (Admin only)
- `DELETE /api/facilities/{id}` - Delete facility (Admin only)

#### Mentorship Logs
- `GET /api/mentorship-logs` - List logs with filtering
- `GET /api/mentorship-logs/{id}` - Get log details
- `POST /api/mentorship-logs` - Create mentorship log
- `PUT /api/mentorship-logs/{id}` - Update log
- `PUT /api/mentorship-logs/{id}/submit` - Submit for approval
- `PUT /api/mentorship-logs/{id}/approve` - Approve log (Supervisor/Admin)
- `PUT /api/mentorship-logs/{id}/return-to-draft` - Return to draft (Supervisor/Admin)
- `DELETE /api/mentorship-logs/{id}` - Delete log

#### Follow-Up Management
- `GET /api/follow-ups` - List follow-ups with filtering
- `GET /api/follow-ups/{id}` - Get follow-up details
- `POST /api/follow-ups` - Create follow-up action item
- `PUT /api/follow-ups/{id}` - Update follow-up
- `PUT /api/follow-ups/{id}/in-progress` - Mark as in progress
- `PUT /api/follow-ups/{id}/complete` - Mark as completed
- `DELETE /api/follow-ups/{id}` - Delete follow-up

#### File Attachments
- `POST /api/attachments/upload/{mentorship_log_id}` - Upload files
- `GET /api/attachments/{mentorship_log_id}` - List attachments
- `GET /api/attachments/download/{attachment_id}` - Download file
- `DELETE /api/attachments/{attachment_id}` - Delete attachment

#### Reports (Admin/Supervisor)
- `GET /api/reports/summary` - Overall summary statistics
- `GET /api/reports/mentorship-logs` - Mentorship logs report with filtering
- `GET /api/reports/follow-ups` - Follow-ups report with overdue tracking
- `GET /api/reports/facility-coverage` - Facility visit coverage report

## User Roles & Permissions

### Admin
- Full system access
- User management (create, update, deactivate, delete)
- Facility management (create, update, delete)
- Can approve mentorship logs
- Access to all reports
- Can manage all mentorship logs and follow-ups

### Supervisor
- View all users, facilities, and logs
- Approve mentorship logs
- Access to all reports
- Cannot create/delete users or facilities
- Can manage all follow-ups

### Mentor
- Create and manage own mentorship logs
- Create follow-ups for own logs
- View assigned facilities
- Submit logs for approval
- Update assigned follow-ups
- Cannot access reports or manage other users' data

## Database Models

### Core Models

**User**
- System users (mentors, supervisors, admins)
- Email-based authentication
- Role-based permissions
- Regional assignment

**Facility**
- Healthcare facilities
- Location details (state, LGA)
- Contact information
- Facility type classification

**MentorshipLog**
- Main visit documentation (ACE2 form)
- Visit details and duration
- Activities and thematic areas
- Observations and recommendations
- Status workflow (draft → submitted → approved)

**SkillsTransfer**
- Skills/knowledge transferred during visit
- Recipient details and cadre
- Transfer method
- Competency level assessment
- Follow-up requirements

**FollowUp**
- Action items from mentorship visits
- Assigned personnel
- Target dates and priority
- Status tracking (pending → in_progress → completed)
- Resource requirements

**Attachment**
- File uploads linked to mentorship logs
- Supported formats: images, PDFs, Office documents
- File size limit: 10MB per file
- Metadata tracking (size, type, uploader)

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_mentorship_logs.py

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_create"
```

### Test Coverage

Current coverage: **87.95%** (201 tests passing)

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
# On Windows:
start htmlcov/index.html
# On Linux/Mac:
open htmlcov/index.html
```

### Test Structure

Tests follow the **Arrange-Act-Assert** pattern and use pytest fixtures for:
- Database session management
- Test client creation
- User authentication tokens
- Sample data generation

## Database Migrations

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/
# Edit if necessary, then apply:
alembic upgrade head
```

### Migration Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

## File Uploads

### Configuration

File uploads are stored in the `uploads/` directory (excluded from git).

**Allowed file types:**
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`
- Documents: `.pdf`, `.doc`, `.docx`
- Spreadsheets: `.xls`, `.xlsx`
- Presentations: `.ppt`, `.pptx`
- Archives: `.zip`, `.rar`

**File size limit:** 10MB per file

### Storage Structure

```
uploads/
└── {mentorship_log_id}/
    ├── {uuid1}.jpg
    ├── {uuid2}.pdf
    └── {uuid3}.docx
```

## Deployment

### Production Checklist

1. **Environment Configuration**
   - Generate strong SECRET_KEY using `openssl rand -hex 32`
   - Set production DATABASE_URL
   - Configure ALLOWED_ORIGINS for your frontend domain
   - Set ALLOWED_HOSTS to your production domain

2. **Database Setup**
   - Run migrations: `alembic upgrade head`
   - Create admin user via API

3. **Security**
   - Enable HTTPS/SSL
   - Configure firewall rules
   - Set up database backups
   - Review CORS settings
   - Implement rate limiting (recommended)

4. **Application Server**
   - Use production ASGI server (Gunicorn + Uvicorn workers)
   - Set appropriate worker count
   - Configure logging

5. **File Storage**
   - Ensure uploads/ directory has proper permissions
   - Consider using cloud storage for production (S3, Google Cloud Storage)
   - Set up backup strategy for uploaded files

### Example Production Command

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mentorship-api .
docker run -p 8000:8000 --env-file .env mentorship-api
```

## Development Guidelines

### Code Quality

```bash
# Format code with black
black app/ tests/

# Sort imports with isort
isort app/ tests/

# Lint with flake8
flake8 app/ tests/ --max-line-length=120
```

### Development Workflow

1. Create feature branch from main
2. Write tests first (TDD approach)
3. Implement feature
4. Run tests and ensure coverage
5. Run code quality checks
6. Submit pull request

### Adding New Endpoints

1. Add route handler in appropriate router file (`app/routers/`)
2. Define Pydantic schemas in `app/schemas.py`
3. Add/update models in `app/models.py` if needed
4. Create database migration if model changes
5. Write comprehensive tests in `tests/`
6. Update API_DOCUMENTATION.md
7. Ensure all tests pass with good coverage

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "from app.database import engine; engine.connect(); print('Connection successful')"
```

### Migration Issues

```bash
# If migrations are out of sync:
alembic stamp head

# Create new migration:
alembic revision --autogenerate -m "Fix migration"
```

### Test Database Issues

Tests use an in-memory SQLite database. If tests fail:
1. Ensure all dependencies are installed
2. Check that models are properly imported in tests
3. Verify fixtures are correctly configured in `conftest.py`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Implement your feature
5. Ensure all tests pass (`pytest`)
6. Run code quality checks
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Support

For issues, questions, or contributions:
- Check the API_DOCUMENTATION.md for endpoint details
- Review test files for usage examples
- Refer to FastAPI documentation: https://fastapi.tiangolo.com/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/

## License

Proprietary - Digital Mentorship Log System
