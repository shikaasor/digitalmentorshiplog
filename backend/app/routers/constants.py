"""
Constants Endpoints

API endpoints to expose application constants to the frontend.
This ensures frontend uses the same predefined values as the backend.
"""

from fastapi import APIRouter
from typing import List, Dict
from app.constants import (
    InteractionType,
    State,
    FacilityType,
    ActivityType,
    ThematicArea,
    CompetencyLevel,
    TransferMethod,
    Priority,
    AttachmentType,
    Cadre,
)

router = APIRouter(prefix="/api/constants", tags=["constants"])


@router.get("/all")
def get_all_constants() -> Dict[str, List[str]]:
    """
    Get all application constants in a single response.

    Returns a dictionary with all predefined values for form fields.
    Frontend can use these to populate dropdowns, checkboxes, etc.
    """
    return {
        "interaction_types": InteractionType.choices(),
        "states": State.choices(),
        "facility_types": FacilityType.choices(),
        "activity_types": ActivityType.choices(),
        "thematic_areas": ThematicArea.choices(),
        "competency_levels": CompetencyLevel.choices(),
        "transfer_methods": TransferMethod.choices(),
        "priorities": Priority.choices(),
        "attachment_types": AttachmentType.choices(),
        "cadres": Cadre.choices(),
    }


@router.get("/states")
def get_states() -> List[str]:
    """Get list of valid states (Kano, Jigawa, Bauchi)"""
    return State.choices()


@router.get("/facility-types")
def get_facility_types() -> List[str]:
    """Get list of valid facility types (Primary, Secondary, Tertiary)"""
    return FacilityType.choices()


@router.get("/interaction-types")
def get_interaction_types() -> List[str]:
    """Get list of valid interaction types for mentorship visits"""
    return InteractionType.choices()


@router.get("/activity-types")
def get_activity_types() -> List[str]:
    """Get list of valid activity types for Section 1"""
    return ActivityType.choices()


@router.get("/thematic-areas")
def get_thematic_areas() -> List[str]:
    """Get list of valid thematic areas for Section 2"""
    return ThematicArea.choices()


@router.get("/competency-levels")
def get_competency_levels() -> List[str]:
    """Get list of valid competency levels for skills transfer"""
    return CompetencyLevel.choices()


@router.get("/transfer-methods")
def get_transfer_methods() -> List[str]:
    """Get list of valid transfer methods for skills transfer"""
    return TransferMethod.choices()


@router.get("/priorities")
def get_priorities() -> List[str]:
    """Get list of valid priority levels for action items"""
    return Priority.choices()


@router.get("/attachment-types")
def get_attachment_types() -> List[str]:
    """Get list of valid attachment types for Section 8"""
    return AttachmentType.choices()


@router.get("/cadres")
def get_cadres() -> List[str]:
    """Get list of valid healthcare worker cadres"""
    return Cadre.choices()
