"""
Supabase Storage Service

Handles file uploads, downloads, and deletions using Supabase Storage.
"""

import os
from typing import BinaryIO
from uuid import UUID
from supabase import create_client, Client
from pathlib import Path

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key for admin operations
STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "mentorship-attachments")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class StorageService:
    """Service for managing files in Supabase Storage"""

    @staticmethod
    def upload_file(
        file_content: bytes,
        file_name: str,
        mentorship_log_id: UUID,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a file to Supabase Storage.

        Args:
            file_content: Binary content of the file
            file_name: Original filename (will be preserved)
            mentorship_log_id: ID of the mentorship log
            content_type: MIME type of the file

        Returns:
            str: Storage path of the uploaded file
        """
        # Create folder structure: mentorship-logs/{log_id}/{original_filename}
        storage_path = f"mentorship-logs/{mentorship_log_id}/{file_name}"

        try:
            # Upload file to Supabase Storage
            response = supabase.storage.from_(STORAGE_BUCKET).upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "true"  # Allow overwriting if file exists
                }
            )

            return storage_path

        except Exception as e:
            raise Exception(f"Failed to upload file to storage: {str(e)}")

    @staticmethod
    def get_public_url(storage_path: str) -> str:
        """
        Get the public URL for a file in storage.

        Args:
            storage_path: Path to the file in storage

        Returns:
            str: Public URL to access the file
        """
        try:
            response = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
            return response
        except Exception as e:
            raise Exception(f"Failed to get public URL: {str(e)}")

    @staticmethod
    def download_file(storage_path: str) -> bytes:
        """
        Download a file from Supabase Storage.

        Args:
            storage_path: Path to the file in storage

        Returns:
            bytes: File content
        """
        try:
            response = supabase.storage.from_(STORAGE_BUCKET).download(storage_path)
            return response
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")

    @staticmethod
    def delete_file(storage_path: str) -> None:
        """
        Delete a file from Supabase Storage.

        Args:
            storage_path: Path to the file in storage
        """
        try:
            supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    @staticmethod
    def create_bucket_if_not_exists() -> None:
        """
        Create the storage bucket if it doesn't exist.
        This should be called during application startup.
        """
        try:
            # Try to get bucket info
            buckets = supabase.storage.list_buckets()
            bucket_exists = any(bucket.name == STORAGE_BUCKET for bucket in buckets)

            if not bucket_exists:
                # Create bucket with public access
                supabase.storage.create_bucket(
                    STORAGE_BUCKET,
                    options={"public": True}  # Make bucket public for easy file access
                )
                print(f"✅ Created storage bucket: {STORAGE_BUCKET}")
            else:
                print(f"✅ Storage bucket already exists: {STORAGE_BUCKET}")

        except Exception as e:
            print(f"⚠️  Could not create/verify storage bucket: {str(e)}")
            # Don't raise - bucket might exist but we don't have permission to list


# Create singleton instance
storage_service = StorageService()
