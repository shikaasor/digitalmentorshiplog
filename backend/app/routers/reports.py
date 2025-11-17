"""
Reports API Endpoints

Basic operational reports providing visibility into mentorship operations.
Includes summary statistics, activity tracking, and follow-up monitoring.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.models import User, UserRole, Facility, MentorshipLog, FollowUp, LogStatus, FollowUpStatus
from app.dependencies import require_role


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
def get_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor)),
):
    """
    Get overall summary statistics.

    Permissions:
    - Only admins and supervisors can access summary reports

    Returns:
    - Total counts for logs, facilities, mentors, follow-ups
    - Breakdown by status for logs and follow-ups
    """
    # Total logs
    total_logs = db.query(func.count(MentorshipLog.id)).scalar()

    # Logs by status
    logs_by_status_query = db.query(
        MentorshipLog.status,
        func.count(MentorshipLog.id).label('count')
    ).group_by(MentorshipLog.status).all()

    logs_by_status = {status.value: count for status, count in logs_by_status_query}

    # Total facilities
    total_facilities = db.query(func.count(Facility.id)).scalar()

    # Total mentors (users with mentor role)
    total_mentors = db.query(func.count(User.id)).filter(
        User.role == UserRole.mentor
    ).scalar()

    # Total follow-ups
    total_follow_ups = db.query(func.count(FollowUp.id)).scalar()

    # Follow-ups by status
    follow_ups_by_status_query = db.query(
        FollowUp.status,
        func.count(FollowUp.id).label('count')
    ).group_by(FollowUp.status).all()

    follow_ups_by_status = {status.value: count for status, count in follow_ups_by_status_query}

    return {
        "total_logs": total_logs,
        "logs_by_status": logs_by_status,
        "total_facilities": total_facilities,
        "total_mentors": total_mentors,
        "total_follow_ups": total_follow_ups,
        "follow_ups_by_status": follow_ups_by_status
    }


@router.get("/mentorship-logs")
def get_mentorship_logs_report(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    mentor_id: Optional[UUID] = Query(None, description="Filter by mentor"),
    facility_id: Optional[UUID] = Query(None, description="Filter by facility"),
    status: Optional[LogStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor)),
):
    """
    Get mentorship logs report with filtering.

    Permissions:
    - Only admins and supervisors can access logs reports

    Filters:
    - **start_date**: Filter logs from this date onwards
    - **end_date**: Filter logs up to this date
    - **mentor_id**: Filter by specific mentor
    - **facility_id**: Filter by specific facility
    - **status**: Filter by log status

    Returns:
    - Total count of logs matching filters
    - Breakdown by mentor, facility, state
    """
    query = db.query(MentorshipLog)

    # Apply filters
    if start_date:
        query = query.filter(MentorshipLog.visit_date >= start_date)

    if end_date:
        query = query.filter(MentorshipLog.visit_date <= end_date)

    if mentor_id:
        query = query.filter(MentorshipLog.mentor_id == mentor_id)

    if facility_id:
        query = query.filter(MentorshipLog.facility_id == facility_id)

    if status:
        query = query.filter(MentorshipLog.status == status)

    # Total count
    total_count = query.count()

    # Logs by mentor
    logs_by_mentor_query = (
        query
        .join(User, MentorshipLog.mentor_id == User.id)
        .with_entities(
            User.id,
            User.name,
            func.count(MentorshipLog.id).label('count')
        )
        .group_by(User.id, User.name)
        .all()
    )

    logs_by_mentor = [
        {"mentor_id": str(mentor_id), "mentor_name": name, "count": count}
        for mentor_id, name, count in logs_by_mentor_query
    ]

    # Logs by facility
    logs_by_facility_query = (
        query
        .join(Facility, MentorshipLog.facility_id == Facility.id)
        .with_entities(
            Facility.id,
            Facility.name,
            func.count(MentorshipLog.id).label('count')
        )
        .group_by(Facility.id, Facility.name)
        .all()
    )

    logs_by_facility = [
        {"facility_id": str(facility_id), "facility_name": name, "count": count}
        for facility_id, name, count in logs_by_facility_query
    ]

    # Logs by state
    logs_by_state_query = (
        query
        .join(Facility, MentorshipLog.facility_id == Facility.id)
        .with_entities(
            Facility.state,
            func.count(MentorshipLog.id).label('count')
        )
        .group_by(Facility.state)
        .all()
    )

    logs_by_state = [
        {"state": state, "count": count}
        for state, count in logs_by_state_query
    ]

    return {
        "total_count": total_count,
        "logs_by_mentor": logs_by_mentor,
        "logs_by_facility": logs_by_facility,
        "logs_by_state": logs_by_state
    }


@router.get("/follow-ups")
def get_follow_ups_report(
    status: Optional[FollowUpStatus] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor)),
):
    """
    Get follow-ups report with filtering.

    Permissions:
    - Only admins and supervisors can access follow-ups reports

    Filters:
    - **status**: Filter by follow-up status
    - **priority**: Filter by priority (High/Medium/Low)

    Returns:
    - Total count of follow-ups
    - Pending and overdue counts
    - Breakdown by status
    """
    query = db.query(FollowUp)

    # Apply filters
    if status:
        query = query.filter(FollowUp.status == status)

    if priority:
        query = query.filter(FollowUp.priority == priority)

    # Total count
    total_count = query.count()

    # Pending count
    pending_query = db.query(func.count(FollowUp.id)).filter(
        FollowUp.status == FollowUpStatus.pending
    )
    if priority:
        pending_query = pending_query.filter(FollowUp.priority == priority)
    pending_count = pending_query.scalar()

    # Overdue count (pending/in_progress with target_date < today)
    today = date.today()
    overdue_query = db.query(func.count(FollowUp.id)).filter(
        FollowUp.status.in_([FollowUpStatus.pending, FollowUpStatus.in_progress]),
        FollowUp.target_date < today
    )
    if priority:
        overdue_query = overdue_query.filter(FollowUp.priority == priority)
    overdue_count = overdue_query.scalar()

    # Follow-ups by status
    by_status_query = query.with_entities(
        FollowUp.status,
        func.count(FollowUp.id).label('count')
    ).group_by(FollowUp.status).all()

    by_status = {status.value: count for status, count in by_status_query}

    return {
        "total_count": total_count,
        "pending_count": pending_count,
        "overdue_count": overdue_count,
        "by_status": by_status
    }


@router.get("/facility-coverage")
def get_facility_coverage_report(
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor)),
):
    """
    Get facility coverage report showing visit tracking.

    Permissions:
    - Only admins and supervisors can access facility coverage reports

    Filters:
    - **state**: Filter by state

    Returns:
    - Total facilities count
    - Visited and unvisited facility counts
    - List of facilities with visit statistics
    """
    # Get all facilities
    facilities_query = db.query(Facility)

    if state:
        facilities_query = facilities_query.filter(Facility.state == state)

    all_facilities = facilities_query.all()
    total_facilities = len(all_facilities)

    # Get visit statistics per facility
    visit_stats_query = (
        db.query(
            Facility.id,
            Facility.name,
            Facility.code,
            Facility.state,
            Facility.lga,
            func.count(MentorshipLog.id).label('visit_count'),
            func.max(MentorshipLog.visit_date).label('last_visit_date')
        )
        .outerjoin(MentorshipLog, Facility.id == MentorshipLog.facility_id)
        .group_by(Facility.id, Facility.name, Facility.code, Facility.state, Facility.lga)
    )

    if state:
        visit_stats_query = visit_stats_query.filter(Facility.state == state)

    visit_stats = visit_stats_query.all()

    # Build facility list
    facilities = []
    visited_count = 0
    unvisited_count = 0

    for facility_id, name, code, fac_state, lga, visit_count, last_visit in visit_stats:
        if visit_count > 0:
            visited_count += 1
        else:
            unvisited_count += 1

        facilities.append({
            "facility_id": str(facility_id),
            "facility_name": name,
            "facility_code": code,
            "state": fac_state,
            "lga": lga,
            "visit_count": visit_count,
            "last_visit_date": str(last_visit) if last_visit else None
        })

    return {
        "total_facilities": total_facilities,
        "visited_facilities": visited_count,
        "unvisited_facilities": unvisited_count,
        "facilities": facilities
    }
