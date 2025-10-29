# Digital Mentorship Log (DML) – Development Guide
## Next.js Frontend & FastAPI Backend

**Author:** Manus AI  
**Version:** 1.0  
**Last Updated:** October 2025  
**Target Rollout:** November 2025

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Implementation](#frontend-implementation)
6. [Backend Implementation](#backend-implementation)
7. [Authentication & Security](#authentication--security)
8. [Deployment & DevOps](#deployment--devops)
9. [Development Workflow](#development-workflow)

---

## System Architecture

### Overview

The Digital Mentorship Log is built on a modern, lightweight stack designed for rapid development and deployment:

- **Frontend:** Next.js 14+ (React framework with built-in SSR, API routes, and optimized performance)
- **Backend:** FastAPI (Python async framework for high-performance REST APIs)
- **Database:** PostgreSQL (relational database for structured mentorship data)
- **Authentication:** JWT tokens with optional SSO integration
- **File Storage:** Local filesystem or cloud storage (AWS S3, Google Cloud Storage)
- **Deployment:** Docker containers with orchestration via Docker Compose or Kubernetes

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Next.js Frontend (React Components, Pages, API)    │   │
│  │  - Dashboard, Forms, Reports                         │   │
│  │  - Authentication UI, User Management               │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           │ REST API
┌──────────────────────────┴──────────────────────────────────┐
│                     API Layer                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python)                            │   │
│  │  - Route Handlers, Business Logic                    │   │
│  │  - Authentication, Authorization                     │   │
│  │  - Data Validation, Error Handling                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ SQL
                           │ Connection Pool
┌──────────────────────────┴──────────────────────────────────┐
│                   Data Layer                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                 │   │
│  │  - Tables, Indexes, Constraints                      │   │
│  │  - Audit Logs, Versioning                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

**Separation of Concerns:** Frontend and backend are completely decoupled, communicating only through REST APIs. This allows independent scaling and development.

**Stateless Backend:** FastAPI backend is stateless, enabling horizontal scaling. Session state is managed via JWT tokens stored on the client.

**Async-First:** FastAPI's async capabilities allow handling multiple concurrent requests efficiently without blocking I/O operations.

**Type Safety:** Both Next.js (TypeScript) and FastAPI (Python type hints) enforce type safety, reducing runtime errors and improving code maintainability.

---

## Core Components

### Frontend Components (Next.js)

The frontend is organized into reusable React components following a feature-based structure:

#### 1. **Layout Components**
- `AppLayout`: Main application shell with navigation, sidebar, and content area
- `AuthLayout`: Layout for login and authentication pages
- `DashboardLayout`: Specialized layout for dashboard views with widgets

#### 2. **Form Components**
- `MentorshipLogForm`: Main form for creating and editing mentorship logs
- `PlanningSection`: Pre-visit planning form (facility, date, objectives, resources)
- `ReportingSection`: Post-visit reporting form (outcomes, action items, lessons learned)
- `DynamicFieldArray`: Reusable component for dynamic form fields (objectives, action items)
- `FileUploadField`: Component for uploading attachments (photos, documents)

#### 3. **Data Display Components**
- `MentorshipLogTable`: Paginated table displaying mentorship logs with filtering and sorting
- `DashboardCards`: KPI cards showing metrics (planned vs completed visits, etc.)
- `FacilityPerformanceChart`: Chart component for facility performance trends
- `TimelineView`: Timeline display of mentorship visits and follow-ups

#### 4. **User Management Components**
- `UserProfile`: Display and edit user profile information
- `UserRoleSelector`: Component for assigning roles and permissions
- `FacilityAssignment`: Multi-select component for assigning facilities to mentors

#### 5. **Navigation Components**
- `Navbar`: Top navigation bar with user menu and notifications
- `Sidebar`: Left sidebar with navigation links based on user role
- `Breadcrumb`: Breadcrumb navigation for page hierarchy

### Backend Components (FastAPI)

The backend is organized into modular services and routes:

#### 1. **Route Handlers**
- `auth.py`: Authentication endpoints (login, logout, token refresh, SSO)
- `mentorship_logs.py`: CRUD endpoints for mentorship logs
- `users.py`: User management endpoints (create, read, update, delete users)
- `facilities.py`: Facility management endpoints
- `follow_ups.py`: Follow-up action item management
- `reports.py`: Report generation and export endpoints
- `notifications.py`: Notification endpoints (email, in-app alerts)

#### 2. **Service Layer**
- `auth_service.py`: Authentication logic (JWT generation, password hashing, SSO integration)
- `mentorship_service.py`: Business logic for mentorship log operations
- `user_service.py`: User management logic
- `facility_service.py`: Facility data management
- `report_service.py`: Report generation logic
- `notification_service.py`: Email and notification handling

#### 3. **Data Access Layer**
- `database.py`: Database connection and session management
- `models.py`: SQLAlchemy ORM models
- `repositories.py`: Data access objects (DAOs) for database queries

#### 4. **Middleware & Utilities**
- `auth_middleware.py`: JWT token validation and user context injection
- `error_handlers.py`: Global exception handling and error responses
- `validators.py`: Request data validation and sanitization
- `utils.py`: Helper functions (date formatting, file handling, etc.)

---

## Database Schema

### Entity-Relationship Diagram

```
User (1) ──────────── (M) Mentorship_Log
  │                          │
  │                          ├─ (1) Facility
  │                          └─ (M) Follow_Up
  │
  └─ (M) User_Facility_Assignment

Facility (1) ──────────── (M) Mentorship_Log
```

### Core Tables

#### 1. **users**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| name | VARCHAR(255) | NOT NULL | Full name |
| designation | VARCHAR(100) | | Job title/position |
| region_state | VARCHAR(100) | | Geographic region or state |
| role | ENUM | NOT NULL | 'mentor', 'supervisor', 'admin' |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

#### 2. **facilities**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique facility identifier |
| name | VARCHAR(255) | NOT NULL | Facility name |
| code | VARCHAR(50) | UNIQUE | Facility code |
| location | VARCHAR(255) | | Geographic location |
| state | VARCHAR(100) | | State/region |
| facility_type | VARCHAR(100) | | Type of facility (clinic, hospital, etc.) |
| contact_person | VARCHAR(255) | | Primary contact name |
| contact_email | VARCHAR(255) | | Contact email |
| contact_phone | VARCHAR(20) | | Contact phone number |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

#### 3. **mentorship_logs**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique log identifier |
| facility_id | UUID | FOREIGN KEY | Reference to facility |
| mentor_id | UUID | FOREIGN KEY | Reference to mentor user |
| visit_date | DATE | NOT NULL | Planned or actual visit date |
| status | ENUM | DEFAULT 'draft' | 'draft', 'submitted', 'approved', 'completed' |
| performance_summary | TEXT | | Summary of facility performance |
| identified_gaps | TEXT | | Performance gaps identified |
| trends_summary | TEXT | | Trends from previous periods |
| previous_followup | TEXT | | Follow-up from previous visit |
| persistent_challenges | TEXT | | Ongoing issues |
| progress_made | TEXT | | Achievements since last visit |
| resources_needed | TEXT | | Required tools or materials |
| facility_requests | TEXT | | Requests from facility |
| logistics_notes | TEXT | | Transport, lodging arrangements |
| visit_outcomes | TEXT | | Post-visit outcomes and notes |
| lessons_learned | TEXT | | Key learnings from visit |
| created_at | TIMESTAMP | DEFAULT NOW() | Log creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| submitted_at | TIMESTAMP | | Submission timestamp |
| approved_at | TIMESTAMP | | Approval timestamp |
| approved_by | UUID | FOREIGN KEY | Approving supervisor |

#### 4. **visit_objectives**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique objective identifier |
| mentorship_log_id | UUID | FOREIGN KEY | Reference to mentorship log |
| objective_text | TEXT | NOT NULL | Objective description |
| sequence | INTEGER | | Display order |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

#### 5. **follow_ups**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique follow-up identifier |
| mentorship_log_id | UUID | FOREIGN KEY | Reference to mentorship log |
| action_item | TEXT | NOT NULL | Description of action item |
| status | ENUM | DEFAULT 'pending' | 'pending', 'in_progress', 'completed' |
| assigned_to | UUID | FOREIGN KEY | User responsible for action |
| due_date | DATE | | Due date for completion |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| completed_at | TIMESTAMP | | Completion timestamp |

#### 6. **attachments**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique attachment identifier |
| mentorship_log_id | UUID | FOREIGN KEY | Reference to mentorship log |
| file_name | VARCHAR(255) | NOT NULL | Original file name |
| file_path | VARCHAR(500) | NOT NULL | Storage path |
| file_size | BIGINT | | File size in bytes |
| file_type | VARCHAR(50) | | MIME type |
| uploaded_by | UUID | FOREIGN KEY | User who uploaded |
| created_at | TIMESTAMP | DEFAULT NOW() | Upload time |

#### 7. **audit_logs**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique audit log identifier |
| user_id | UUID | FOREIGN KEY | User performing action |
| entity_type | VARCHAR(100) | | Type of entity modified |
| entity_id | UUID | | ID of modified entity |
| action | VARCHAR(50) | | 'create', 'update', 'delete' |
| changes | JSONB | | JSON diff of changes |
| created_at | TIMESTAMP | DEFAULT NOW() | Action timestamp |

#### 8. **user_facility_assignments**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique assignment identifier |
| user_id | UUID | FOREIGN KEY | Reference to user |
| facility_id | UUID | FOREIGN KEY | Reference to facility |
| assigned_at | TIMESTAMP | DEFAULT NOW() | Assignment time |

### Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_mentorship_logs_facility_id ON mentorship_logs(facility_id);
CREATE INDEX idx_mentorship_logs_mentor_id ON mentorship_logs(mentor_id);
CREATE INDEX idx_mentorship_logs_visit_date ON mentorship_logs(visit_date);
CREATE INDEX idx_mentorship_logs_status ON mentorship_logs(status);
CREATE INDEX idx_follow_ups_mentorship_log_id ON follow_ups(mentorship_log_id);
CREATE INDEX idx_follow_ups_status ON follow_ups(status);
CREATE INDEX idx_user_facility_assignments_user_id ON user_facility_assignments(user_id);
CREATE INDEX idx_user_facility_assignments_facility_id ON user_facility_assignments(facility_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## API Endpoints

### Authentication Endpoints

```
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh-token
POST   /api/auth/register (admin only)
GET    /api/auth/me
POST   /api/auth/sso/callback
```

### Mentorship Log Endpoints

```
GET    /api/mentorship-logs                    # List logs (with filters)
POST   /api/mentorship-logs                    # Create new log
GET    /api/mentorship-logs/{id}               # Get single log
PUT    /api/mentorship-logs/{id}               # Update log
DELETE /api/mentorship-logs/{id}               # Delete log (soft delete)
POST   /api/mentorship-logs/{id}/submit        # Submit for approval
POST   /api/mentorship-logs/{id}/approve       # Approve log (supervisor)
POST   /api/mentorship-logs/{id}/export        # Export as PDF/Excel
```

### User Management Endpoints

```
GET    /api/users                              # List users (admin only)
POST   /api/users                              # Create user (admin only)
GET    /api/users/{id}                         # Get user profile
PUT    /api/users/{id}                         # Update user profile
DELETE /api/users/{id}                         # Delete user (admin only)
POST   /api/users/{id}/assign-facilities       # Assign facilities to mentor
GET    /api/users/{id}/assigned-facilities     # Get assigned facilities
```

### Facility Endpoints

```
GET    /api/facilities                         # List all facilities
POST   /api/facilities                         # Create facility (admin)
GET    /api/facilities/{id}                    # Get facility details
PUT    /api/facilities/{id}                    # Update facility
DELETE /api/facilities/{id}                    # Delete facility (admin)
GET    /api/facilities/{id}/performance        # Get facility performance metrics
```

### Follow-Up Endpoints

```
GET    /api/follow-ups                         # List follow-ups
POST   /api/mentorship-logs/{id}/follow-ups    # Create follow-up
PUT    /api/follow-ups/{id}                    # Update follow-up
PUT    /api/follow-ups/{id}/status             # Update follow-up status
DELETE /api/follow-ups/{id}                    # Delete follow-up
```

### Report & Analytics Endpoints

```
GET    /api/reports/dashboard                  # Dashboard metrics
GET    /api/reports/mentor-summary             # Mentor performance summary
GET    /api/reports/facility-summary           # Facility performance summary
GET    /api/reports/export                     # Export reports (PDF/Excel)
GET    /api/analytics/trends                   # Performance trends
```

### File Upload Endpoints

```
POST   /api/attachments/upload                 # Upload file
GET    /api/attachments/{id}                   # Download file
DELETE /api/attachments/{id}                   # Delete attachment
```

### Example Request/Response

**Request:** Create Mentorship Log
```json
POST /api/mentorship-logs
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "facility_id": "550e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-15",
  "performance_summary": "Overall facility performance is satisfactory...",
  "identified_gaps": "Staffing levels below target...",
  "objectives": [
    "Improve staff training protocols",
    "Strengthen inventory management",
    "Enhance patient documentation"
  ],
  "resources_needed": "Training materials, reference guides",
  "staff_to_engage": ["Clinical staff", "Administrative staff"]
}
```

**Response:** Success (201 Created)
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "facility_id": "550e8400-e29b-41d4-a716-446655440000",
  "mentor_id": "770e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-15",
  "status": "draft",
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T10:30:00Z"
}
```

---

## Frontend Implementation

### Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── dashboard/
│   │   ├── page.tsx            # Dashboard main
│   │   ├── mentor/             # Mentor dashboard
│   │   └── supervisor/         # Supervisor dashboard
│   ├── mentorship-logs/
│   │   ├── page.tsx            # Logs list
│   │   ├── [id]/
│   │   │   ├── page.tsx        # View log
│   │   │   └── edit/page.tsx   # Edit log
│   │   └── new/page.tsx        # Create new log
│   ├── auth/
│   │   ├── login/page.tsx      # Login page
│   │   └── profile/page.tsx    # User profile
│   └── api/
│       └── [...].ts            # API route handlers
├── components/
│   ├── layouts/
│   │   ├── AppLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   └── DashboardLayout.tsx
│   ├── forms/
│   │   ├── MentorshipLogForm.tsx
│   │   ├── PlanningSection.tsx
│   │   ├── ReportingSection.tsx
│   │   └── DynamicFieldArray.tsx
│   ├── tables/
│   │   └── MentorshipLogTable.tsx
│   ├── charts/
│   │   ├── PerformanceTrendChart.tsx
│   │   └── KPICards.tsx
│   └── common/
│       ├── Navbar.tsx
│       ├── Sidebar.tsx
│       └── Breadcrumb.tsx
├── lib/
│   ├── api.ts                  # API client
│   ├── auth.ts                 # Auth utilities
│   ├── hooks.ts                # Custom React hooks
│   └── utils.ts                # Helper functions
├── styles/
│   └── globals.css
├── types/
│   └── index.ts                # TypeScript types
└── package.json
```

### Key Frontend Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| next | React framework | 14+ |
| react | UI library | 18+ |
| typescript | Type safety | 5+ |
| axios | HTTP client | 1.6+ |
| react-hook-form | Form management | 7+ |
| zod | Schema validation | 3+ |
| recharts | Data visualization | 2+ |
| date-fns | Date utilities | 2+ |
| tailwindcss | CSS framework | 3+ |
| zustand | State management | 4+ |

### Example: MentorshipLogForm Component

```typescript
// components/forms/MentorshipLogForm.tsx
'use client';

import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import axios from 'axios';

// Validation schema
const mentorshipLogSchema = z.object({
  facility_id: z.string().uuid('Invalid facility'),
  visit_date: z.string().refine(date => new Date(date) > new Date(), {
    message: 'Visit date must be in the future'
  }),
  performance_summary: z.string().min(10, 'Summary required'),
  identified_gaps: z.string().optional(),
  objectives: z.array(z.string()).min(1, 'At least one objective required'),
  resources_needed: z.string().optional(),
});

type FormData = z.infer<typeof mentorshipLogSchema>;

export default function MentorshipLogForm({ logId }: { logId?: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(mentorshipLogSchema),
  });

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const endpoint = logId 
        ? `/api/mentorship-logs/${logId}` 
        : '/api/mentorship-logs';
      
      const method = logId ? 'PUT' : 'POST';
      
      const response = await axios({
        method,
        url: endpoint,
        data,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      // Success handling
      console.log('Log saved:', response.data);
      // Redirect or show success message
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save log');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && <div className="error-alert">{error}</div>}
      
      <div>
        <label>Facility</label>
        <Controller
          name="facility_id"
          control={control}
          render={({ field }) => (
            <select {...field} className="input">
              <option value="">Select facility</option>
              {/* Options populated from API */}
            </select>
          )}
        />
        {errors.facility_id && <span className="error">{errors.facility_id.message}</span>}
      </div>

      <div>
        <label>Visit Date</label>
        <Controller
          name="visit_date"
          control={control}
          render={({ field }) => (
            <input type="date" {...field} className="input" />
          )}
        />
        {errors.visit_date && <span className="error">{errors.visit_date.message}</span>}
      </div>

      <div>
        <label>Performance Summary</label>
        <Controller
          name="performance_summary"
          control={control}
          render={({ field }) => (
            <textarea {...field} className="textarea" rows={4} />
          )}
        />
        {errors.performance_summary && <span className="error">{errors.performance_summary.message}</span>}
      </div>

      <button 
        type="submit" 
        disabled={isSubmitting}
        className="btn btn-primary"
      >
        {isSubmitting ? 'Saving...' : 'Save Log'}
      </button>
    </form>
  );
}
```

---

## Backend Implementation

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/
│   │   ├── auth.py             # Auth routes
│   │   ├── mentorship_logs.py   # Mentorship log routes
│   │   ├── users.py            # User management routes
│   │   ├── facilities.py        # Facility routes
│   │   ├── follow_ups.py        # Follow-up routes
│   │   └── reports.py          # Report routes
│   ├── services/
│   │   ├── auth_service.py      # Auth logic
│   │   ├── mentorship_service.py # Mentorship logic
│   │   ├── user_service.py      # User logic
│   │   └── report_service.py    # Report logic
│   ├── middleware/
│   │   └── auth.py             # JWT middleware
│   └── utils/
│       ├── security.py         # Password hashing, JWT
│       ├── validators.py       # Data validation
│       └── helpers.py          # Helper functions
├── tests/
│   ├── test_auth.py
│   ├── test_mentorship_logs.py
│   └── test_users.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

### Key Backend Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| fastapi | Web framework | 0.100+ |
| uvicorn | ASGI server | 0.23+ |
| sqlalchemy | ORM | 2.0+ |
| psycopg2-binary | PostgreSQL driver | 2.9+ |
| pydantic | Data validation | 2.0+ |
| python-jose | JWT handling | 3.3+ |
| passlib | Password hashing | 1.7+ |
| python-multipart | File uploads | 0.0.6+ |
| pytest | Testing | 7.0+ |

### Example: FastAPI Main Application

```python
# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import auth, mentorship_logs, users, facilities, follow_ups, reports
from app.middleware.auth import AuthMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")
    yield
    # Shutdown
    print("Application shutting down...")

app = FastAPI(
    title="Digital Mentorship Log API",
    description="API for managing mentorship activities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(mentorship_logs.router, prefix="/api/mentorship-logs", tags=["mentorship_logs"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(facilities.router, prefix="/api/facilities", tags=["facilities"])
app.include_router(follow_ups.router, prefix="/api/follow-ups", tags=["follow_ups"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example: Mentorship Log Routes

```python
# app/routers/mentorship_logs.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.schemas import MentorshipLogCreate, MentorshipLogUpdate, MentorshipLogResponse
from app.services.mentorship_service import MentorshipService
from app.middleware.auth import get_current_user

router = APIRouter()
service = MentorshipService()

@router.get("", response_model=List[MentorshipLogResponse])
async def list_mentorship_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    facility_id: str = Query(None),
    status: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """List mentorship logs with optional filtering"""
    logs = service.list_logs(
        db=db,
        user_id=current_user.id,
        facility_id=facility_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return logs

@router.post("", response_model=MentorshipLogResponse, status_code=201)
async def create_mentorship_log(
    log_data: MentorshipLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new mentorship log"""
    log = service.create_log(db=db, log_data=log_data, mentor_id=current_user.id)
    return log

@router.get("/{log_id}", response_model=MentorshipLogResponse)
async def get_mentorship_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific mentorship log"""
    log = service.get_log(db=db, log_id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Authorization check
    if log.mentor_id != current_user.id and current_user.role != "supervisor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return log

@router.put("/{log_id}", response_model=MentorshipLogResponse)
async def update_mentorship_log(
    log_id: str,
    log_data: MentorshipLogUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a mentorship log"""
    log = service.get_log(db=db, log_id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Authorization check
    if log.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_log = service.update_log(db=db, log_id=log_id, log_data=log_data)
    return updated_log

@router.post("/{log_id}/submit")
async def submit_mentorship_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a mentorship log for approval"""
    log = service.get_log(db=db, log_id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    if log.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_log = service.submit_log(db=db, log_id=log_id)
    return {"message": "Log submitted for approval", "log": updated_log}
```

---

## Authentication & Security

### JWT Token Implementation

The system uses JWT (JSON Web Tokens) for stateless authentication:

```python
# app/utils/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

### Role-Based Access Control (RBAC)

```python
# app/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.utils.security import decode_token
from app.database import get_db
from app.models import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def require_role(*roles: str):
    """Dependency to check user role"""
    async def check_role(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return check_role
```

### Usage Example

```python
@router.post("/users", dependencies=[Depends(require_role("admin"))])
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (admin only)"""
    # Implementation
    pass
```

---

## Deployment & DevOps

### Docker Configuration

```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile (Frontend)
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: dml_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: dml_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dml_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://dml_user:${DB_PASSWORD}@postgres:5432/dml_db
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

### Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dml_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SSO (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## Development Workflow

### Local Setup

**Backend Setup:**
```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python -m alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Database Migrations

Using Alembic for schema versioning:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add mentorship_logs table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

**Backend Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

**Frontend Tests:**
```bash
# Run Jest tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

### Code Quality

```bash
# Backend linting
flake8 app/
black app/
isort app/

# Frontend linting
npm run lint
npm run format
```

---

## Implementation Checklist

### Phase 1: Foundation (Weeks 1-2)
- [ ] Setup project repositories (Next.js, FastAPI)
- [ ] Configure Docker and Docker Compose
- [ ] Setup PostgreSQL database
- [ ] Implement authentication system (JWT)
- [ ] Create core database models and migrations
- [ ] Setup CI/CD pipeline

### Phase 2: Core Features (Weeks 3-4)
- [ ] Implement mentorship log CRUD operations
- [ ] Build planning section form
- [ ] Build reporting section form
- [ ] Implement facility management
- [ ] Create user management system
- [ ] Add role-based access control

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] Implement follow-up management
- [ ] Add file upload functionality
- [ ] Build dashboard and analytics
- [ ] Implement report generation (PDF/Excel)
- [ ] Add search and filtering
- [ ] Setup notification system

### Phase 4: Polish & Testing (Weeks 7-8)
- [ ] Comprehensive testing (unit, integration, E2E)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation completion
- [ ] User acceptance testing
- [ ] Deployment preparation

---

## Conclusion

This development guide provides a solid foundation for building the Digital Mentorship Log system. The architecture is designed for scalability, maintainability, and rapid development. By following the component-based approach and leveraging modern frameworks (Next.js and FastAPI), the team can deliver a robust system within the November 2025 timeline.

Key success factors include clear separation of concerns, comprehensive testing, and adherence to the established patterns and conventions outlined in this guide.

---

## References

[1] Next.js Documentation - https://nextjs.org/docs
[2] FastAPI Documentation - https://fastapi.tiangolo.com/
[3] SQLAlchemy ORM Tutorial - https://docs.sqlalchemy.org/
[4] PostgreSQL Official Documentation - https://www.postgresql.org/docs/
[5] JWT Authentication Best Practices - https://tools.ietf.org/html/rfc7519
[6] React Hooks Documentation - https://react.dev/reference/react/hooks
[7] Pydantic Data Validation - https://docs.pydantic.dev/
[8] Docker Best Practices - https://docs.docker.com/develop/dev-best-practices/

