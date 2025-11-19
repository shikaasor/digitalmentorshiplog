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
from app.models import User, SpecialistNotification, MentorshipLog, Notification
from app.schemas import SpecialistNotificationResponse, MarkNotificationReadRequest, NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all notifications for the current user (unified format).

    Includes:
    - Comment notifications
    - Approval notifications
    - Rejection notifications
    - Specialist log notifications

    Query params:
    - unread_only: If true, only return unread notifications
    """
    all_notifications = []

    # 1. Get new unified notifications (comments, approvals, rejections)
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    unified_notifs = query.order_by(Notification.created_at.desc()).all()

    for notif in unified_notifs:
        all_notifications.append(NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            notification_type=notif.notification_type.value,
            title=notif.title,
            message=notif.message,
            related_log_id=notif.related_log_id,
            related_comment_id=notif.related_comment_id,
            extra_data=notif.extra_data,
            is_read=notif.is_read,
            created_at=notif.created_at,
            read_at=notif.read_at
        ))

    # 2. Get specialist notifications (legacy format, convert to unified)
    specialist_query = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id
    )

    if unread_only:
        specialist_query = specialist_query.filter(SpecialistNotification.is_read == False)

    specialist_notifs = specialist_query.order_by(SpecialistNotification.notified_at.desc()).all()

    for notif in specialist_notifs:
        log = db.query(MentorshipLog).filter(
            MentorshipLog.id == notif.mentorship_log_id
        ).first()

        if log:
            all_notifications.append(NotificationResponse(
                id=notif.id,
                user_id=notif.specialist_id,
                notification_type="specialist_log",
                title=f"New log in your area: {notif.thematic_area}",
                message=f"A mentorship log for {log.facility.name if log.facility else 'a facility'} has been submitted in your specialization area",
                related_log_id=notif.mentorship_log_id,
                related_comment_id=None,
                extra_data={
                    "thematic_area": notif.thematic_area,
                    "facility_name": log.facility.name if log.facility else None,
                    "mentor_name": log.mentor.name if log.mentor else None,
                    "visit_date": log.visit_date.isoformat() if log.visit_date else None
                },
                is_read=notif.is_read,
                created_at=notif.notified_at,
                read_at=notif.read_at
            ))

    # Sort all notifications by created_at descending
    all_notifications.sort(key=lambda x: x.created_at, reverse=True)

    return all_notifications


@router.get("/count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications for the current user (all types).
    """
    # Count unified notifications
    unified_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    # Count specialist notifications
    specialist_count = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id,
        SpecialistNotification.is_read == False
    ).count()

    total_count = unified_count + specialist_count

    return {"unread_count": total_count}


@router.post("/mark-read", status_code=200)
async def mark_notifications_read(
    request: MarkNotificationReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark one or more notifications as read (handles both unified and specialist notifications).
    """
    marked_count = 0

    # Try unified notifications first
    unified_notifs = db.query(Notification).filter(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == current_user.id
    ).all()

    for notif in unified_notifs:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
        marked_count += 1

    # Try specialist notifications
    specialist_notifs = db.query(SpecialistNotification).filter(
        SpecialistNotification.id.in_(request.notification_ids),
        SpecialistNotification.specialist_id == current_user.id
    ).all()

    for notif in specialist_notifs:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
        marked_count += 1

    if marked_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No notifications found with the provided IDs"
        )

    db.commit()

    return {"message": f"{marked_count} notification(s) marked as read"}


@router.post("/mark-all-read", status_code=200)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user (both types).
    """
    # Mark unified notifications as read
    unified_notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()

    for notif in unified_notifs:
        notif.is_read = True
        notif.read_at = datetime.utcnow()

    # Mark specialist notifications as read
    specialist_notifs = db.query(SpecialistNotification).filter(
        SpecialistNotification.specialist_id == current_user.id,
        SpecialistNotification.is_read == False
    ).all()

    for notif in specialist_notifs:
        notif.is_read = True
        notif.read_at = datetime.utcnow()

    total_count = len(unified_notifs) + len(specialist_notifs)

    db.commit()

    return {"message": f"{total_count} notification(s) marked as read"}


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification (handles both types).
    """
    # Try unified notification first
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if notification:
        db.delete(notification)
        db.commit()
        return None

    # Try specialist notification
    specialist_notif = db.query(SpecialistNotification).filter(
        SpecialistNotification.id == notification_id,
        SpecialistNotification.specialist_id == current_user.id
    ).first()

    if specialist_notif:
        db.delete(specialist_notif)
        db.commit()
        return None

    raise HTTPException(status_code=404, detail="Notification not found")
