from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from enum import Enum


# Enums
class UserRole(str, Enum):
    mentor = "mentor"
    supervisor = "supervisor"
    admin = "admin"


class LogStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    completed = "completed"


class FollowUpStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    designation: Optional[str] = None
    region_state: Optional[str] = None
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    region_state: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Facility Schemas
class FacilityBase(BaseModel):
    name: str
    code: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    facility_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    facility_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class FacilityResponse(FacilityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Visit Objective Schemas
class VisitObjectiveBase(BaseModel):
    objective_text: str
    sequence: Optional[int] = None


class VisitObjectiveCreate(VisitObjectiveBase):
    pass


class VisitObjectiveResponse(VisitObjectiveBase):
    id: UUID
    mentorship_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Follow-Up Schemas
class FollowUpBase(BaseModel):
    action_item: str
    assigned_to: Optional[UUID] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpUpdate(BaseModel):
    action_item: Optional[str] = None
    status: Optional[FollowUpStatus] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None


class FollowUpResponse(FollowUpBase):
    id: UUID
    mentorship_log_id: UUID
    status: FollowUpStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Attachment Schemas
class AttachmentResponse(BaseModel):
    id: UUID
    mentorship_log_id: UUID
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    uploaded_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Mentorship Log Schemas
class MentorshipLogBase(BaseModel):
    facility_id: UUID
    visit_date: date
    performance_summary: Optional[str] = None
    identified_gaps: Optional[str] = None
    trends_summary: Optional[str] = None
    previous_followup: Optional[str] = None
    persistent_challenges: Optional[str] = None
    progress_made: Optional[str] = None
    resources_needed: Optional[str] = None
    facility_requests: Optional[str] = None
    logistics_notes: Optional[str] = None
    visit_outcomes: Optional[str] = None
    lessons_learned: Optional[str] = None


class MentorshipLogCreate(MentorshipLogBase):
    objectives: Optional[List[str]] = []


class MentorshipLogUpdate(BaseModel):
    facility_id: Optional[UUID] = None
    visit_date: Optional[date] = None
    performance_summary: Optional[str] = None
    identified_gaps: Optional[str] = None
    trends_summary: Optional[str] = None
    previous_followup: Optional[str] = None
    persistent_challenges: Optional[str] = None
    progress_made: Optional[str] = None
    resources_needed: Optional[str] = None
    facility_requests: Optional[str] = None
    logistics_notes: Optional[str] = None
    visit_outcomes: Optional[str] = None
    lessons_learned: Optional[str] = None
    objectives: Optional[List[str]] = None


class MentorshipLogResponse(MentorshipLogBase):
    id: UUID
    mentor_id: UUID
    status: LogStatus
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None

    # Nested relationships
    objectives: List[VisitObjectiveResponse] = []
    follow_ups: List[FollowUpResponse] = []
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True


# User-Facility Assignment Schemas
class UserFacilityAssignmentCreate(BaseModel):
    user_id: UUID
    facility_ids: List[UUID]


class UserFacilityAssignmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    facility_id: UUID
    assigned_at: datetime

    class Config:
        from_attributes = True
