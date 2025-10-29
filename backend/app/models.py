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
    state = Column(String(100))
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

    # Planning section fields
    performance_summary = Column(Text)
    identified_gaps = Column(Text)
    trends_summary = Column(Text)
    previous_followup = Column(Text)
    persistent_challenges = Column(Text)
    progress_made = Column(Text)
    resources_needed = Column(Text)
    facility_requests = Column(Text)
    logistics_notes = Column(Text)

    # Reporting section fields
    visit_outcomes = Column(Text)
    lessons_learned = Column(Text)

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
    objectives = relationship("VisitObjective", back_populates="mentorship_log", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="mentorship_log", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="mentorship_log", cascade="all, delete-orphan")


class VisitObjective(Base):
    __tablename__ = "visit_objectives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentorship_log_id = Column(UUID(as_uuid=True), ForeignKey("mentorship_logs.id"), nullable=False, index=True)
    objective_text = Column(Text, nullable=False)
    sequence = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mentorship_log = relationship("MentorshipLog", back_populates="objectives")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentorship_log_id = Column(UUID(as_uuid=True), ForeignKey("mentorship_logs.id"), nullable=False, index=True)
    action_item = Column(Text, nullable=False)
    status = Column(Enum(FollowUpStatus), nullable=False, default=FollowUpStatus.pending, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    due_date = Column(Date)
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
