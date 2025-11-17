# Digital Mentorship Log - API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000` (Development)
**API Prefix:** `/api`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Data Models](#data-models)
5. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Users](#user-endpoints)
   - [Facilities](#facility-endpoints)
   - [Mentorship Logs](#mentorship-log-endpoints)
   - [Follow-Ups](#follow-up-endpoints)
   - [Reports & Analytics](#reports--analytics-endpoints)
   - [File Attachments](#file-attachment-endpoints)

---

## Overview

The Digital Mentorship Log API is a RESTful API built with FastAPI that provides endpoints for managing mentorship activities, facilities, users, and follow-up actions. All responses are in JSON format.

### Key Features
- JWT-based authentication
- Role-based access control (Mentor, Supervisor, Admin)
- Comprehensive data validation
- File upload support
- Pagination for list endpoints
- Audit logging

### Base Response Format

**Success Response:**
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  ...
}
```

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive an access token that must be included in subsequent requests.

### Authentication Flow

1. **Login** → Receive JWT token
2. **Include token** in all authenticated requests via `Authorization` header
3. **Token expires** after 24 hours (configurable)
4. **Refresh token** if needed

### Including the Token

All authenticated endpoints require the JWT token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

### User Roles

- **Mentor**: Can create and manage their own mentorship logs
- **Supervisor**: Can view and approve logs from mentors they supervise
- **Admin**: Full system access, can manage users and facilities

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |

### Error Response Format

```json
{
  "detail": "Descriptive error message"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Data Models

### User

```typescript
{
  id: string (UUID)
  email: string
  name: string
  designation?: string
  region_state?: string
  role: "mentor" | "supervisor" | "admin"
  is_active: boolean
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
}
```

### Facility

```typescript
{
  id: string (UUID)
  name: string
  code?: string
  location?: string
  state?: string
  facility_type?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
}
```

### Mentorship Log

```typescript
{
  id: string (UUID)
  facility_id: string (UUID)
  mentor_id: string (UUID)
  visit_date: string (YYYY-MM-DD)
  status: "draft" | "submitted" | "approved" | "completed"

  // Planning Section
  performance_summary?: string
  identified_gaps?: string
  trends_summary?: string
  previous_followup?: string
  persistent_challenges?: string
  progress_made?: string
  resources_needed?: string
  facility_requests?: string
  logistics_notes?: string

  // Reporting Section
  visit_outcomes?: string
  lessons_learned?: string

  // Metadata
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
  submitted_at?: string (ISO 8601)
  approved_at?: string (ISO 8601)
  approved_by?: string (UUID)

  // Nested Relations
  objectives: VisitObjective[]
  follow_ups: FollowUp[]
  attachments: Attachment[]
}
```

### Visit Objective

```typescript
{
  id: string (UUID)
  mentorship_log_id: string (UUID)
  objective_text: string
  sequence?: number
  created_at: string (ISO 8601)
}
```

### Follow-Up

```typescript
{
  id: string (UUID)
  mentorship_log_id: string (UUID)
  action_item: string
  status: "pending" | "in_progress" | "completed"
  assigned_to?: string (UUID)
  due_date?: string (YYYY-MM-DD)
  notes?: string
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
  completed_at?: string (ISO 8601)
}
```

### Attachment

```typescript
{
  id: string (UUID)
  mentorship_log_id: string (UUID)
  file_name: string
  file_path: string
  file_size?: number (bytes)
  file_type?: string (MIME type)
  uploaded_by?: string (UUID)
  created_at: string (ISO 8601)
}
```

---

## API Endpoints

---

## Authentication Endpoints

### 1. Login

Authenticate a user and receive a JWT token.

**Endpoint:** `POST /api/auth/login`

**Authentication:** None (public)

**Request Body:**
```json
{
  "email": "mentor@example.com",
  "password": "securePassword123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Invalid email format

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"mentor@example.com","password":"securePassword123"}'
```

---

### 2. Get Current User

Retrieve the currently authenticated user's information.

**Endpoint:** `GET /api/auth/me`

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "mentor@example.com",
  "name": "John Doe",
  "designation": "Senior Mentor",
  "region_state": "Lagos State",
  "role": "mentor",
  "is_active": true,
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-15T14:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token

---

### 3. Logout

Logout the current user (client-side token removal).

**Endpoint:** `POST /api/auth/logout`

**Authentication:** Required

**Success Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 4. Refresh Token

Refresh an expired JWT token.

**Endpoint:** `POST /api/auth/refresh-token`

**Authentication:** Required

**Request Body:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

**Success Response (200):**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer"
}
```

---

## User Endpoints

### 1. List Users

Retrieve a paginated list of users.

**Endpoint:** `GET /api/users`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Number of records to return (default: 10, max: 100)
- `role` (string, optional): Filter by role ("mentor", "supervisor", "admin")
- `is_active` (boolean, optional): Filter by active status

**Success Response (200):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "mentor@example.com",
      "name": "John Doe",
      "designation": "Senior Mentor",
      "region_state": "Lagos State",
      "role": "mentor",
      "is_active": true,
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-15T14:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 10,
  "pages": 5
}
```

**Error Responses:**
- `403 Forbidden` - Insufficient permissions

---

### 2. Create User

Create a new user account.

**Endpoint:** `POST /api/users`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "email": "newmentor@example.com",
  "name": "Jane Smith",
  "designation": "Mentor",
  "region_state": "Abuja",
  "role": "mentor",
  "password": "securePassword123"
}
```

**Success Response (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "email": "newmentor@example.com",
  "name": "Jane Smith",
  "designation": "Mentor",
  "region_state": "Abuja",
  "role": "mentor",
  "is_active": true,
  "created_at": "2025-10-29T10:00:00Z",
  "updated_at": "2025-10-29T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Email already exists
- `403 Forbidden` - Insufficient permissions
- `422 Unprocessable Entity` - Validation errors

---

### 3. Get User by ID

Retrieve a specific user's information.

**Endpoint:** `GET /api/users/{user_id}`

**Authentication:** Required

**Path Parameters:**
- `user_id` (UUID): The user's unique identifier

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "mentor@example.com",
  "name": "John Doe",
  "designation": "Senior Mentor",
  "region_state": "Lagos State",
  "role": "mentor",
  "is_active": true,
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-15T14:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - User doesn't exist

---

### 4. Update User

Update a user's information.

**Endpoint:** `PUT /api/users/{user_id}`

**Authentication:** Required (Own profile or Admin)

**Path Parameters:**
- `user_id` (UUID): The user's unique identifier

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "designation": "Lead Mentor",
  "region_state": "Lagos State"
}
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "mentor@example.com",
  "name": "John Doe Updated",
  "designation": "Lead Mentor",
  "region_state": "Lagos State",
  "role": "mentor",
  "is_active": true,
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-29T11:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - Cannot update other users
- `404 Not Found` - User doesn't exist

---

### 5. Delete User

Delete a user account.

**Endpoint:** `DELETE /api/users/{user_id}`

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (UUID): The user's unique identifier

**Success Response (200):**
```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - User doesn't exist

---

### 6. Assign Facilities to User

Assign facilities to a mentor.

**Endpoint:** `POST /api/users/{user_id}/assign-facilities`

**Authentication:** Required (Admin or Supervisor)

**Path Parameters:**
- `user_id` (UUID): The mentor's unique identifier

**Request Body:**
```json
{
  "facility_ids": [
    "770e8400-e29b-41d4-a716-446655440000",
    "880e8400-e29b-41d4-a716-446655440000"
  ]
}
```

**Success Response (200):**
```json
{
  "message": "Facilities assigned successfully",
  "assigned_count": 2
}
```

---

### 7. Get User's Assigned Facilities

Retrieve facilities assigned to a user.

**Endpoint:** `GET /api/users/{user_id}/assigned-facilities`

**Authentication:** Required

**Path Parameters:**
- `user_id` (UUID): The user's unique identifier

**Success Response (200):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "name": "Central Health Clinic",
    "code": "CHC-001",
    "location": "Downtown Lagos",
    "state": "Lagos State",
    "facility_type": "Primary Care",
    "created_at": "2025-09-01T10:00:00Z",
    "updated_at": "2025-09-01T10:00:00Z"
  }
]
```

---

## Facility Endpoints

### 1. List Facilities

Retrieve a paginated list of facilities.

**Endpoint:** `GET /api/facilities`

**Authentication:** Required

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Number of records to return (default: 10, max: 100)
- `state` (string, optional): Filter by state
- `facility_type` (string, optional): Filter by facility type

**Success Response (200):**
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "name": "Central Health Clinic",
      "code": "CHC-001",
      "location": "Downtown Lagos",
      "state": "Lagos State",
      "facility_type": "Primary Care",
      "contact_person": "Dr. Ada Johnson",
      "contact_email": "ada@chc.com",
      "contact_phone": "+234-800-1234",
      "created_at": "2025-09-01T10:00:00Z",
      "updated_at": "2025-09-01T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 10,
  "pages": 3
}
```

---

### 2. Create Facility

Create a new facility.

**Endpoint:** `POST /api/facilities`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "New Health Center",
  "code": "NHC-002",
  "location": "Abuja Central",
  "state": "FCT Abuja",
  "facility_type": "Secondary Care",
  "contact_person": "Dr. Chidi Okonkwo",
  "contact_email": "chidi@nhc.com",
  "contact_phone": "+234-800-5678"
}
```

**Success Response (201):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "name": "New Health Center",
  "code": "NHC-002",
  "location": "Abuja Central",
  "state": "FCT Abuja",
  "facility_type": "Secondary Care",
  "contact_person": "Dr. Chidi Okonkwo",
  "contact_email": "chidi@nhc.com",
  "contact_phone": "+234-800-5678",
  "created_at": "2025-10-29T11:00:00Z",
  "updated_at": "2025-10-29T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Facility code already exists
- `403 Forbidden` - Insufficient permissions

---

### 3. Get Facility by ID

Retrieve a specific facility's information.

**Endpoint:** `GET /api/facilities/{facility_id}`

**Authentication:** Required

**Path Parameters:**
- `facility_id` (UUID): The facility's unique identifier

**Success Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "name": "Central Health Clinic",
  "code": "CHC-001",
  "location": "Downtown Lagos",
  "state": "Lagos State",
  "facility_type": "Primary Care",
  "contact_person": "Dr. Ada Johnson",
  "contact_email": "ada@chc.com",
  "contact_phone": "+234-800-1234",
  "created_at": "2025-09-01T10:00:00Z",
  "updated_at": "2025-09-01T10:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Facility doesn't exist

---

### 4. Update Facility

Update a facility's information.

**Endpoint:** `PUT /api/facilities/{facility_id}`

**Authentication:** Required (Admin only)

**Path Parameters:**
- `facility_id` (UUID): The facility's unique identifier

**Request Body:**
```json
{
  "name": "Central Health Clinic - Updated",
  "contact_person": "Dr. Ada Johnson-Smith"
}
```

**Success Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "name": "Central Health Clinic - Updated",
  "code": "CHC-001",
  "location": "Downtown Lagos",
  "state": "Lagos State",
  "facility_type": "Primary Care",
  "contact_person": "Dr. Ada Johnson-Smith",
  "contact_email": "ada@chc.com",
  "contact_phone": "+234-800-1234",
  "created_at": "2025-09-01T10:00:00Z",
  "updated_at": "2025-10-29T12:00:00Z"
}
```

---

### 5. Delete Facility

Delete a facility.

**Endpoint:** `DELETE /api/facilities/{facility_id}`

**Authentication:** Required (Admin only)

**Path Parameters:**
- `facility_id` (UUID): The facility's unique identifier

**Success Response (200):**
```json
{
  "message": "Facility deleted successfully"
}
```

**Error Responses:**
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Facility doesn't exist

---

### 6. Get Facility Performance

Retrieve performance metrics for a facility.

**Endpoint:** `GET /api/facilities/{facility_id}/performance`

**Authentication:** Required

**Path Parameters:**
- `facility_id` (UUID): The facility's unique identifier

**Query Parameters:**
- `start_date` (date, optional): Start date for metrics (YYYY-MM-DD)
- `end_date` (date, optional): End date for metrics (YYYY-MM-DD)

**Success Response (200):**
```json
{
  "facility_id": "770e8400-e29b-41d4-a716-446655440000",
  "facility_name": "Central Health Clinic",
  "total_visits": 15,
  "completed_visits": 12,
  "pending_followups": 8,
  "completed_followups": 20,
  "last_visit_date": "2025-10-20",
  "performance_trend": "improving"
}
```

---

## Mentorship Log Endpoints

### 1. List Mentorship Logs

Retrieve a paginated list of mentorship logs with optional filters.

**Endpoint:** `GET /api/mentorship-logs`

**Authentication:** Required

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Number of records to return (default: 10, max: 100)
- `facility_id` (UUID, optional): Filter by facility
- `status` (string, optional): Filter by status ("draft", "submitted", "approved", "completed")
- `start_date` (date, optional): Filter by visit date >= start_date
- `end_date` (date, optional): Filter by visit date <= end_date

**Success Response (200):**
```json
{
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "facility_id": "770e8400-e29b-41d4-a716-446655440000",
      "mentor_id": "550e8400-e29b-41d4-a716-446655440000",
      "visit_date": "2025-11-15",
      "status": "draft",
      "performance_summary": "Overall performance is satisfactory...",
      "identified_gaps": "Staffing levels below target...",
      "created_at": "2025-10-28T10:30:00Z",
      "updated_at": "2025-10-28T10:30:00Z",
      "objectives": [],
      "follow_ups": [],
      "attachments": []
    }
  ],
  "total": 40,
  "page": 1,
  "size": 10,
  "pages": 4
}
```

---

### 2. Create Mentorship Log

Create a new mentorship log.

**Endpoint:** `POST /api/mentorship-logs`

**Authentication:** Required (Mentor role)

**Request Body:**
```json
{
  "facility_id": "770e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-20",
  "performance_summary": "The facility has shown improvement in patient care protocols.",
  "identified_gaps": "Need more training materials for new staff.",
  "trends_summary": "Upward trend in service delivery quality.",
  "previous_followup": "Previous action items completed successfully.",
  "persistent_challenges": "Staff turnover remains high.",
  "progress_made": "Implemented new patient tracking system.",
  "resources_needed": "Training manuals, reference guides",
  "facility_requests": "Additional medical equipment",
  "logistics_notes": "Arranged transport for Nov 20th",
  "objectives": [
    "Improve staff training protocols",
    "Strengthen inventory management",
    "Enhance patient documentation"
  ]
}
```

**Success Response (201):**
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440000",
  "facility_id": "770e8400-e29b-41d4-a716-446655440000",
  "mentor_id": "550e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-20",
  "status": "draft",
  "performance_summary": "The facility has shown improvement in patient care protocols.",
  "identified_gaps": "Need more training materials for new staff.",
  "trends_summary": "Upward trend in service delivery quality.",
  "previous_followup": "Previous action items completed successfully.",
  "persistent_challenges": "Staff turnover remains high.",
  "progress_made": "Implemented new patient tracking system.",
  "resources_needed": "Training manuals, reference guides",
  "facility_requests": "Additional medical equipment",
  "logistics_notes": "Arranged transport for Nov 20th",
  "visit_outcomes": null,
  "lessons_learned": null,
  "created_at": "2025-10-29T12:00:00Z",
  "updated_at": "2025-10-29T12:00:00Z",
  "submitted_at": null,
  "approved_at": null,
  "approved_by": null,
  "objectives": [
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440000",
      "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "objective_text": "Improve staff training protocols",
      "sequence": 1,
      "created_at": "2025-10-29T12:00:00Z"
    },
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440000",
      "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "objective_text": "Strengthen inventory management",
      "sequence": 2,
      "created_at": "2025-10-29T12:00:00Z"
    },
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440000",
      "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "objective_text": "Enhance patient documentation",
      "sequence": 3,
      "created_at": "2025-10-29T12:00:00Z"
    }
  ],
  "follow_ups": [],
  "attachments": []
}
```

**Error Responses:**
- `400 Bad Request` - Invalid facility_id or mentor not assigned to facility
- `422 Unprocessable Entity` - Validation errors

---

### 3. Get Mentorship Log by ID

Retrieve a specific mentorship log with all related data.

**Endpoint:** `GET /api/mentorship-logs/{log_id}`

**Authentication:** Required

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Success Response (200):**
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440000",
  "facility_id": "770e8400-e29b-41d4-a716-446655440000",
  "mentor_id": "550e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-20",
  "status": "submitted",
  "performance_summary": "The facility has shown improvement...",
  "identified_gaps": "Need more training materials...",
  "created_at": "2025-10-29T12:00:00Z",
  "updated_at": "2025-10-29T14:00:00Z",
  "submitted_at": "2025-10-29T14:00:00Z",
  "objectives": [...],
  "follow_ups": [...],
  "attachments": [...]
}
```

**Error Responses:**
- `403 Forbidden` - Cannot view other mentor's logs (unless supervisor/admin)
- `404 Not Found` - Log doesn't exist

---

### 4. Update Mentorship Log

Update an existing mentorship log.

**Endpoint:** `PUT /api/mentorship-logs/{log_id}`

**Authentication:** Required (Log owner only)

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Request Body:**
```json
{
  "visit_outcomes": "Visit was successful. Staff showed enthusiasm for new protocols.",
  "lessons_learned": "Need to schedule follow-up training sessions.",
  "objectives": [
    "Improve staff training protocols",
    "Strengthen inventory management"
  ]
}
```

**Success Response (200):**
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440000",
  "facility_id": "770e8400-e29b-41d4-a716-446655440000",
  "mentor_id": "550e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-11-20",
  "status": "draft",
  "visit_outcomes": "Visit was successful. Staff showed enthusiasm for new protocols.",
  "lessons_learned": "Need to schedule follow-up training sessions.",
  "updated_at": "2025-10-29T15:00:00Z",
  "objectives": [...],
  "follow_ups": [],
  "attachments": []
}
```

**Error Responses:**
- `403 Forbidden` - Cannot edit other mentor's logs or submitted/approved logs
- `404 Not Found` - Log doesn't exist

---

### 5. Delete Mentorship Log

Delete a mentorship log (soft delete).

**Endpoint:** `DELETE /api/mentorship-logs/{log_id}`

**Authentication:** Required (Log owner or Admin)

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Success Response (200):**
```json
{
  "message": "Mentorship log deleted successfully"
}
```

**Error Responses:**
- `403 Forbidden` - Cannot delete submitted/approved logs or other mentor's logs
- `404 Not Found` - Log doesn't exist

---

### 6. Submit Mentorship Log

Submit a mentorship log for supervisor approval.

**Endpoint:** `POST /api/mentorship-logs/{log_id}/submit`

**Authentication:** Required (Log owner only)

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Success Response (200):**
```json
{
  "message": "Log submitted for approval",
  "log": {
    "id": "bb0e8400-e29b-41d4-a716-446655440000",
    "status": "submitted",
    "submitted_at": "2025-10-29T16:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Log already submitted or missing required fields
- `403 Forbidden` - Not the log owner
- `404 Not Found` - Log doesn't exist

---

### 7. Approve Mentorship Log

Approve a submitted mentorship log.

**Endpoint:** `POST /api/mentorship-logs/{log_id}/approve`

**Authentication:** Required (Supervisor or Admin)

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Request Body (optional):**
```json
{
  "comments": "Approved. Good work on the facility visit."
}
```

**Success Response (200):**
```json
{
  "message": "Log approved successfully",
  "log": {
    "id": "bb0e8400-e29b-41d4-a716-446655440000",
    "status": "approved",
    "approved_at": "2025-10-29T17:00:00Z",
    "approved_by": "660e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Log not in submitted status
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Log doesn't exist

---

### 8. Export Mentorship Log

Export a mentorship log as PDF or Excel.

**Endpoint:** `POST /api/mentorship-logs/{log_id}/export`

**Authentication:** Required

**Path Parameters:**
- `log_id` (UUID): The log's unique identifier

**Query Parameters:**
- `format` (string, required): Export format ("pdf" or "excel")

**Success Response (200):**
- Returns binary file with appropriate Content-Type header

**Error Responses:**
- `404 Not Found` - Log doesn't exist
- `422 Unprocessable Entity` - Invalid format

---

## Follow-Up Endpoints

### 1. List Follow-Ups

Retrieve a list of follow-up items.

**Endpoint:** `GET /api/follow-ups`

**Authentication:** Required

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip
- `limit` (integer, optional): Number of records to return
- `status` (string, optional): Filter by status
- `assigned_to` (UUID, optional): Filter by assigned user

**Success Response (200):**
```json
{
  "items": [
    {
      "id": "ff0e8400-e29b-41d4-a716-446655440000",
      "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "action_item": "Conduct staff training session",
      "status": "pending",
      "assigned_to": "550e8400-e29b-41d4-a716-446655440000",
      "due_date": "2025-11-30",
      "notes": "Focus on patient documentation",
      "created_at": "2025-10-29T12:00:00Z",
      "updated_at": "2025-10-29T12:00:00Z",
      "completed_at": null
    }
  ],
  "total": 15,
  "page": 1,
  "size": 10,
  "pages": 2
}
```

---

### 2. Create Follow-Up

Create a follow-up item for a mentorship log.

**Endpoint:** `POST /api/mentorship-logs/{log_id}/follow-ups`

**Authentication:** Required

**Path Parameters:**
- `log_id` (UUID): The mentorship log's unique identifier

**Request Body:**
```json
{
  "action_item": "Schedule follow-up training on inventory management",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440000",
  "due_date": "2025-12-15",
  "notes": "Coordinate with facility manager"
}
```

**Success Response (201):**
```json
{
  "id": "110e8400-e29b-41d4-a716-446655440000",
  "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
  "action_item": "Schedule follow-up training on inventory management",
  "status": "pending",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440000",
  "due_date": "2025-12-15",
  "notes": "Coordinate with facility manager",
  "created_at": "2025-10-29T18:00:00Z",
  "updated_at": "2025-10-29T18:00:00Z",
  "completed_at": null
}
```

---

### 3. Update Follow-Up

Update a follow-up item.

**Endpoint:** `PUT /api/follow-ups/{followup_id}`

**Authentication:** Required

**Path Parameters:**
- `followup_id` (UUID): The follow-up's unique identifier

**Request Body:**
```json
{
  "status": "in_progress",
  "notes": "Training scheduled for Dec 10th"
}
```

**Success Response (200):**
```json
{
  "id": "110e8400-e29b-41d4-a716-446655440000",
  "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
  "action_item": "Schedule follow-up training on inventory management",
  "status": "in_progress",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440000",
  "due_date": "2025-12-15",
  "notes": "Training scheduled for Dec 10th",
  "created_at": "2025-10-29T18:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z",
  "completed_at": null
}
```

---

### 4. Update Follow-Up Status

Update only the status of a follow-up item.

**Endpoint:** `PUT /api/follow-ups/{followup_id}/status`

**Authentication:** Required

**Path Parameters:**
- `followup_id` (UUID): The follow-up's unique identifier

**Request Body:**
```json
{
  "status": "completed"
}
```

**Success Response (200):**
```json
{
  "id": "110e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "completed_at": "2025-11-02T14:30:00Z"
}
```

---

### 5. Delete Follow-Up

Delete a follow-up item.

**Endpoint:** `DELETE /api/follow-ups/{followup_id}`

**Authentication:** Required

**Path Parameters:**
- `followup_id` (UUID): The follow-up's unique identifier

**Success Response (200):**
```json
{
  "message": "Follow-up deleted successfully"
}
```

---

## Reports & Analytics Endpoints

### 1. Get Dashboard Metrics

Retrieve dashboard metrics for the current user.

**Endpoint:** `GET /api/reports/dashboard`

**Authentication:** Required

**Query Parameters:**
- `start_date` (date, optional): Start date for metrics
- `end_date` (date, optional): End date for metrics

**Success Response (200):**
```json
{
  "total_logs": 45,
  "planned_visits": 12,
  "completed_visits": 33,
  "pending_approvals": 5,
  "overdue_followups": 3,
  "recent_logs": [...],
  "upcoming_visits": [...]
}
```

---

### 2. Get Mentor Summary

Retrieve performance summary for a specific mentor.

**Endpoint:** `GET /api/reports/mentor-summary`

**Authentication:** Required (Supervisor or Admin)

**Query Parameters:**
- `mentor_id` (UUID, optional): Specific mentor (defaults to current user)
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Success Response (200):**
```json
{
  "mentor_id": "550e8400-e29b-41d4-a716-446655440000",
  "mentor_name": "John Doe",
  "total_visits": 25,
  "completed_visits": 20,
  "pending_visits": 5,
  "facilities_covered": 8,
  "followups_created": 40,
  "followups_completed": 35,
  "average_rating": 4.5
}
```

---

### 3. Get Facility Summary

Retrieve performance summary for facilities.

**Endpoint:** `GET /api/reports/facility-summary`

**Authentication:** Required

**Query Parameters:**
- `facility_id` (UUID, optional): Specific facility
- `state` (string, optional): Filter by state
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Success Response (200):**
```json
{
  "facilities": [
    {
      "facility_id": "770e8400-e29b-41d4-a716-446655440000",
      "facility_name": "Central Health Clinic",
      "total_visits": 15,
      "completed_visits": 12,
      "pending_followups": 8,
      "last_visit_date": "2025-10-20"
    }
  ]
}
```

---

### 4. Export Report

Export reports in various formats.

**Endpoint:** `GET /api/reports/export`

**Authentication:** Required

**Query Parameters:**
- `type` (string, required): Report type ("mentor", "facility", "overview")
- `format` (string, required): Export format ("pdf", "excel", "csv")
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Success Response (200):**
- Returns binary file with appropriate Content-Type header

---

### 5. Get Analytics Trends

Retrieve performance trends and analytics.

**Endpoint:** `GET /api/analytics/trends`

**Authentication:** Required

**Query Parameters:**
- `metric` (string, required): Metric to analyze ("visits", "followups", "completion_rate")
- `period` (string, optional): Time period ("week", "month", "quarter", "year")
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Success Response (200):**
```json
{
  "metric": "visits",
  "period": "month",
  "data_points": [
    {
      "date": "2025-10-01",
      "value": 12
    },
    {
      "date": "2025-10-08",
      "value": 15
    },
    {
      "date": "2025-10-15",
      "value": 18
    }
  ],
  "trend": "increasing",
  "percentage_change": 15.5
}
```

---

## File Attachment Endpoints

### 1. Upload Attachment

Upload a file attachment to a mentorship log.

**Endpoint:** `POST /api/attachments/upload`

**Authentication:** Required

**Request:** `multipart/form-data`

**Form Fields:**
- `mentorship_log_id` (UUID): The log's unique identifier
- `file` (file): The file to upload

**Success Response (201):**
```json
{
  "id": "220e8400-e29b-41d4-a716-446655440000",
  "mentorship_log_id": "bb0e8400-e29b-41d4-a716-446655440000",
  "file_name": "facility_photo.jpg",
  "file_path": "/uploads/2025/10/29/facility_photo.jpg",
  "file_size": 2048576,
  "file_type": "image/jpeg",
  "uploaded_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-29T19:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - File too large or invalid type
- `422 Unprocessable Entity` - Missing required fields

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/attachments/upload" \
  -H "Authorization: Bearer <token>" \
  -F "mentorship_log_id=bb0e8400-e29b-41d4-a716-446655440000" \
  -F "file=@/path/to/file.jpg"
```

---

### 2. Download Attachment

Download a file attachment.

**Endpoint:** `GET /api/attachments/{attachment_id}`

**Authentication:** Required

**Path Parameters:**
- `attachment_id` (UUID): The attachment's unique identifier

**Success Response (200):**
- Returns binary file with appropriate Content-Type header
- Content-Disposition header includes original filename

**Error Responses:**
- `403 Forbidden` - Cannot access attachment from other mentor's log
- `404 Not Found` - Attachment doesn't exist

---

### 3. Delete Attachment

Delete a file attachment.

**Endpoint:** `DELETE /api/attachments/{attachment_id}`

**Authentication:** Required

**Path Parameters:**
- `attachment_id` (UUID): The attachment's unique identifier

**Success Response (200):**
```json
{
  "message": "Attachment deleted successfully"
}
```

**Error Responses:**
- `403 Forbidden` - Cannot delete attachment from other mentor's log
- `404 Not Found` - Attachment doesn't exist

---

## Testing the API

### Using cURL

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"mentor@example.com","password":"password123"}'
```

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

**Create Mentorship Log:**
```bash
curl -X POST "http://localhost:8000/api/mentorship-logs" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "facility_id": "770e8400-e29b-41d4-a716-446655440000",
    "visit_date": "2025-11-25",
    "performance_summary": "Facility showing improvement",
    "objectives": ["Train staff", "Update protocols"]
  }'
```

### Using Python (requests)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "mentor@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Get logs
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/mentorship-logs",
    headers=headers
)
logs = response.json()
```

### Using JavaScript (axios)

```javascript
// Login
const loginResponse = await axios.post(
  'http://localhost:8000/api/auth/login',
  {
    email: 'mentor@example.com',
    password: 'password123'
  }
);

const token = loginResponse.data.access_token;

// Get logs
const logsResponse = await axios.get(
  'http://localhost:8000/api/mentorship-logs',
  {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
);
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **General endpoints**: 100 requests per minute per user
- **File upload**: 10 uploads per hour per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1635436800
```

---

## Versioning

The API uses URL versioning. Current version is v1 (implicit in `/api/` prefix).

Future versions will be accessed via `/api/v2/`, `/api/v3/`, etc.

---

## Support & Contact

For API support, please contact the development team or refer to the project documentation.

**Interactive API Docs:** http://localhost:8000/docs (when server is running)
