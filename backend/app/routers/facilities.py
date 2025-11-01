"""
Facility Management Endpoints

Endpoints for managing facilities (health centers) in the mentorship system.
Facilities are pre-populated reference data that can be filtered by state and LGA.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Facility, User, UserRole
from app.schemas import FacilityCreate, FacilityUpdate, FacilityResponse, PaginatedResponse
from app.dependencies import get_current_user, require_role


router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("", response_model=PaginatedResponse[FacilityResponse])
def list_facilities(
    state: Optional[str] = Query(None, description="Filter by state (e.g., Kano, Jigawa, Bauchi)"),
    lga: Optional[str] = Query(None, description="Filter by Local Government Area"),
    search: Optional[str] = Query(None, description="Search facilities by name or code"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all facilities with optional filtering.

    Filters:
    - **state**: Filter by state (Kano, Jigawa, or Bauchi)
    - **lga**: Filter by Local Government Area
    - **search**: Search by facility name or code
    - **facility_type**: Filter by facility type

    Authenticated users can view all facilities.
    """
    query = db.query(Facility)

    # Apply filters
    if state:
        query = query.filter(Facility.state.ilike(f"%{state}%"))

    if lga:
        query = query.filter(Facility.lga.ilike(f"%{lga}%"))

    if facility_type:
        query = query.filter(Facility.facility_type.ilike(f"%{facility_type}%"))

    if search:
        query = query.filter(
            or_(
                Facility.name.ilike(f"%{search}%"),
                Facility.code.ilike(f"%{search}%")
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering
    facilities = (
        query
        .order_by(Facility.state, Facility.lga, Facility.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=facilities,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility(
    facility_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single facility by ID.

    Authenticated users can view facility details.
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    return facility


@router.post("", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(
    facility_data: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Create a new facility (Admin only).

    Only administrators can add new facilities to the system.
    """
    # Check if facility code already exists
    if facility_data.code:
        existing = db.query(Facility).filter(Facility.code == facility_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Facility with code '{facility_data.code}' already exists"
            )

    facility = Facility(**facility_data.model_dump())
    db.add(facility)
    db.commit()
    db.refresh(facility)

    return facility


@router.put("/{facility_id}", response_model=FacilityResponse)
def update_facility(
    facility_id: UUID,
    facility_data: FacilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Update a facility (Admin only).

    Only administrators can update facility information.
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    # Check if updating code to a code that already exists
    if facility_data.code and facility_data.code != facility.code:
        existing = db.query(Facility).filter(Facility.code == facility_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Facility with code '{facility_data.code}' already exists"
            )

    # Update facility fields
    update_data = facility_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(facility, field, value)

    db.commit()
    db.refresh(facility)

    return facility


@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(
    facility_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Delete a facility (Admin only).

    Only administrators can delete facilities.

    Note: This will fail if the facility has associated mentorship logs.
    Consider soft deletion or archiving in production.
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    # Check if facility has mentorship logs
    if facility.mentorship_logs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete facility with associated mentorship logs"
        )

    db.delete(facility)
    db.commit()

    return None
