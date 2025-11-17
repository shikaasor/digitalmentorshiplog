"""
Notifications Router

API endpoints for managing specialist notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, SpecialistNotification, MentorshipLog
from app.schemas import SpecialistNotificationResponse, MarkNotificationReadRequest

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/", response_model=List[SpecialistNotificationResponse])
async def get_my_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user.

    Query params:
    - unread_only: If true, only return unread notifications
    """
    query = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id
    )

    if unread_only:
        query = query.filter(SpecialistNotification.is_read == False)

    notifications = query.order_by(SpecialistNotification.notified_at.desc()).all()

    # Enrich with log details
    result = []
    for notif in notifications:
        log = db.query(MentorshipLog).filter(
            MentorshipLog.id == notif.mentorship_log_id
        ).first()

        if log:
            notif_dict = {
                "id": notif.id,
                "mentorship_log_id": notif.mentorship_log_id,
                "specialist_id": notif.specialist_id,
                "thematic_area": notif.thematic_area,
                "is_read": notif.is_read,
                "notified_at": notif.notified_at,
                "read_at": notif.read_at,
                "log_facility_name": log.facility.name if log.facility else None,
                "log_mentor_name": log.mentor.name if log.mentor else None,
                "log_visit_date": log.visit_date,
            }
            result.append(SpecialistNotificationResponse(**notif_dict))

    return result


@router.get("/count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications for the current user.
    """
    count = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id,
        SpecialistNotification.is_read == False
    ).count()

    return {"unread_count": count}


@router.post("/mark-read", status_code=200)
async def mark_notifications_read(
    request: MarkNotificationReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark one or more notifications as read.
    """
    # Get notifications
    notifications = db.query(SpecialistNotification).filter(
        SpecialistNotification.id.in_(request.notification_ids),
        SpecialistNotification.specialist_id == current_user.id
    ).all()

    if not notifications:
        raise HTTPException(
            status_code=404,
            detail="No notifications found with the provided IDs"
        )

    # Mark as read
    for notif in notifications:
        notif.is_read = True
        notif.read_at = datetime.utcnow()

    db.commit()

    return {"message": f"{len(notifications)} notification(s) marked as read"}


@router.post("/mark-all-read", status_code=200)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user.
    """
    notifications = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id,
        SpecialistNotification.is_read == False
    ).all()

    count = len(notifications)

    for notif in notifications:
        notif.is_read = True
        notif.read_at = datetime.utcnow()

    db.commit()

    return {"message": f"{count} notification(s) marked as read"}


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification.
    """
    notification = db.query(SpecialistNotification).filter(
        SpecialistNotification.id == notification_id,
        SpecialistNotification.specialist_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()

    return None
