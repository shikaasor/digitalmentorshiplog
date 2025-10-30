from sqlalchemy import Boolean, Column, String, Text, Date, DateTime, ForeignKey, Integer, Enum, BigInteger, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


# Enums
class UserRole(str, enum.Enum):
    mentor = "mentor"
    supervisor = "supervisor"
    admin = "admin"


class LogStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    completed = "completed"


class FollowUpStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    designation = Column(String(100))
    region_state = Column(String(100))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.mentor)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    mentorship_logs = relationship("MentorshipLog", back_populates="mentor", foreign_keys="MentorshipLog.mentor_id")
    approved_logs = relationship("MentorshipLog", back_populates="approver", foreign_keys="MentorshipLog.approved_by")
    facility_assignments = relationship("UserFacilityAssignment", back_populates="user")
    follow_ups = relationship("FollowUp", back_populates="assigned_user")


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True)
    location = Column(String(255))
    state = Column(String(100), index=True)  # For filtering by state
    lga = Column(String(100), index=True)  # Local Government Area for filtering
    facility_type = Column(String(100))
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    mentorship_logs = relationship("MentorshipLog", back_populates="facility")
    user_assignments = relationship("UserFacilityAssignment", back_populates="facility")


class MentorshipLog(Base):
    __tablename__ = "mentorship_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"), nullable=False, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    visit_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(LogStatus), nullable=False, default=LogStatus.draft, index=True)

    # Header fields - Visit Details
    interaction_type = Column(String(50))  # On-site, Virtual, Phone
    duration_hours = Column(Integer)
    duration_minutes = Column(Integer)
    mentees_present = Column(JSON)  # Array of {name: str, cadre: str}

    # Section 1: Activities Conducted (stored as JSON array of selected activities)
    activities_conducted = Column(JSON)  # Array of activity names
    activities_other_specify = Column(Text)  # Text for "Other (specify)"

    # Section 2: Thematic Areas Covered (stored as JSON array of selected themes)
    thematic_areas = Column(JSON)  # Array of thematic area names
    thematic_areas_other_specify = Column(Text)  # Text for "Other (specify)"

    # Section 3: Observations
    strengths_observed = Column(Text)
    gaps_identified = Column(Text)
    root_causes = Column(Text)

    # Section 4: Skills Transfer - separate table (SkillsTransfer)

    # Section 5: Action Items - separate table (FollowUp) with enhanced fields

    # Section 6: Challenges & Solutions
    challenges_encountered = Column(Text)
    solutions_proposed = Column(Text)
    support_needed = Column(Text)

    # Section 7: Success Stories (Optional)
    success_stories = Column(Text)

    # Section 8: Attachments - checkboxes for attachment types
    attachment_types = Column(JSON)  # Array: ["Photos", "Tools/Templates", "Before/After", "Reference Materials"]

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    facility = relationship("Facility", back_populates="mentorship_logs")
    mentor = relationship("User", back_populates="mentorship_logs", foreign_keys=[mentor_id])
    approver = relationship("User", back_populates="approved_logs", foreign_keys=[approved_by])
    skills_transfers = relationship("SkillsTransfer", back_populates="mentorship_log", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="mentorship_log", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="mentorship_log", cascade="all, delete-orphan")


class SkillsTransfer(Base):
    """Section 4: Skills Transfer table from PDF"""
    __tablename__ = "skills_transfers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentorship_log_id = Column(UUID(as_uuid=True), ForeignKey("mentorship_logs.id"), nullable=False, index=True)
    skill_knowledge_transferred = Column(Text, nullable=False)
    recipient_name = Column(String(255))
    recipient_cadre = Column(String(100))
    method = Column(String(255))
    competency_level = Column(String(100))
    followup_needed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mentorship_log = relationship("MentorshipLog", back_populates="skills_transfers")


class FollowUp(Base):
    """Section 5: Action Items table from PDF"""
    __tablename__ = "follow_ups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentorship_log_id = Column(UUID(as_uuid=True), ForeignKey("mentorship_logs.id"), nullable=False, index=True)
    action_item = Column(Text, nullable=False)  # Action Description
    responsible_person = Column(String(255))  # Can be text or link to user
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # If linking to user table
    target_date = Column(Date)  # Target Date from PDF
    resources_needed = Column(Text)  # Resources Needed
    priority = Column(String(50))  # Priority (High/Medium/Low)
    status = Column(Enum(FollowUpStatus), nullable=False, default=FollowUpStatus.pending, index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    mentorship_log = relationship("MentorshipLog", back_populates="follow_ups")
    assigned_user = relationship("User", back_populates="follow_ups")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentorship_log_id = Column(UUID(as_uuid=True), ForeignKey("mentorship_logs.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mentorship_log = relationship("MentorshipLog", back_populates="attachments")


class UserFacilityAssignment(Base):
    __tablename__ = "user_facility_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="facility_assignments")
    facility = relationship("Facility", back_populates="user_assignments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    entity_type = Column(String(100))
    entity_id = Column(UUID(as_uuid=True))
    action = Column(String(50))
    changes = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
