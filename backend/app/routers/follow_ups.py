"""
Follow-Up Management Endpoints

Endpoints for managing action items (follow-ups) from mentorship logs.
Follow-ups track action items from Section 5 of the ACE2 PDF form.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.database import get_db
from app.models import FollowUp, MentorshipLog, User, UserRole, FollowUpStatus
from app.schemas import FollowUpCreate, FollowUpUpdate, FollowUpResponse, PaginatedResponse
from app.dependencies import get_current_user, require_role


router = APIRouter(prefix="/api/follow-ups", tags=["follow-ups"])


def check_follow_up_permissions(current_user: User, mentorship_log: MentorshipLog, operation: str = "manage") -> None:
    """
    Check if current user has permission to manage follow-up.

    Rules:
    - Admins and supervisors can manage all follow-ups
    - Mentors can only manage follow-ups for their own logs
    - Assigned users can update status of their assigned follow-ups (checked separately)
    """
    # Admins and supervisors can manage all follow-ups
    if current_user.role in [UserRole.admin, UserRole.supervisor]:
        return

    # Mentors can only manage follow-ups for their own logs
    if current_user.role == UserRole.mentor:
        if mentorship_log.mentor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage follow-ups for your own mentorship logs"
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


def check_follow_up_update_permissions(current_user: User, follow_up: FollowUp) -> None:
    """
    Check if current user can update this follow-up.

    Rules:
    - Admins and supervisors can update all follow-ups
    - Mentors can update follow-ups for their own logs
    - Assigned users can update their assigned follow-ups (including status)
    """
    # Admins and supervisors can update all
    if current_user.role in [UserRole.admin, UserRole.supervisor]:
        return

    # Check if user is the mentor of the log
    if follow_up.mentorship_log.mentor_id == current_user.id:
        return

    # Check if user is assigned to this follow-up
    if follow_up.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to update this follow-up"
    )


@router.get("", response_model=PaginatedResponse[FollowUpResponse])
def list_follow_ups(
    status: Optional[FollowUpStatus] = Query(None, description="Filter by status"),
    mentorship_log_id: Optional[UUID] = Query(None, description="Filter by mentorship log"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    priority: Optional[str] = Query(None, description="Filter by priority (High/Medium/Low)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all follow-ups with optional filtering.

    Filters:
    - **status**: Filter by status (pending, in_progress, completed)
    - **mentorship_log_id**: Filter by mentorship log
    - **assigned_to**: Filter by assigned user
    - **priority**: Filter by priority (High, Medium, Low)

    Permissions:
    - Admins and supervisors can view all follow-ups
    - Mentors can only view follow-ups from their own logs or assigned to them
    """
    query = db.query(FollowUp)

    # Role-based filtering for mentors
    if current_user.role == UserRole.mentor:
        # Mentors can only see follow-ups from their own logs or assigned to them
        query = query.join(FollowUp.mentorship_log).filter(
            or_(
                MentorshipLog.mentor_id == current_user.id,
                FollowUp.assigned_to == current_user.id
            )
        )

    # Apply filters
    if status:
        query = query.filter(FollowUp.status == status)

    if mentorship_log_id:
        query = query.filter(FollowUp.mentorship_log_id == mentorship_log_id)

    if assigned_to:
        query = query.filter(FollowUp.assigned_to == assigned_to)

    if priority:
        query = query.filter(FollowUp.priority == priority)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    follow_ups = (
        query
        .order_by(FollowUp.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=follow_ups,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{follow_up_id}", response_model=FollowUpResponse)
def get_follow_up(
    follow_up_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single follow-up by ID.

    Authenticated users can view follow-up details.
    """
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    return follow_up


@router.post("", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_follow_up(
    follow_up_data: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new follow-up action item.

    Permissions:
    - Admins and supervisors can create follow-ups for any log
    - Mentors can create follow-ups for their own logs
    """
    # Get the mentorship log
    mentorship_log = db.query(MentorshipLog).filter(
        MentorshipLog.id == follow_up_data.mentorship_log_id
    ).first()

    if not mentorship_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions
    check_follow_up_permissions(current_user, mentorship_log, "create")

    # Create follow-up
    follow_up_dict = follow_up_data.model_dump()
    follow_up = FollowUp(**follow_up_dict)

    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)

    return follow_up


@router.put("/{follow_up_id}", response_model=FollowUpResponse)
def update_follow_up(
    follow_up_id: UUID,
    follow_up_data: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a follow-up.

    Permissions:
    - Admins and supervisors can update any follow-up
    - Mentors can update follow-ups for their own logs
    - Assigned users can update their assigned follow-ups
    """
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    # Check permissions
    check_follow_up_update_permissions(current_user, follow_up)

    # Update follow-up fields
    update_dict = follow_up_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(follow_up, field, value)

    db.commit()
    db.refresh(follow_up)

    return follow_up


@router.put("/{follow_up_id}/in-progress", response_model=FollowUpResponse)
def mark_follow_up_in_progress(
    follow_up_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a follow-up as in progress.

    Permissions:
    - Admins and supervisors can mark any follow-up as in progress
    - Mentors can mark their own logs' follow-ups as in progress
    - Assigned users can mark their assigned follow-ups as in progress
    """
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    # Check permissions
    check_follow_up_update_permissions(current_user, follow_up)

    # Update status
    follow_up.status = FollowUpStatus.in_progress

    db.commit()
    db.refresh(follow_up)

    return follow_up


@router.put("/{follow_up_id}/complete", response_model=FollowUpResponse)
def mark_follow_up_completed(
    follow_up_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a follow-up as completed.

    Permissions:
    - Admins and supervisors can mark any follow-up as completed
    - Mentors can mark their own logs' follow-ups as completed
    - Assigned users can mark their assigned follow-ups as completed
    """
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    # Check permissions
    check_follow_up_update_permissions(current_user, follow_up)

    # Update status and set completion time
    follow_up.status = FollowUpStatus.completed
    follow_up.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(follow_up)

    return follow_up


@router.delete("/{follow_up_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_follow_up(
    follow_up_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a follow-up.

    Permissions:
    - Admins and supervisors can delete any follow-up
    - Mentors can delete follow-ups for their own logs
    """
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    # Check permissions (use the mentorship_log's permissions)
    check_follow_up_permissions(current_user, follow_up.mentorship_log, "delete")

    db.delete(follow_up)
    db.commit()

    return None
