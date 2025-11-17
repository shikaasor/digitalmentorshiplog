# Supervisor-Mentor Relationship & Specialist System Implementation

## Overview

This document describes the implementation of the supervisor-mentor relationship and specialist system for the Digital Mentorship Log application.

**Implementation Date:** November 13, 2025
**Status:** Backend Complete - Frontend Pending

## Features Implemented

### 1. Supervisor-Mentor Relationship
- **One-to-many relationship:** Each mentor can have one assigned supervisor
- **Hierarchical approval:** Only a mentor's assigned supervisor (or admin) can approve their logs
- **Database field:** `users.supervisor_id` links to the supervising user

### 2. Specialist System
- **Thematic area specializations:** Users can be designated as specialists in specific thematic areas
- **Automatic visibility:** Specialists automatically see logs that match their thematic areas (when submitted/approved)
- **Immediate notifications:** Specialists are notified when logs in their areas are submitted
- **Specialist comments:** Specialists can leave comments on logs in their areas

### 3. Comments System
- **Log comments:** Any user with access to a log can leave comments
- **Specialist identification:** Comments from specialists are flagged automatically
- **Access control:** Comments visible to log owner, supervisor, specialists, and admins

### 4. Notifications
- **Real-time notifications:** Specialists notified immediately when relevant logs are submitted
- **Notification management:** Mark as read, view counts, delete notifications
- **Thematic area tracking:** Each notification tracks which thematic area triggered it

## Database Schema Changes

### New Tables

#### `user_specializations`
```sql
- id (UUID, PK)
- user_id (UUID, FK → users.id)
- thematic_area (VARCHAR(100))
- created_at (TIMESTAMP)
- UNIQUE(user_id, thematic_area)
```

#### `log_comments`
```sql
- id (UUID, PK)
- mentorship_log_id (UUID, FK → mentorship_logs.id)
- user_id (UUID, FK → users.id)
- comment_text (TEXT)
- is_specialist_comment (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### `specialist_notifications`
```sql
- id (UUID, PK)
- mentorship_log_id (UUID, FK → mentorship_logs.id)
- specialist_id (UUID, FK → users.id)
- thematic_area (VARCHAR(100))
- is_read (BOOLEAN, default: false)
- notified_at (TIMESTAMP)
- read_at (TIMESTAMP, nullable)
- UNIQUE(mentorship_log_id, specialist_id, thematic_area)
```

### Modified Tables

#### `users`
Added column:
- `supervisor_id` (UUID, FK → users.id, nullable)

## API Endpoints

### User Management (Updated)

**POST /api/users**
- Added `supervisor_id` field to assign supervisor
- Added `specializations` array to assign thematic areas

**PUT /api/users/{user_id}**
- Can update `supervisor_id`
- Can update `specializations` array

**GET /api/users/{user_id}**
- Returns `supervisor_id` and `specializations` in response

### Mentorship Logs (Updated)

**GET /api/mentorship-logs**
- Updated visibility logic:
  - Mentors: Own logs only
  - Supervisors: Own logs + direct mentees' logs
  - Specialists: Logs in their thematic areas (submitted/approved status only)
  - Admins: All logs

**POST /api/mentorship-logs/{log_id}/submit**
- Now creates notifications for specialists in matching thematic areas
- Notifications sent immediately on submission

**POST /api/mentorship-logs/{log_id}/approve**
- Updated authorization: Only assigned supervisor or admin can approve
- Validates supervisor-mentee relationship before approval

### Comments (New Endpoints)

**GET /api/mentorship-logs/{log_id}/comments**
- List all comments for a log
- Returns user info (name, role) with each comment
- Accessible by: log owner, assigned supervisor, specialists, admin

**POST /api/mentorship-logs/{log_id}/comments**
- Add comment to a log
- Automatically marks as specialist comment if user is a specialist for the log

**PUT /api/mentorship-logs/comments/{comment_id}**
- Update own comment
- Admin can update any comment

**DELETE /api/mentorship-logs/comments/{comment_id}**
- Delete own comment
- Admin can delete any comment

### Notifications (New Endpoints)

**GET /api/notifications/**
- Get notifications for current user
- Query param: `unread_only` (boolean)
- Returns log details (facility name, mentor name, visit date)

**GET /api/notifications/count**
- Get count of unread notifications

**POST /api/notifications/mark-read**
- Mark specific notifications as read
- Body: `{ notification_ids: [UUID, ...] }`

**POST /api/notifications/mark-all-read**
- Mark all notifications as read for current user

**DELETE /api/notifications/{notification_id}**
- Delete a notification

## Authorization Logic

### Helper Functions (app/dependencies.py)

**can_approve_log(log, current_user, db)**
- Returns True if user can approve the log
- Rules:
  - Admins: Can approve any log
  - Supervisors: Only their direct mentees' logs
  - Others: Cannot approve

**can_view_as_specialist(log, user, db)**
- Returns True if user has specialist access to log
- Checks if user has specialization matching log's thematic areas

**get_visible_logs_query(current_user, db)**
- Returns SQLAlchemy query for logs visible to user
- Implements role-based + specialist-based visibility
- Uses PostgreSQL `?|` operator for JSON array overlap

## Thematic Areas

The system uses 9 predefined thematic areas (from `app/constants.py`):

1. General HIV care and treatment
2. Advanced HIV disease (AHD)
3. Pediatric HIV management
4. PMTCT
5. TB/HIV
6. Laboratory services
7. Pharmacy/supply chain
8. Data quality and use
9. Quality improvement
10. Other (with text specification)

## Migration

**File:** `backend/alembic/versions/64353edf8841_add_supervisor_and_specialist_system.py`

**To apply:**
```bash
cd backend
alembic upgrade head
```

**To rollback:**
```bash
alembic downgrade -1
```

## Models Updated

- `User`: Added supervisor relationship and specializations
- `MentorshipLog`: Added comments relationship
- `UserSpecialization`: New model
- `LogComment`: New model
- `SpecialistNotification`: New model

## Schemas Updated

- `UserCreate`: Added `supervisor_id` and `specializations`
- `UserUpdate`: Added `supervisor_id` and `specializations`
- `UserResponse`: Added `supervisor_id` and `specializations`
- `MentorshipLogResponse`: Added `comments` array
- New: `UserSpecializationResponse`
- New: `LogCommentCreate`, `LogCommentUpdate`, `LogCommentResponse`
- New: `SpecialistNotificationResponse`, `MarkNotificationReadRequest`

## Workflow Examples

### Example 1: Creating a Mentor with Supervisor

```bash
POST /api/users
{
  "email": "mentor@example.com",
  "password": "secure123",
  "name": "John Mentor",
  "role": "mentor",
  "supervisor_id": "550e8400-e29b-41d4-a716-446655440000",
  "specializations": []
}
```

### Example 2: Creating a Specialist

```bash
POST /api/users
{
  "email": "specialist@example.com",
  "password": "secure123",
  "name": "Dr. HIV Specialist",
  "role": "supervisor",
  "specializations": [
    "General HIV care and treatment",
    "Advanced HIV disease (AHD)",
    "Pediatric HIV management"
  ]
}
```

### Example 3: Submitting a Log (Triggers Notifications)

```bash
POST /api/mentorship-logs/{log_id}/submit

# System automatically:
# 1. Changes status to "submitted"
# 2. Finds specialists matching thematic areas
# 3. Creates notifications for each specialist
# 4. Specialists see notification in /api/notifications/
```

### Example 4: Specialist Viewing Logs

```bash
GET /api/mentorship-logs

# Returns:
# - Own logs (if specialist is also a mentor)
# - Mentees' logs (if specialist is also a supervisor)
# - ALL logs matching their thematic areas (submitted/approved status)
```

### Example 5: Supervisor Approving Log

```bash
POST /api/mentorship-logs/{log_id}/approve

# Validation:
# 1. Check log status is "submitted"
# 2. Check current user is mentor's assigned supervisor OR admin
# 3. If not assigned supervisor → 403 Forbidden
# 4. If valid → Approve and record approver
```

### Example 6: Specialist Adding Comment

```bash
POST /api/mentorship-logs/{log_id}/comments
{
  "comment_text": "Excellent work on PMTCT protocols. Consider adding..."
}

# System automatically:
# 1. Checks if user has specialist access to log
# 2. Sets is_specialist_comment = true
# 3. Saves comment with user info
```

## Testing Checklist

### Database
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables created with correct schema
- [ ] Test rollback: `alembic downgrade -1`

### User Management
- [ ] Create mentor with supervisor_id
- [ ] Create user with specializations
- [ ] Update user specializations
- [ ] Verify supervisor validation (must be supervisor role)

### Authorization
- [ ] Supervisor can only approve mentee's logs
- [ ] Supervisor cannot approve other mentor's logs
- [ ] Admin can approve any log
- [ ] Specialist can view logs in their areas
- [ ] Specialist cannot view logs outside their areas

### Notifications
- [ ] Submit log → specialists notified
- [ ] Notification includes correct log details
- [ ] Mark as read updates timestamps
- [ ] Unread count accurate
- [ ] No duplicate notifications

### Comments
- [ ] Mentor can comment on own log
- [ ] Supervisor can comment on mentee's log
- [ ] Specialist can comment on logs in their area
- [ ] Comments show correct user info
- [ ] Update/delete own comments only

### Visibility
- [ ] Mentor sees only own logs
- [ ] Supervisor sees own + mentees' logs
- [ ] Specialist sees logs in their thematic areas (submitted/approved)
- [ ] Admin sees all logs

## Known Limitations & Future Enhancements

### Current Limitations
1. No email notifications (only in-app)
2. No notification preferences (all specialists notified)
3. Cannot assign multiple supervisors (strict one-to-many)
4. Specialists see logs only when submitted/approved (not drafts)

### Future Enhancements
1. **Email notifications:** Send emails when specialists are notified
2. **Notification preferences:** Allow users to configure which areas they want alerts for
3. **Supervisor delegation:** Temporary supervisor assignment during absence
4. **Specialist review workflow:** Optional specialist approval before supervisor approval
5. **Comment threading:** Reply to specific comments
6. **Comment mentions:** @mention users in comments
7. **Dashboard widgets:** "Logs awaiting your review" for specialists
8. **Analytics:** Track specialist engagement and response times

## Frontend Integration (Pending)

The following frontend components need to be updated:

### User Forms
- [ ] Add supervisor selector dropdown (filtered to supervisor role users)
- [ ] Add thematic area multi-select checkboxes
- [ ] Update user profile display to show supervisor and specializations

### Mentorship Log List
- [ ] Update filter logic to use new visibility API
- [ ] Add badge/indicator for specialist-visible logs
- [ ] Show comment count badge

### Log Detail Page
- [ ] Add comments section below log details
- [ ] Show existing comments with user info
- [ ] Add comment input form
- [ ] Highlight specialist comments differently

### Notifications
- [ ] Add notification bell icon in navbar
- [ ] Show unread count badge
- [ ] Notification dropdown/panel
- [ ] Click notification → navigate to log
- [ ] Mark as read on click

### Dashboard
- [ ] Add "Logs to Review" section for specialists
- [ ] Show notification summary
- [ ] Add "My Mentees" section for supervisors

## Support & Troubleshooting

### Common Issues

**Issue:** Supervisor cannot approve log
- **Solution:** Verify mentor's `supervisor_id` matches approving supervisor's ID

**Issue:** Specialist not seeing logs
- **Solution:** Check specializations match log's thematic areas exactly (case-sensitive)

**Issue:** No notifications created
- **Solution:** Ensure log has `thematic_areas` array and specialists exist with matching areas

**Issue:** Duplicate notification error
- **Solution:** Expected behavior - unique constraint prevents duplicates

### Debugging Queries

```sql
-- Check user's supervisor
SELECT u.name, s.name as supervisor_name
FROM users u
LEFT JOIN users s ON u.supervisor_id = s.id
WHERE u.id = 'user-uuid';

-- Check user's specializations
SELECT u.name, us.thematic_area
FROM users u
JOIN user_specializations us ON u.id = us.user_id
WHERE u.id = 'user-uuid';

-- Check notifications for user
SELECT n.*, m.visit_date, f.name as facility_name
FROM specialist_notifications n
JOIN mentorship_logs m ON n.mentorship_log_id = m.id
JOIN facilities f ON m.facility_id = f.id
WHERE n.specialist_id = 'user-uuid'
ORDER BY n.notified_at DESC;

-- Check log visibility (who can see a log)
-- 1. Log owner
-- 2. Assigned supervisor (via mentor's supervisor_id)
-- 3. Specialists with matching thematic areas
SELECT
    'owner' as access_type, m.mentor_id as user_id
FROM mentorship_logs m WHERE m.id = 'log-uuid'
UNION
SELECT
    'supervisor' as access_type, u.supervisor_id as user_id
FROM mentorship_logs m
JOIN users u ON m.mentor_id = u.id
WHERE m.id = 'log-uuid' AND u.supervisor_id IS NOT NULL
UNION
SELECT
    'specialist' as access_type, us.user_id
FROM mentorship_logs m
JOIN user_specializations us ON us.thematic_area = ANY(m.thematic_areas::text[])
WHERE m.id = 'log-uuid';
```

## Conclusion

The supervisor-mentor relationship and specialist system has been successfully implemented on the backend. The system provides:

✅ Hierarchical approval workflow
✅ Specialist visibility based on thematic areas
✅ Real-time notifications for specialists
✅ Comment system for collaboration
✅ Proper authorization and access control

Next steps: Frontend implementation to expose these features to users.
