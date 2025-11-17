"""
Constants for Digital Mentorship Log
Extracted from ACE2_Mentorship_Log.pdf

These constants define the valid options for checkbox fields in the mentorship log form.
Frontend should render these as checkboxes, with selected values stored as arrays in the database.
"""

from enum import Enum


# =============================================================================
# HEADER FIELDS
# =============================================================================

class InteractionType:
    """Valid interaction types for mentorship visits"""
    ON_SITE = "On-site"
    VIRTUAL = "Virtual"
    PHONE = "Phone"

    @classmethod
    def choices(cls):
        return [cls.ON_SITE, cls.VIRTUAL, cls.PHONE]


class State:
    """Valid states for facilities (from PDF form)"""
    KANO = "Kano"
    JIGAWA = "Jigawa"
    BAUCHI = "Bauchi"

    @classmethod
    def choices(cls):
        return [cls.KANO, cls.JIGAWA, cls.BAUCHI]


class FacilityType:
    """Valid facility types (healthcare facility levels)"""
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    TERTIARY = "Tertiary"

    @classmethod
    def choices(cls):
        return [cls.PRIMARY, cls.SECONDARY, cls.TERTIARY]


# =============================================================================
# SECTION 1: ACTIVITIES CONDUCTED
# =============================================================================

class ActivityType:
    """
    Section 1: Activities Conducted checkbox options

    Frontend Implementation:
    - Render 7 checkboxes + "Other" checkbox
    - If "Other" is selected, show text input for activities_other_specify
    - Store selected values as array in activities_conducted field
    - Store "Other" description in activities_other_specify field
    """
    DIRECT_CLINICAL_SERVICE = "Direct clinical service"
    SIDE_BY_SIDE_MENTORSHIP = "Side-by-side mentorship"
    CASE_REVIEW_DISCUSSION = "Case review/discussion"
    DATA_REVIEW_ANALYSIS = "Data review and analysis"
    SYSTEMS_ASSESSMENT = "Systems assessment/improvement"
    TRAINING_DEMONSTRATION = "Training/demonstration"
    MEETING_FACILITATION = "Meeting facilitation"
    OTHER = "Other"

    @classmethod
    def choices(cls):
        return [
            cls.DIRECT_CLINICAL_SERVICE,
            cls.SIDE_BY_SIDE_MENTORSHIP,
            cls.CASE_REVIEW_DISCUSSION,
            cls.DATA_REVIEW_ANALYSIS,
            cls.SYSTEMS_ASSESSMENT,
            cls.TRAINING_DEMONSTRATION,
            cls.MEETING_FACILITATION,
            cls.OTHER,
        ]


# =============================================================================
# SECTION 2: THEMATIC AREAS COVERED
# =============================================================================

class ThematicArea:
    """
    Section 2: Thematic Areas Covered checkbox options

    Frontend Implementation:
    - Render 9 checkboxes + "Other" checkbox
    - If "Other" is selected, show text input for thematic_areas_other_specify
    - Store selected values as array in thematic_areas field
    - Store "Other" description in thematic_areas_other_specify field
    """
    ART_SERVICES = "General HIV care and treatment"
    CARE_AND_SUPPORT = "Care and Support"
    PEDIATRIC_HIV = "Pediatric HIV management"
    PMTCT = "PMTCT"
    TB_HIV = "TB/HIV"
    LABORATORY_SERVICES = "Laboratory services"
    SUPPLY_CHAIN = "Supply chain"
    STRATEGIC_INFORMATION = "Strategic Information"
    QUALITY_IMPROVEMENT = "Quality improvement"
    OTHER = "Other"

    @classmethod
    def choices(cls):
        return [
            cls.ART_SERVICES,
            cls.CARE_AND_SUPPORT,
            cls.PEDIATRIC_HIV,
            cls.PMTCT,
            cls.TB_HIV,
            cls.LABORATORY_SERVICES,
            cls.SUPPLY_CHAIN,
            cls.STRATEGIC_INFORMATION,
            cls.QUALITY_IMPROVEMENT,
            cls.OTHER,
        ]


# =============================================================================
# SECTION 4: SKILLS TRANSFER - COMPETENCY LEVELS
# =============================================================================

class CompetencyLevel:
    """
    Section 4: Skills Transfer - Competency Level options

    Common competency assessment levels used in clinical mentorship.
    Frontend can render as dropdown or radio buttons.
    """
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    PROFICIENT = "Proficient"
    EXPERT = "Expert"

    @classmethod
    def choices(cls):
        return [
            cls.BEGINNER,
            cls.INTERMEDIATE,
            cls.ADVANCED,
            cls.PROFICIENT,
            cls.EXPERT,
        ]


class TransferMethod:
    """
    Section 4: Skills Transfer - Method of transfer

    Common methods used for skills transfer in clinical settings.
    Frontend can render as dropdown or checkboxes.
    """
    DEMONSTRATION = "Demonstration"
    HANDS_ON_PRACTICE = "Hands-on practice"
    OBSERVATION = "Observation"
    DISCUSSION = "Discussion"
    PRESENTATION = "Presentation"
    SIMULATION = "Simulation"
    OTHER = "Other"

    @classmethod
    def choices(cls):
        return [
            cls.DEMONSTRATION,
            cls.HANDS_ON_PRACTICE,
            cls.OBSERVATION,
            cls.DISCUSSION,
            cls.PRESENTATION,
            cls.SIMULATION,
            cls.OTHER,
        ]


# =============================================================================
# SECTION 5: ACTION ITEMS - PRIORITY LEVELS
# =============================================================================

class Priority:
    """
    Section 5: Action Items - Priority levels

    Standard priority classification for action items and follow-ups.
    Frontend should render as dropdown or radio buttons with color coding.
    """
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    @classmethod
    def choices(cls):
        return [cls.HIGH, cls.MEDIUM, cls.LOW]


# =============================================================================
# SECTION 8: ATTACHMENTS
# =============================================================================

class AttachmentType:
    """
    Section 8: Attachments checkbox options

    Frontend Implementation:
    - Render 4 checkboxes
    - Store selected types as array in attachment_types field
    - Each checkbox indicates the TYPE of attachments included
    - Actual file uploads are stored in attachments table
    """
    PHOTOS = "Photos (with consent)"
    TOOLS_TEMPLATES = "Tools/Templates Shared"
    BEFORE_AFTER = "Before/After Documentation"
    REFERENCE_MATERIALS = "Reference Materials"

    @classmethod
    def choices(cls):
        return [
            cls.PHOTOS,
            cls.TOOLS_TEMPLATES,
            cls.BEFORE_AFTER,
            cls.REFERENCE_MATERIALS,
        ]


# =============================================================================
# COMMON CADRES (for mentees_present and skills_transfer recipient_cadre)
# =============================================================================

class Cadre:
    """
    Common healthcare worker cadres in Nigerian health facilities

    Used in:
    - Header: Mentees Present (Name & Cadre)
    - Section 4: Skills Transfer - Recipient Name & Cadre

    Frontend can render as dropdown or text input with autocomplete.
    """
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    MIDWIFE = "Midwife"
    PHARMACIST = "Pharmacist"
    PHARMACY_TECHNICIAN = "Pharmacy Technician"
    LAB_SCIENTIST = "Laboratory Scientist"
    LAB_TECHNICIAN = "Laboratory Technician"
    CHEW = "Community Health Extension Worker (CHEW)"
    CHO = "Community Health Officer (CHO)"
    DATA_CLERK = "Data Clerk"
    M_AND_E_OFFICER = "M&E Officer"
    OTHER = "Other"

    @classmethod
    def choices(cls):
        return [
            cls.DOCTOR,
            cls.NURSE,
            cls.MIDWIFE,
            cls.PHARMACIST,
            cls.PHARMACY_TECHNICIAN,
            cls.LAB_SCIENTIST,
            cls.LAB_TECHNICIAN,
            cls.CHEW,
            cls.CHO,
            cls.DATA_CLERK,
            cls.M_AND_E_OFFICER,
            cls.OTHER,
        ]


# =============================================================================
# FRONTEND USAGE EXAMPLES
# =============================================================================

"""
Example: Section 1 - Activities Conducted

Frontend sends:
{
  "activities_conducted": [
    "Direct clinical service",
    "Case review/discussion",
    "Other"
  ],
  "activities_other_specify": "Community health education session"
}

Database stores:
- activities_conducted: ["Direct clinical service", "Case review/discussion", "Other"] (JSON array)
- activities_other_specify: "Community health education session" (Text)


Example: Section 2 - Thematic Areas

Frontend sends:
{
  "thematic_areas": [
    "General HIV care and treatment",
    "PMTCT",
    "Other"
  ],
  "thematic_areas_other_specify": "Prevention and adherence counseling"
}

Database stores:
- thematic_areas: ["General HIV care and treatment", "PMTCT", "Other"] (JSON array)
- thematic_areas_other_specify: "Prevention and adherence counseling" (Text)


Example: Section 8 - Attachments

Frontend sends:
{
  "attachment_types": [
    "Photos (with consent)",
    "Tools/Templates Shared"
  ]
}

Database stores:
- attachment_types: ["Photos (with consent)", "Tools/Templates Shared"] (JSON array)

Note: Actual file uploads go to attachments table with file_path, file_name, etc.


Example: Header - Mentees Present

Frontend sends:
{
  "mentees_present": [
    {"name": "Dr. Ahmed Ibrahim", "cadre": "Doctor"},
    {"name": "Nurse Fatima Usman", "cadre": "Nurse"}
  ]
}

Database stores:
- mentees_present: [{"name": "Dr. Ahmed Ibrahim", "cadre": "Doctor"}, ...] (JSON array)
"""
