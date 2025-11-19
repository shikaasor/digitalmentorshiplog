"""
Mentorship Log Endpoints

Core endpoints for managing mentorship logs - the main functionality of the system.
Mentors log their activities, which go through a workflow: draft → submitted → approved.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models import (
    MentorshipLog, SkillsTransfer, FollowUp, User, UserRole, LogStatus,
    UserSpecialization, SpecialistNotification, LogComment, Notification, NotificationType
)
from app.schemas import (
    MentorshipLogCreate, MentorshipLogUpdate, MentorshipLogResponse,
    PaginatedResponse
)
from app.dependencies import (
    get_current_user, require_role, get_visible_logs_query, can_approve_log,
    can_view_as_specialist
)


router = APIRouter(prefix="/api/mentorship-logs", tags=["mentorship-logs"])


@router.get("", response_model=PaginatedResponse[MentorshipLogResponse])
def list_mentorship_logs(
    facility_id: Optional[UUID] = Query(None, description="Filter by facility"),
    mentor_id: Optional[UUID] = Query(None, description="Filter by mentor"),
    status: Optional[LogStatus] = Query(None, description="Filter by status (draft, submitted, approved, completed)"),
    visit_date_from: Optional[date] = Query(None, description="Filter by visit date from (inclusive)"),
    visit_date_to: Optional[date] = Query(None, description="Filter by visit date to (inclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List mentorship logs with optional filtering.

    Filters:
    - **facility_id**: Filter by facility
    - **mentor_id**: Filter by mentor
    - **status**: Filter by log status
    - **visit_date_from/to**: Filter by visit date range

    Permissions:
    - Mentors: Own logs only
    - Supervisors: Own logs + mentees' logs
    - Specialists: Logs in their thematic areas (submitted/approved only)
    - Admins: All logs
    """
    from sqlalchemy.orm import joinedload

    # Start with visible logs query based on user role and access
    query = get_visible_logs_query(current_user, db)

    # Eager load relationships for better performance
    query = query.options(
        joinedload(MentorshipLog.facility),
        joinedload(MentorshipLog.mentor),
        joinedload(MentorshipLog.approver),
        joinedload(MentorshipLog.skills_transfers),
        joinedload(MentorshipLog.follow_ups),
        joinedload(MentorshipLog.attachments),
        joinedload(MentorshipLog.comments).joinedload(LogComment.user)
    )

    # Apply additional filter by mentor_id if provided (for admins/supervisors)
    if mentor_id and current_user.role in [UserRole.admin, UserRole.supervisor]:
        query = query.filter(MentorshipLog.mentor_id == mentor_id)

    # Apply other filters
    if facility_id:
        query = query.filter(MentorshipLog.facility_id == facility_id)

    if status:
        query = query.filter(MentorshipLog.status == status)

    if visit_date_from:
        query = query.filter(MentorshipLog.visit_date >= visit_date_from)

    if visit_date_to:
        query = query.filter(MentorshipLog.visit_date <= visit_date_to)

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering (most recent first)
    logs = (
        query
        .order_by(MentorshipLog.visit_date.desc(), MentorshipLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=logs,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{log_id}", response_model=MentorshipLogResponse)
def get_mentorship_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single mentorship log with all nested data.

    Returns the log with:
    - Skills transfers (Section 4)
    - Follow-up actions (Section 5)
    - Attachments (Section 8)

    Permissions:
    - Mentors can only view their own logs
    - Supervisors and admins can view all logs
    - Specialists can view submitted/approved logs matching their thematic areas
    """
    from sqlalchemy.orm import joinedload

    log = db.query(MentorshipLog)\
        .options(
            joinedload(MentorshipLog.facility),
            joinedload(MentorshipLog.mentor),
            joinedload(MentorshipLog.approver),
            joinedload(MentorshipLog.skills_transfers),
            joinedload(MentorshipLog.follow_ups),
            joinedload(MentorshipLog.attachments),
            joinedload(MentorshipLog.comments).joinedload(LogComment.user)
        )\
        .filter(MentorshipLog.id == log_id)\
        .first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions
    # Admins and supervisors can view all logs
    if current_user.role in [UserRole.admin, UserRole.supervisor]:
        return log

    # Mentors can view their own logs
    if current_user.role == UserRole.mentor and log.mentor_id == current_user.id:
        return log

    # Specialists can view submitted/approved logs matching their thematic areas
    if log.status in [LogStatus.submitted, LogStatus.approved]:
        if can_view_as_specialist(log, current_user, db):
            return log

    # If none of the above conditions are met, deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to view this log"
    )


@router.post("", response_model=MentorshipLogResponse, status_code=status.HTTP_201_CREATED)
def create_mentorship_log(
    log_data: MentorshipLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new mentorship log (all users).

    Creates a log in "draft" status with optional nested data:
    - Skills transfers (Section 4)
    - Follow-up actions (Section 5)

    The mentor creating the log is automatically assigned.
    """
    # Extract nested data
    skills_transfers_data = log_data.skills_transfers or []
    follow_ups_data = log_data.follow_ups or []

    # Create main log
    log_dict = log_data.model_dump(exclude={'skills_transfers', 'follow_ups'})
    log = MentorshipLog(
        **log_dict,
        mentor_id=current_user.id,
        status=LogStatus.draft
    )

    db.add(log)
    db.flush()  # Get the log ID

    # Create nested skills transfers
    for st_data in skills_transfers_data:
        skills_transfer = SkillsTransfer(
            **st_data.model_dump(),
            mentorship_log_id=log.id
        )
        db.add(skills_transfer)

    # Create nested follow-ups
    for fu_data in follow_ups_data:
        follow_up = FollowUp(
            **fu_data.model_dump(),
            mentorship_log_id=log.id
        )
        db.add(follow_up)

    db.commit()
    db.refresh(log)

    return log


@router.put("/{log_id}", response_model=MentorshipLogResponse)
def update_mentorship_log(
    log_id: UUID,
    log_data: MentorshipLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a mentorship log (mentors only - can update their own drafts).

    Only draft logs can be updated.
    Submitted or approved logs cannot be edited.

    To update nested data (skills transfers, follow-ups), use dedicated endpoints.

    Permissions:
    - Only mentors can edit logs, and only their own draft logs
    - Supervisors and admins CANNOT edit logs - they can only review (approve/reject) and comment
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions - only mentors can edit, and only their own logs
    if log.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the log creator can edit their log. Supervisors should use comments and approve/reject actions."
        )

    # Check if log is editable
    if log.status != LogStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit {log.status.value} logs. Only draft logs can be edited."
        )

    # Handle nested data if provided
    skills_transfers_data = log_data.skills_transfers
    follow_ups_data = log_data.follow_ups

    # Update main log fields
    update_dict = log_data.model_dump(exclude={'skills_transfers', 'follow_ups'}, exclude_unset=True)
    for field, value in update_dict.items():
        setattr(log, field, value)

    # Update skills transfers if provided
    if skills_transfers_data is not None:
        # Delete existing skills transfers
        db.query(SkillsTransfer).filter(SkillsTransfer.mentorship_log_id == log.id).delete()

        # Create new skills transfers
        for st_data in skills_transfers_data:
            skills_transfer = SkillsTransfer(
                **st_data.model_dump(),
                mentorship_log_id=log.id
            )
            db.add(skills_transfer)

    # Update follow-ups if provided
    if follow_ups_data is not None:
        # Delete existing follow-ups
        db.query(FollowUp).filter(FollowUp.mentorship_log_id == log.id).delete()

        # Create new follow-ups
        for fu_data in follow_ups_data:
            follow_up = FollowUp(
                **fu_data.model_dump(),
                mentorship_log_id=log.id
            )
            db.add(follow_up)

    db.commit()
    db.refresh(log)

    return log


@router.post("/{log_id}/submit", response_model=MentorshipLogResponse)
def submit_mentorship_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a mentorship log for review.

    Changes status from "draft" to "submitted".
    Once submitted, the log cannot be edited until it's sent back to draft.

    Permissions:
    - Mentors can only submit their own logs
    - Supervisors and admins can submit any log
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions
    if current_user.role == UserRole.mentor and log.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own logs"
        )

    # Check current status
    if log.status != LogStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit {log.status.value} log. Only draft logs can be submitted."
        )

    # Update status
    log.status = LogStatus.submitted
    log.submitted_at = datetime.utcnow()

    # Notify specialists matching thematic areas
    if log.thematic_areas and isinstance(log.thematic_areas, list):
        for area in log.thematic_areas:
            # Find specialists for this thematic area
            specialists = db.query(User).join(UserSpecialization).filter(
                UserSpecialization.thematic_area == area,
                User.is_active == True,
                User.id != current_user.id  # Don't notify self
            ).all()

            for specialist in specialists:
                # Create notification (ignore duplicates via unique constraint)
                try:
                    notification = SpecialistNotification(
                        mentorship_log_id=log_id,
                        specialist_id=specialist.id,
                        thematic_area=area
                    )
                    db.add(notification)
                    db.flush()
                except Exception:
                    # Duplicate notification, ignore
                    db.rollback()
                    pass

    db.commit()
    db.refresh(log)

    return log


@router.post("/{log_id}/approve", response_model=MentorshipLogResponse)
def approve_mentorship_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor, UserRole.admin)),
):
    """
    Approve a mentorship log.

    Changes status from "submitted" to "approved".
    Records who approved and when.

    Permissions:
    - Admins can approve any log
    - Supervisors can only approve logs from their assigned mentees
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check if current user can approve this log
    if not can_approve_log(log, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only approve logs from your assigned mentees"
        )

    # Check current status
    if log.status != LogStatus.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve {log.status.value} log. Only submitted logs can be approved."
        )

    # Update status
    log.status = LogStatus.approved
    log.approved_at = datetime.utcnow()
    log.approved_by = current_user.id

    # Create approval notification for the mentor
    if log.mentor_id != current_user.id:  # Don't notify yourself
        approval_notification = Notification(
            user_id=log.mentor_id,
            notification_type=NotificationType.approval,
            title="Log Approved",
            message=f"Your mentorship log for {log.facility.name if log.facility else 'a facility'} has been approved by {current_user.name}",
            related_log_id=log_id,
            extra_data={
                "approver_name": current_user.name,
                "approver_role": current_user.role.value,
                "facility_name": log.facility.name if log.facility else None,
                "visit_date": log.visit_date.isoformat() if log.visit_date else None
            }
        )
        db.add(approval_notification)

    db.commit()
    db.refresh(log)

    return log


@router.post("/{log_id}/return-to-draft", response_model=MentorshipLogResponse)
def return_log_to_draft(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor, UserRole.admin)),
):
    """
    Return a submitted log back to draft status (Supervisor/Admin only).

    This allows the mentor to make corrections.
    Can only return submitted logs, not approved ones.

    Permissions:
    - Only supervisors and admins can return logs to draft
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check current status
    if log.status != LogStatus.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot return {log.status.value} log to draft. Only submitted logs can be returned."
        )

    # Update status
    log.status = LogStatus.draft
    log.submitted_at = None

    db.commit()
    db.refresh(log)

    return log


@router.post("/{log_id}/reject", response_model=MentorshipLogResponse)
def reject_mentorship_log(
    log_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor, UserRole.admin)),
):
    """
    Reject a submitted mentorship log (Supervisor/Admin only).

    Changes status from "submitted" to "draft" and stores the rejection reason.
    This allows the mentor to see why their log was rejected and make corrections.

    Permissions:
    - Only supervisors and admins can reject logs
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check current status
    if log.status != LogStatus.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject {log.status.value} log. Only submitted logs can be rejected."
        )

    # Validate reason is provided
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required"
        )

    # Update status and store rejection info
    log.status = LogStatus.draft
    log.rejected_at = datetime.utcnow()
    log.rejection_reason = reason
    log.submitted_at = None  # Clear submission timestamp

    # Create rejection notification for the mentor
    if log.mentor_id != current_user.id:  # Don't notify yourself
        rejection_notification = Notification(
            user_id=log.mentor_id,
            notification_type=NotificationType.rejection,
            title="Log Returned for Revision",
            message=f"Your mentorship log for {log.facility.name if log.facility else 'a facility'} has been returned by {current_user.name}. Reason: {reason}",
            related_log_id=log_id,
            extra_data={
                "rejector_name": current_user.name,
                "rejector_role": current_user.role.value,
                "facility_name": log.facility.name if log.facility else None,
                "visit_date": log.visit_date.isoformat() if log.visit_date else None,
                "rejection_reason": reason
            }
        )
        db.add(rejection_notification)

    db.commit()
    db.refresh(log)

    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentorship_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a mentorship log.

    Permissions:
    - Mentors can only delete their own draft logs
    - Admins can delete any log
    """
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions
    if current_user.role == UserRole.mentor:
        if log.mentor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own logs"
            )
        if log.status != LogStatus.draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only delete draft logs"
            )

    # Cascade delete will handle skills_transfers, follow_ups, and attachments
    db.delete(log)
    db.commit()

    return None
