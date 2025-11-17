# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Digital Mentorship Log (DML) is a full-stack application for healthcare mentorship management. It digitizes the ACE2 PDF mentorship form, allowing mentors to plan visits, document activities, track follow-ups, and generate reports.

**Stack:**
- Backend: FastAPI (Python 3.11+) with PostgreSQL via Supabase
- Frontend: Next.js 14+ (TypeScript) with Tailwind CSS and DaisyUI
- Deployment: Vercel (backend via serverless functions, frontend as static site)
- Storage: Supabase Storage for file attachments
- Auth: JWT tokens with bcrypt password hashing

## Development Commands

### Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head                                    # Apply all migrations
alembic revision --autogenerate -m "description"        # Create new migration
alembic downgrade -1                                    # Rollback one migration

# Testing
pytest                                                  # Run all tests
pytest tests/test_mentorship_logs.py                    # Run specific test file
pytest --cov=app --cov-report=html                      # Run with coverage report
pytest -v                                               # Verbose output
pytest -k "test_create"                                 # Run tests matching pattern

# Code quality
black app/ tests/                                       # Format code
isort app/ tests/                                       # Sort imports
flake8 app/ tests/ --max-line-length=120               # Lint code
```

### Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev              # Starts on http://localhost:3000

# Build and production
npm run build            # Build for production
npm start                # Start production server

# Code quality
npm run lint             # Run ESLint
npm run format           # Format with Prettier
```

## Architecture Overview

### Backend Structure

The backend uses a layered architecture:

1. **Routers** (`app/routers/`): Handle HTTP requests, define API endpoints
2. **Models** (`app/models.py`): SQLAlchemy ORM models defining database schema
3. **Schemas** (`app/schemas.py`): Pydantic models for request/response validation
4. **Dependencies** (`app/dependencies.py`): Dependency injection for auth and permissions
5. **Database** (`app/database.py`): Connection management with NullPool for Supabase

**Key Design Decisions:**
- Uses **NullPool** (no connection pooling) to prevent connection exhaustion on Supabase free tier (max 15-20 connections)
- Each request creates a fresh connection that's immediately destroyed after use
- Database sessions are managed via `get_db()` dependency with proper cleanup in finally block
- For serverless (Vercel), uses standard pooling with `pool_pre_ping=True`

### Frontend Structure

The frontend uses Next.js App Router with a feature-based structure:

1. **App Directory** (`app/`): Pages using Next.js 14+ file-based routing
2. **Components** (`components/`): Reusable React components
3. **Lib** (`lib/`): Utilities, API clients, stores, and hooks
   - `lib/api/`: Service modules for backend communication (axios-based)
   - `lib/stores/`: Zustand stores for global state management
4. **Types** (`types/`): TypeScript type definitions

**Key Patterns:**
- Protected routes use `ProtectedRoute` component wrapper
- API calls centralized in service modules under `lib/api/`
- Forms use React Hook Form + Zod for validation
- State management with Zustand (lightweight alternative to Redux)
- Styling with Tailwind CSS + DaisyUI component library

### Database Schema

**Core Tables:**
- `users`: System users (mentors, supervisors, admins) with role-based access
- `facilities`: Healthcare facilities tracked by the system
- `mentorship_logs`: Main visit documentation (ACE2 form data)
- `skills_transfers`: Skills/knowledge transferred during visits
- `follow_ups`: Action items from visits with status tracking
- `attachments`: File uploads linked to mentorship logs

**Important Relationships:**
- `mentorship_logs` → `facilities` (many-to-one)
- `mentorship_logs` → `users` (mentor_id, many-to-one)
- `mentorship_logs` → `skills_transfers` (one-to-many)
- `mentorship_logs` → `follow_ups` (one-to-many)
- `mentorship_logs` → `attachments` (one-to-many)

### Authentication & Authorization

**JWT Flow:**
1. User logs in via `POST /api/auth/login`
2. Backend validates credentials and returns JWT token
3. Frontend stores token and includes in `Authorization: Bearer <token>` header
4. Backend validates token via `get_current_user` dependency
5. Role-based permissions enforced via `require_admin()` and `require_supervisor()` dependencies

**User Roles:**
- **Mentor**: Create/edit own logs, submit for approval, view assigned facilities
- **Supervisor**: View all logs, approve logs, access reports, cannot manage users/facilities
- **Admin**: Full system access including user/facility management

## Working with This Codebase

### Adding a New API Endpoint

1. Define Pydantic schemas in `backend/app/schemas.py`
2. Add route handler in appropriate router file (`backend/app/routers/`)
3. Add database model if needed in `backend/app/models.py`
4. Create migration: `alembic revision --autogenerate -m "description"`
5. Apply migration: `alembic upgrade head`
6. Write tests in `backend/tests/`
7. Update `API_DOCUMENTATION.md` if external-facing

### Adding a New Frontend Page

1. Create page file in `app/` directory (e.g., `app/new-feature/page.tsx`)
2. Add navigation link in `components/layouts/DashboardLayout.tsx`
3. Create API service in `lib/api/` if needed
4. Define TypeScript types in `types/index.ts`
5. Wrap with `ProtectedRoute` if authentication required

### Working with Forms

Backend uses Pydantic for validation. Frontend uses React Hook Form + Zod:

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const schema = z.object({
  field: z.string().min(1, 'Required'),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

### Database Connection Management

**Critical:** The backend uses `NullPool` for local development to avoid exhausting Supabase's connection limit. This means:
- No connection pooling - connections are created and destroyed immediately
- Higher latency but prevents "too many connections" errors
- For production/Vercel, standard pooling is used with `pool_pre_ping=True`

**When modifying database code:**
- Always use the `get_db()` dependency in route handlers
- Never manually create engine instances
- Ensure sessions are properly closed in finally blocks

### File Storage

Uses Supabase Storage for file attachments:
- Bucket: `mentorship-attachments` (configured in `app/storage.py`)
- Max file size: 10MB (configurable in `app/config.py`)
- Allowed types: Images, PDFs, Office documents, archives
- Files organized by mentorship_log_id

### Testing Strategy

**Backend:**
- Uses pytest with SQLite in-memory database
- Fixtures in `tests/conftest.py` provide test client, DB session, auth tokens
- Test coverage target: >85% (currently 87.95%)
- Tests follow Arrange-Act-Assert pattern

**Frontend:**
- Component tests should be added as features grow
- Use testing-library patterns for React components

## Common Patterns

### Backend Error Handling

```python
from fastapi import HTTPException, status

# Not found
raise HTTPException(status_code=404, detail="Resource not found")

# Unauthorized
raise HTTPException(status_code=401, detail="Invalid credentials")

# Forbidden
raise HTTPException(status_code=403, detail="Insufficient permissions")

# Validation error (Pydantic handles automatically)
```

### Frontend API Calls

```typescript
import { apiClient } from '@/lib/api/client';

// GET request
const response = await apiClient.get('/mentorship-logs');

// POST with data
const response = await apiClient.post('/mentorship-logs', logData);

// Error handling is centralized in apiClient
```

### State Management

```typescript
import { useAuthStore } from '@/lib/stores/auth.store';

const { user, login, logout, isAuthenticated } = useAuthStore();
```

## Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_STORAGE_BUCKET=mentorship-attachments
SECRET_KEY=...  # Generate with: openssl rand -hex 32
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## Deployment

**Vercel Deployment:**
- Configuration in `vercel.json` routes `/api/*` to `api/index.py`
- Backend runs as serverless function
- Frontend builds as static site with SSR support
- Supabase PostgreSQL and Storage used for persistence

**Important:** When deploying, ensure:
1. All environment variables are set in Vercel dashboard
2. Database migrations are applied: `alembic upgrade head`
3. Supabase Storage bucket exists and has proper CORS settings

## Key Files Reference

- `backend/app/main.py` - FastAPI app initialization, middleware, router registration
- `backend/app/models.py` - All SQLAlchemy ORM models
- `backend/app/schemas.py` - All Pydantic schemas
- `backend/app/dependencies.py` - Auth dependencies and permission checks
- `backend/app/database.py` - Database connection with NullPool configuration
- `frontend/lib/api/client.ts` - Axios client with auth interceptors
- `frontend/lib/stores/auth.store.ts` - Authentication state management
- `frontend/components/auth/ProtectedRoute.tsx` - Route protection wrapper

## Documentation

- `API_DOCUMENTATION.md` - Complete API reference with request/response examples
- `backend/README.md` - Backend setup and architecture details
- `frontend/README.md` - Frontend setup and component guidelines
- `Digital Mentorship Log (DML) – Development Guide.md` - Comprehensive system design

## Notes for AI Assistants

- The codebase follows RESTful API conventions
- Backend uses async/await patterns where appropriate
- Frontend components should be typed with TypeScript interfaces
- When adding features, maintain consistency with existing patterns
- Database migrations must be created for schema changes
- Tests should be written for new endpoints and critical functionality
- The project uses Python type hints and TypeScript for type safety throughout
