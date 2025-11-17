"""
Comments Router

API endpoints for adding and viewing comments on mentorship logs.
Supports both general comments and specialist comments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, can_view_as_specialist
from app.models import User, MentorshipLog, LogComment, UserRole
from app.schemas import LogCommentCreate, LogCommentResponse, LogCommentUpdate

router = APIRouter(prefix="/api/mentorship-logs", tags=["comments"])


@router.get("/{log_id}/comments", response_model=List[LogCommentResponse])
async def get_log_comments(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a mentorship log.

    Users can see comments if they:
    - Own the log (mentor)
    - Are the assigned supervisor
    - Have specialist access to the log
    - Are admin
    """
    # Get the log
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Mentorship log not found")

    # Check access
    can_access = False

    # Own log
    if log.mentor_id == current_user.id:
        can_access = True

    # Admin
    elif current_user.role == UserRole.admin:
        can_access = True

    # Assigned supervisor
    elif current_user.role == UserRole.supervisor:
        mentor = db.query(User).filter(User.id == log.mentor_id).first()
        if mentor and mentor.supervisor_id == current_user.id:
            can_access = True

    # Specialist access
    if not can_access and can_view_as_specialist(log, current_user, db):
        can_access = True

    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to view comments on this log"
        )

    # Get comments
    comments = db.query(LogComment).filter(
        LogComment.mentorship_log_id == log_id
    ).order_by(LogComment.created_at.asc()).all()

    # Build response with user info
    result = []
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "mentorship_log_id": comment.mentorship_log_id,
            "user_id": comment.user_id,
            "user_name": comment.user.name,
            "user_role": comment.user.role,
            "comment_text": comment.comment_text,
            "is_specialist_comment": comment.is_specialist_comment,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }
        result.append(LogCommentResponse(**comment_dict))

    return result


@router.post("/{log_id}/comments", response_model=LogCommentResponse, status_code=201)
async def create_log_comment(
    log_id: UUID,
    comment_data: LogCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a comment to a mentorship log.

    Anyone with access to view the log can comment:
    - Mentor (own log)
    - Assigned supervisor
    - Specialists in matching thematic areas
    - Admin
    """
    # Get the log
    log = db.query(MentorshipLog).filter(MentorshipLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Mentorship log not found")

    # Check access (same as getting comments)
    can_access = False
    is_specialist = False

    # Own log
    if log.mentor_id == current_user.id:
        can_access = True

    # Admin
    elif current_user.role == UserRole.admin:
        can_access = True

    # Assigned supervisor
    elif current_user.role == UserRole.supervisor:
        mentor = db.query(User).filter(User.id == log.mentor_id).first()
        if mentor and mentor.supervisor_id == current_user.id:
            can_access = True

    # Specialist access
    if not can_access and can_view_as_specialist(log, current_user, db):
        can_access = True
        is_specialist = True

    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to comment on this log"
        )

    # Create comment
    new_comment = LogComment(
        mentorship_log_id=log_id,
        user_id=current_user.id,
        comment_text=comment_data.comment_text,
        is_specialist_comment=is_specialist or comment_data.is_specialist_comment
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Return enriched response
    return LogCommentResponse(
        id=new_comment.id,
        mentorship_log_id=new_comment.mentorship_log_id,
        user_id=new_comment.user_id,
        user_name=current_user.name,
        user_role=current_user.role,
        comment_text=new_comment.comment_text,
        is_specialist_comment=new_comment.is_specialist_comment,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
    )


@router.put("/comments/{comment_id}", response_model=LogCommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_data: LogCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment. Only the comment author or admin can update.
    """
    comment = db.query(LogComment).filter(LogComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only comment author or admin can update
    if comment.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own comments"
        )

    # Update comment
    comment.comment_text = comment_data.comment_text
    db.commit()
    db.refresh(comment)

    return LogCommentResponse(
        id=comment.id,
        mentorship_log_id=comment.mentorship_log_id,
        user_id=comment.user_id,
        user_name=comment.user.name,
        user_role=comment.user.role,
        comment_text=comment.comment_text,
        is_specialist_comment=comment.is_specialist_comment,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment. Only the comment author or admin can delete.
    """
    comment = db.query(LogComment).filter(LogComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only comment author or admin can delete
    if comment.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comments"
        )

    db.delete(comment)
    db.commit()

    return None
