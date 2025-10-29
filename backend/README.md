# Digital Mentorship Log - Backend API

FastAPI backend for the Digital Mentorship Log system, using Supabase for persistent storage.

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: Supabase (PostgreSQL)
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (JSON Web Tokens)
- **Storage**: Supabase Storage
- **Python**: 3.11+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection setup
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── mentorship_logs.py
│   │   ├── users.py
│   │   ├── facilities.py
│   │   ├── follow_ups.py
│   │   └── reports.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── mentorship_service.py
│   │   ├── user_service.py
│   │   └── facility_service.py
│   ├── middleware/          # Custom middleware
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/               # Helper utilities
│       ├── __init__.py
│       ├── security.py
│       └── helpers.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_mentorship_logs.py
│   └── test_users.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Supabase account and project
- pip or poetry for package management

### 2. Environment Setup

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Update the `.env` file with your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
```

### 3. Install Dependencies

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

### 4. Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Or run directly
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Models

### Core Models

- **User**: System users (mentors, supervisors, admins)
- **Facility**: Healthcare facilities
- **MentorshipLog**: Main mentorship visit logs
- **VisitObjective**: Visit objectives linked to logs
- **FollowUp**: Follow-up action items
- **Attachment**: File attachments for logs
- **UserFacilityAssignment**: User-facility relationships
- **AuditLog**: System audit trail

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh-token` - Refresh JWT token

### Mentorship Logs
- `GET /api/mentorship-logs` - List logs
- `POST /api/mentorship-logs` - Create new log
- `GET /api/mentorship-logs/{id}` - Get log details
- `PUT /api/mentorship-logs/{id}` - Update log
- `DELETE /api/mentorship-logs/{id}` - Delete log
- `POST /api/mentorship-logs/{id}/submit` - Submit for approval
- `POST /api/mentorship-logs/{id}/approve` - Approve log

### Users
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Facilities
- `GET /api/facilities` - List facilities
- `POST /api/facilities` - Create facility
- `GET /api/facilities/{id}` - Get facility
- `PUT /api/facilities/{id}` - Update facility

### Follow-Ups
- `GET /api/follow-ups` - List follow-ups
- `POST /api/mentorship-logs/{id}/follow-ups` - Create follow-up
- `PUT /api/follow-ups/{id}` - Update follow-up

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- SQL injection protection via SQLAlchemy ORM
- CORS configuration
- Request validation with Pydantic

## Contributing

1. Create a feature branch
2. Make changes with proper tests
3. Run code quality checks
4. Submit pull request

## License

Proprietary - Digital Mentorship Log System
