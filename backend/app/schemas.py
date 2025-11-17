from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Generic, TypeVar
from datetime import date, datetime
from uuid import UUID
from enum import Enum

# Generic type for paginated responses
T = TypeVar('T')


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


# Generic Paginated Response
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int


# User Specialization Schemas
class UserSpecializationBase(BaseModel):
    thematic_area: str


class UserSpecializationCreate(UserSpecializationBase):
    pass


class UserSpecializationResponse(UserSpecializationBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    designation: Optional[str] = None
    region_state: Optional[str] = None
    role: UserRole


class UserCreate(UserBase):
    password: str
    supervisor_id: Optional[UUID] = None
    specializations: Optional[List[str]] = []  # List of thematic areas


class UserUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    region_state: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    supervisor_id: Optional[UUID] = None
    specializations: Optional[List[str]] = None  # List of thematic areas


class UserResponse(UserBase):
    id: UUID
    supervisor_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    specializations: List[UserSpecializationResponse] = []

    class Config:
        from_attributes = True


# Facility Schemas
class FacilityBase(BaseModel):
    name: str
    code: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    lga: Optional[str] = None  # Local Government Area
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
    lga: Optional[str] = None
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


# Skills Transfer Schemas (Section 4 of PDF)
class SkillsTransferBase(BaseModel):
    skill_knowledge_transferred: str
    recipient_name: Optional[str] = None
    recipient_cadre: Optional[str] = None
    method: Optional[str] = None
    competency_level: Optional[str] = None
    followup_needed: bool = False


class SkillsTransferCreate(SkillsTransferBase):
    pass


class SkillsTransferResponse(SkillsTransferBase):
    id: UUID
    mentorship_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Follow-Up Schemas (Section 5: Action Items from PDF)
class FollowUpBase(BaseModel):
    action_item: str  # Action Description
    responsible_person: Optional[str] = None  # Responsible Person (can be text)
    assigned_to: Optional[UUID] = None  # If linking to user table
    target_date: Optional[date] = None  # Target Date
    resources_needed: Optional[str] = None  # Resources Needed
    priority: Optional[str] = None  # Priority (High/Medium/Low)
    notes: Optional[str] = None


class FollowUpNested(FollowUpBase):
    """For creating follow-ups nested within mentorship logs (no mentorship_log_id needed)"""
    pass


class FollowUpCreate(FollowUpBase):
    """For creating standalone follow-ups via API (mentorship_log_id required)"""
    mentorship_log_id: UUID  # Required when creating standalone follow-up via API


class FollowUpUpdate(BaseModel):
    action_item: Optional[str] = None
    status: Optional[FollowUpStatus] = None
    responsible_person: Optional[str] = None
    assigned_to: Optional[UUID] = None
    target_date: Optional[date] = None
    resources_needed: Optional[str] = None
    priority: Optional[str] = None
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


# Mentorship Log Schemas (Matching ACE2 PDF Form)
class MentorshipLogBase(BaseModel):
    facility_id: UUID
    visit_date: date

    # Header fields - Visit Details
    interaction_type: Optional[str] = None  # On-site, Virtual, Phone
    duration_hours: Optional[int] = None
    duration_minutes: Optional[int] = None
    mentees_present: Optional[List[dict]] = []  # [{"name": "...", "cadre": "..."}]

    # Section 1: Activities Conducted (array of selected activities)
    activities_conducted: Optional[List[str]] = []
    activities_other_specify: Optional[str] = None  # Text for "Other (specify)"

    # Section 2: Thematic Areas Covered (array of selected themes)
    thematic_areas: Optional[List[str]] = []
    thematic_areas_other_specify: Optional[str] = None  # Text for "Other (specify)"

    # Section 3: Observations
    strengths_observed: Optional[str] = None
    gaps_identified: Optional[str] = None
    root_causes: Optional[str] = None

    # Section 6: Challenges & Solutions
    challenges_encountered: Optional[str] = None
    solutions_proposed: Optional[str] = None
    support_needed: Optional[str] = None

    # Section 7: Success Stories (Optional)
    success_stories: Optional[str] = None

    # Section 8: Attachments - checkbox types
    attachment_types: Optional[List[str]] = []  # ["Photos", "Tools/Templates", "Before/After", "Reference Materials"]


class MentorshipLogCreate(MentorshipLogBase):
    skills_transfers: Optional[List[SkillsTransferCreate]] = []
    follow_ups: Optional[List[FollowUpNested]] = []  # Use FollowUpNested for nested creation


class MentorshipLogUpdate(BaseModel):
    facility_id: Optional[UUID] = None
    visit_date: Optional[date] = None
    interaction_type: Optional[str] = None
    duration_hours: Optional[int] = None
    duration_minutes: Optional[int] = None
    mentees_present: Optional[List[dict]] = None
    activities_conducted: Optional[List[str]] = None
    activities_other_specify: Optional[str] = None
    thematic_areas: Optional[List[str]] = None
    thematic_areas_other_specify: Optional[str] = None
    strengths_observed: Optional[str] = None
    gaps_identified: Optional[str] = None
    root_causes: Optional[str] = None
    challenges_encountered: Optional[str] = None
    solutions_proposed: Optional[str] = None
    support_needed: Optional[str] = None
    success_stories: Optional[str] = None
    attachment_types: Optional[List[str]] = None
    skills_transfers: Optional[List[SkillsTransferCreate]] = None
    follow_ups: Optional[List[FollowUpNested]] = None  # Use FollowUpNested for nested update


class MentorshipLogResponse(MentorshipLogBase):
    id: UUID
    mentor_id: UUID
    status: LogStatus
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Nested relationships (Section 4, 5, 8)
    skills_transfers: List[SkillsTransferResponse] = []
    follow_ups: List[FollowUpResponse] = []
    attachments: List[AttachmentResponse] = []
    comments: List["LogCommentResponse"] = []

    # Related objects (loaded via joinedload)
    facility: Optional[FacilityResponse] = None
    mentor: Optional[UserResponse] = None
    approver: Optional[UserResponse] = None

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


# Log Comment Schemas
class LogCommentCreate(BaseModel):
    comment_text: str
    is_specialist_comment: bool = False


class LogCommentUpdate(BaseModel):
    comment_text: str


class LogCommentResponse(BaseModel):
    id: UUID
    mentorship_log_id: UUID
    user_id: UUID
    user_name: str  # Computed from relationship
    user_role: UserRole  # Computed from relationship
    comment_text: str
    is_specialist_comment: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Specialist Notification Schemas
class SpecialistNotificationResponse(BaseModel):
    id: UUID
    mentorship_log_id: UUID
    specialist_id: UUID
    thematic_area: str
    is_read: bool
    notified_at: datetime
    read_at: Optional[datetime] = None

    # Include log details for frontend display
    log_facility_name: Optional[str] = None
    log_mentor_name: Optional[str] = None
    log_visit_date: Optional[date] = None

    class Config:
        from_attributes = True


class MarkNotificationReadRequest(BaseModel):
    notification_ids: List[UUID]


# Rebuild models to resolve forward references
MentorshipLogResponse.model_rebuild()
