# Digital Mentorship Log API Documentation

Base URL: `http://localhost:8000`

Interactive Documentation: `http://localhost:8000/docs`

## Overview

The Digital Mentorship Log API provides endpoints for managing mentorship activities, tracking action items, and generating operational reports. The API follows the ACE2 PDF form structure for mentorship documentation.

## Authentication

All endpoints (except registration) require JWT authentication.

**Header Format:**
```
Authorization: Bearer <token>
```

---

## 1. Authentication Endpoints

### Register a New User
```http
POST /api/auth/register
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "designation": "Senior Mentor",
  "region_state": "Kano",
  "role": "mentor"
}
```

### Login
```http
POST /api/auth/login
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
```

### Logout
```http
POST /api/auth/logout
```

---

## 2. User Management (Admin/Supervisor Only)

### List Users
```http
GET /api/users?role=mentor&is_active=true&search=john&skip=0&limit=100
```

### Get User by ID
```http
GET /api/users/{user_id}
```

### Create User (Admin Only)
```http
POST /api/users
```

### Update User
```http
PUT /api/users/{user_id}
```

### Activate/Deactivate User (Admin Only)
```http
PUT /api/users/{user_id}/activate
PUT /api/users/{user_id}/deactivate
```

### Delete User (Admin Only)
```http
DELETE /api/users/{user_id}
```

---

## 3. Facility Management

### List Facilities
```http
GET /api/facilities?state=Kano&lga=Gwale&search=General&skip=0&limit=100
```

### Get Facility by ID
```http
GET /api/facilities/{facility_id}
```

### Create Facility (Admin Only)
```http
POST /api/facilities
```

**Body:**
```json
{
  "name": "Kano General Hospital",
  "code": "KGH001",
  "location": "123 Hospital Road",
  "state": "Kano",
  "lga": "Kano Municipal",
  "facility_type": "Hospital",
  "contact_person": "Dr. Ahmed",
  "contact_email": "ahmed@kgh.ng",
  "contact_phone": "+234123456789"
}
```

### Update Facility (Admin Only)
```http
PUT /api/facilities/{facility_id}
```

### Delete Facility (Admin Only)
```http
DELETE /api/facilities/{facility_id}
```

---

## 4. Mentorship Logs (ACE2 Form)

### List Mentorship Logs
```http
GET /api/mentorship-logs?status=draft&facility_id={id}&mentor_id={id}&start_date=2025-01-01&end_date=2025-12-31
```

### Get Mentorship Log by ID
```http
GET /api/mentorship-logs/{log_id}
```

### Create Mentorship Log
```http
POST /api/mentorship-logs
```

**Body:**
```json
{
  "facility_id": "uuid",
  "visit_date": "2025-10-30",
  "interaction_type": "On-site",
  "duration_hours": 2,
  "duration_minutes": 30,
  "mentees_present": [
    {"name": "Dr. Sarah", "cadre": "Medical Officer"}
  ],
  "activities_conducted": ["Clinical Review", "Training"],
  "activities_other_specify": "Custom activity description",
  "thematic_areas": ["Quality Improvement", "Patient Safety"],
  "thematic_areas_other_specify": "Custom theme",
  "strengths_observed": "Excellent patient care protocols",
  "gaps_identified": "Limited documentation practices",
  "root_causes": "Lack of training on documentation",
  "challenges_encountered": "Time constraints during visit",
  "solutions_proposed": "Schedule dedicated training sessions",
  "support_needed": "Training materials and facilitator",
  "success_stories": "Improved patient outcomes noted",
  "attachment_types": ["Photos", "Tools/Templates"],
  "skills_transfers": [
    {
      "skill_knowledge_transferred": "Patient triage protocols",
      "recipient_name": "Nurse Jane",
      "recipient_cadre": "Nurse",
      "method": "Hands-on demonstration",
      "competency_level": "Intermediate",
      "followup_needed": true
    }
  ],
  "follow_ups": [
    {
      "action_item": "Conduct follow-up training",
      "responsible_person": "Dr. Ahmed",
      "target_date": "2025-11-15",
      "priority": "High",
      "resources_needed": "Training materials"
    }
  ]
}
```

### Update Mentorship Log
```http
PUT /api/mentorship-logs/{log_id}
```

### Submit Log for Approval
```http
PUT /api/mentorship-logs/{log_id}/submit
```

### Approve Log (Supervisor/Admin Only)
```http
PUT /api/mentorship-logs/{log_id}/approve
```

### Return Log to Draft (Supervisor/Admin Only)
```http
PUT /api/mentorship-logs/{log_id}/return-to-draft
```

### Delete Mentorship Log
```http
DELETE /api/mentorship-logs/{log_id}
```

---

## 5. Follow-Up Management

### List Follow-Ups
```http
GET /api/follow-ups?status=pending&mentorship_log_id={id}&assigned_to={user_id}&priority=High
```

### Get Follow-Up by ID
```http
GET /api/follow-ups/{follow_up_id}
```

### Create Follow-Up
```http
POST /api/follow-ups
```

**Body:**
```json
{
  "mentorship_log_id": "uuid",
  "action_item": "Schedule follow-up training",
  "responsible_person": "Dr. Ahmed",
  "assigned_to": "uuid",
  "target_date": "2025-11-15",
  "resources_needed": "Training materials",
  "priority": "High",
  "notes": "Coordinate with facility manager"
}
```

### Update Follow-Up
```http
PUT /api/follow-ups/{follow_up_id}
```

### Mark as In Progress
```http
PUT /api/follow-ups/{follow_up_id}/in-progress
```

### Mark as Completed
```http
PUT /api/follow-ups/{follow_up_id}/complete
```

### Delete Follow-Up
```http
DELETE /api/follow-ups/{follow_up_id}
```

---

## 6. File Attachments

### Upload Files to Mentorship Log
```http
POST /api/attachments/upload/{mentorship_log_id}
Content-Type: multipart/form-data
```

**Form Data:**
```
files: [file1, file2, ...]
```

**Allowed File Types:**
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`
- Documents: `.pdf`, `.doc`, `.docx`
- Spreadsheets: `.xls`, `.xlsx`
- Presentations: `.ppt`, `.pptx`
- Archives: `.zip`, `.rar`

**Max File Size:** 10MB per file

### List Attachments for a Log
```http
GET /api/attachments/{mentorship_log_id}
```

### Download Attachment
```http
GET /api/attachments/download/{attachment_id}
```

### Delete Attachment
```http
DELETE /api/attachments/{attachment_id}
```

---

## 7. Reports (Admin/Supervisor Only)

### Summary Report
```http
GET /api/reports/summary
```

**Response:**
```json
{
  "total_logs": 150,
  "logs_by_status": {
    "draft": 10,
    "submitted": 40,
    "approved": 100
  },
  "total_facilities": 50,
  "total_mentors": 15,
  "total_follow_ups": 75,
  "follow_ups_by_status": {
    "pending": 30,
    "in_progress": 20,
    "completed": 25
  }
}
```

### Mentorship Logs Report
```http
GET /api/reports/mentorship-logs?start_date=2025-01-01&end_date=2025-12-31&mentor_id={id}&facility_id={id}&status=approved
```

**Response:**
```json
{
  "total_count": 100,
  "logs_by_mentor": [
    {"mentor_id": "uuid", "mentor_name": "John Doe", "count": 15}
  ],
  "logs_by_facility": [
    {"facility_id": "uuid", "facility_name": "Kano General Hospital", "count": 20}
  ],
  "logs_by_state": [
    {"state": "Kano", "count": 50}
  ]
}
```

### Follow-Ups Report
```http
GET /api/reports/follow-ups?status=pending&priority=High
```

**Response:**
```json
{
  "total_count": 75,
  "pending_count": 30,
  "overdue_count": 5,
  "by_status": {
    "pending": 30,
    "in_progress": 20,
    "completed": 25
  }
}
```

### Facility Coverage Report
```http
GET /api/reports/facility-coverage?state=Kano
```

**Response:**
```json
{
  "total_facilities": 50,
  "visited_facilities": 45,
  "unvisited_facilities": 5,
  "facilities": [
    {
      "facility_id": "uuid",
      "facility_name": "Kano General Hospital",
      "facility_code": "KGH001",
      "state": "Kano",
      "lga": "Kano Municipal",
      "visit_count": 15,
      "last_visit_date": "2025-10-25"
    }
  ]
}
```

---

## User Roles & Permissions

### Admin
- Full access to all endpoints
- Can create/update/delete users and facilities
- Can approve mentorship logs
- Can access all reports

### Supervisor
- Can view all users, facilities, and logs
- Can approve mentorship logs
- Can access all reports
- Cannot create/delete users or facilities

### Mentor
- Can create and manage own mentorship logs
- Can create follow-ups for own logs
- Can view facilities
- Cannot access reports or manage other users' data

---

## Status Workflows

### Mentorship Log Status
```
draft → submitted → approved
       ↓             ↓
   return-to-draft ←┘
```

### Follow-Up Status
```
pending → in_progress → completed
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding in production.

## Pagination

Most list endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 500)

---

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

---

## Development

Start development server:
```bash
uvicorn app.main:app --reload
```

Run database migrations:
```bash
alembic upgrade head
```

---

For detailed interactive documentation, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
