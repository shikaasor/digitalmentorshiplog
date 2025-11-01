"""
Attachment Management Endpoints

Endpoints for uploading, downloading, and managing file attachments
for mentorship logs (Section 8 of ACE2 PDF form).

Files are stored in Supabase Storage for persistence and scalability.
"""

import os
from pathlib import Path
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attachment, MentorshipLog, User, UserRole
from app.schemas import AttachmentResponse
from app.dependencies import get_current_user
from app.storage import storage_service


router = APIRouter(prefix="/api/attachments", tags=["attachments"])


# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif",  # Images
    ".pdf", ".doc", ".docx",  # Documents
    ".xls", ".xlsx",  # Spreadsheets
    ".ppt", ".pptx",  # Presentations
    ".zip", ".rar"  # Archives
}


def check_file_permissions(current_user: User, mentorship_log: MentorshipLog) -> None:
    """
    Check if user has permission to manage attachments for this log.

    Rules:
    - Admins and supervisors can manage all attachments
    - Mentors can only manage attachments for their own logs
    """
    if current_user.role in [UserRole.admin, UserRole.supervisor]:
        return

    if current_user.role == UserRole.mentor:
        if mentorship_log.mentor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage attachments for your own logs"
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


@router.post("/upload/{mentorship_log_id}", response_model=List[AttachmentResponse], status_code=status.HTTP_201_CREATED)
async def upload_attachments(
    mentorship_log_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload one or more files as attachments to a mentorship log.

    Permissions:
    - Admins and supervisors can upload to any log
    - Mentors can only upload to their own logs

    Validations:
    - Max file size: 10MB
    - Allowed formats: images, PDFs, Office documents, archives
    """
    # Get mentorship log
    mentorship_log = db.query(MentorshipLog).filter(
        MentorshipLog.id == mentorship_log_id
    ).first()

    if not mentorship_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Check permissions
    check_file_permissions(current_user, mentorship_log)

    uploaded_attachments = []

    for file in files:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file content and check size
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )

        # Upload to Supabase Storage (preserves original filename)
        try:
            storage_path = storage_service.upload_file(
                file_content=content,
                file_name=file.filename,  # Preserve original filename
                mentorship_log_id=mentorship_log_id,
                content_type=file.content_type or "application/octet-stream"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

        # Create attachment record with storage path
        attachment = Attachment(
            mentorship_log_id=mentorship_log_id,
            file_name=file.filename,  # Store original filename
            file_path=storage_path,  # Store Supabase Storage path
            file_size=file_size,
            file_type=file.content_type,
            uploaded_by=current_user.id
        )

        db.add(attachment)
        uploaded_attachments.append(attachment)

    db.commit()

    # Refresh all attachments
    for attachment in uploaded_attachments:
        db.refresh(attachment)

    return uploaded_attachments


@router.get("/{mentorship_log_id}", response_model=List[AttachmentResponse])
def list_attachments(
    mentorship_log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all attachments for a mentorship log.

    Authenticated users can view attachments.
    """
    # Verify log exists
    mentorship_log = db.query(MentorshipLog).filter(
        MentorshipLog.id == mentorship_log_id
    ).first()

    if not mentorship_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship log not found"
        )

    # Get attachments
    attachments = db.query(Attachment).filter(
        Attachment.mentorship_log_id == mentorship_log_id
    ).all()

    return attachments


@router.get("/download/{attachment_id}")
def download_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download an attachment file from Supabase Storage.

    Returns the file content with appropriate headers.
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    try:
        # Download file from Supabase Storage
        file_content = storage_service.download_file(attachment.file_path)

        # Return file with appropriate headers
        return Response(
            content=file_content,
            media_type=attachment.file_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{attachment.file_name}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found in storage: {str(e)}"
        )


@router.get("/url/{attachment_id}")
def get_attachment_url(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the public URL for an attachment file.

    This is useful for displaying images or embedding files.
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    try:
        public_url = storage_service.get_public_url(attachment.file_path)
        return {"url": public_url, "filename": attachment.file_name}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file URL: {str(e)}"
        )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an attachment.

    Permissions:
    - Admins and supervisors can delete any attachment
    - Mentors can only delete attachments from their own logs
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # Get mentorship log for permission check
    mentorship_log = db.query(MentorshipLog).filter(
        MentorshipLog.id == attachment.mentorship_log_id
    ).first()

    # Check permissions
    check_file_permissions(current_user, mentorship_log)

    # Delete file from Supabase Storage
    try:
        storage_service.delete_file(attachment.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete file from storage: {str(e)}")

    # Delete database record
    db.delete(attachment)
    db.commit()

    return None
