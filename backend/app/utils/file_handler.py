"""
File upload handling and validation utilities for DataCure.
Handles file validation, scanning, and storage operations.
"""
import os
import mimetypes
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from typing import Tuple, Optional, Dict
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded files for security and compliance."""

    # Secure file extensions - whitelist approach
    ALLOWED_EXTENSIONS = {
        # Documents
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',

        # Images
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',

        # Medical Images
        'dcm': 'application/dicom',

        # Archives (restricted - only for exports)
        'zip': 'application/zip',
    }

    # Maximum file sizes by type (in bytes)
    MAX_SIZES = {
        'pdf': 50 * 1024 * 1024,      # 50MB
        'doc': 25 * 1024 * 1024,      # 25MB
        'docx': 25 * 1024 * 1024,     # 25MB
        'xls': 25 * 1024 * 1024,      # 25MB
        'xlsx': 25 * 1024 * 1024,     # 25MB
        'jpg': 10 * 1024 * 1024,      # 10MB
        'jpeg': 10 * 1024 * 1024,     # 10MB
        'png': 10 * 1024 * 1024,      # 10MB
        'gif': 5 * 1024 * 1024,       # 5MB
        'dcm': 100 * 1024 * 1024,     # 100MB
        'zip': 500 * 1024 * 1024,     # 500MB
    }

    # Dangerous file patterns
    DANGEROUS_PATTERNS = [
        '.exe', '.bat', '.cmd', '.com',  # Executables
        '.ps1', '.vbs', '.js',            # Scripts
        '.sh', '.bash', '.py',             # Shell/Python
        '.app', '.jar', '.apk',            # Applications
        '.html', '.htm', '.asp', '.aspx', '.php',  # Web scripts
    ]

    @staticmethod
    def get_allowed_extensions() -> set:
        """Get set of allowed file extensions."""
        return set(FileValidator.ALLOWED_EXTENSIONS.keys())

    @staticmethod
    def validate_extension(filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension.

        Args:
            filename: Original filename from upload

        Returns:
            (is_valid, error_message)
        """
        if not filename:
            return False, 'No filename provided'

        # Get file extension
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if not file_ext:
            return False, 'File must have an extension'

        if file_ext not in FileValidator.ALLOWED_EXTENSIONS:
            allowed = ', '.join(sorted(FileValidator.ALLOWED_EXTENSIONS.keys()))
            return False, f'File type not allowed. Allowed types: {allowed}'

        return True, None

    @staticmethod
    def validate_size(file_size: int, file_ext: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file size against extension limits.

        Args:
            file_size: File size in bytes
            file_ext: File extension (without dot)

        Returns:
            (is_valid, error_message)
        """
        max_size = FileValidator.MAX_SIZES.get(file_ext.lower())

        if not max_size:
            return False, f'Unknown file type: {file_ext}'

        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f'File size exceeds limit of {max_mb:.1f}MB'

        if file_size < 100:  # Minimum 100 bytes
            return False, 'File size too small'

        return True, None

    @staticmethod
    def validate_mime_type(filename: str, file_content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate MIME type matches extension.

        Args:
            filename: Filename with extension
            file_content: First bytes of file content

        Returns:
            (is_valid, error_message)
        """
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        expected_mime = FileValidator.ALLOWED_EXTENSIONS.get(file_ext)

        if not expected_mime:
            return False, 'Unknown file type'

        # Detect MIME type from file content
        detected_mime, _ = mimetypes.guess_type(filename)

        # For binary files like PDF, DCM, check magic bytes
        if file_ext == 'pdf':
            if not file_content.startswith(b'%PDF'):
                return False, 'File is not a valid PDF'
        elif file_ext == 'dcm':
            if len(file_content) < 132 or file_content[128:132] != b'DICM':
                return False, 'File is not a valid DICOM image'
        elif file_ext in ['jpg', 'jpeg']:
            if not file_content.startswith(b'\xff\xd8\xff'):
                return False, 'File is not a valid JPEG image'
        elif file_ext == 'png':
            if not file_content.startswith(b'\x89PNG'):
                return False, 'File is not a valid PNG image'

        return True, None

    @staticmethod
    def is_safe_filename(filename: str) -> Tuple[bool, Optional[str]]:
        """
        Check if filename is safe to use on filesystem.

        Args:
            filename: Original filename

        Returns:
            (is_safe, error_message)
        """
        # Check for dangerous patterns
        filename_lower = filename.lower()
        for pattern in FileValidator.DANGEROUS_PATTERNS:
            if pattern in filename_lower:
                return False, f'Filename contains dangerous pattern: {pattern}'

        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, 'Filename contains invalid path characters'

        # Ensure it's a valid filename
        secure = secure_filename(filename)
        if not secure:
            return False, 'Filename is invalid'

        return True, None

    @classmethod
    def validate_upload(cls, filename: str, file_size: int, file_content: bytes) \
            -> Tuple[bool, Optional[str]]:
        """
        Validate complete file upload.

        Args:
            filename: Original filename
            file_size: File size in bytes
            file_content: File content bytes

        Returns:
            (is_valid, error_message)
        """
        # Validate extension
        extension_valid, ext_error = cls.validate_extension(filename)
        if not extension_valid:
            return False, ext_error

        # Validate filename safety
        filename_safe, filename_error = cls.is_safe_filename(filename)
        if not filename_safe:
            return False, filename_error

        # Get extension
        file_ext = filename.rsplit('.', 1)[1].lower()

        # Validate size
        size_valid, size_error = cls.validate_size(file_size, file_ext)
        if not size_valid:
            return False, size_error

        # Validate MIME type
        mime_valid, mime_error = cls.validate_mime_type(filename, file_content)
        if not mime_valid:
            return False, mime_error

        return True, None


class FileStorage:
    """Handles secure file storage and retrieval."""

    @staticmethod
    def get_upload_folder() -> Path:
        """Get configured upload folder path."""
        folder = current_app.config.get('UPLOAD_FOLDER', './uploads')
        return Path(folder)

    @staticmethod
    def get_safe_filename(original_filename: str, hospital_id: str, user_id: str) -> str:
        """
        Generate safe filename with hospital and user context.

        Args:
            original_filename: Original uploaded filename
            hospital_id: Hospital ID
            user_id: User ID

        Returns:
            Safe filename with timestamp and path
        """
        # Extract extension
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''

        # Create safe base filename
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])

        # Add timestamp to ensure uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        # Create filename with context
        filename = f"{hospital_id}/{user_id}/{timestamp}_{safe_name}.{ext}"

        return filename

    @staticmethod
    def save_file(file_content: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Save validated file to storage.

        Args:
            file_content: File bytes to save
            filename: Safe filename (should use get_safe_filename)

        Returns:
            (success, error_message, file_path)
        """
        try:
            upload_folder = FileStorage.get_upload_folder()
            upload_folder.mkdir(parents=True, exist_ok=True)

            # Create subdirectory structure
            file_path = upload_folder / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            logger.info(f"File saved: {file_path}")
            return True, None, str(file_path)

        except IOError as e:
            error_msg = f'Failed to save file: {str(e)}'
            logger.error(error_msg)
            return False, error_msg, None

    @staticmethod
    def delete_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from storage.

        Args:
            file_path: Full path to file

        Returns:
            (success, error_message)
        """
        try:
            path = Path(file_path)

            # Security check - ensure file is within upload folder
            upload_folder = FileStorage.get_upload_folder().resolve()
            file_path_resolved = path.resolve()

            if not str(file_path_resolved).startswith(str(upload_folder)):
                return False, 'Invalid file path'

            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True, None
            else:
                return False, 'File not found'

        except Exception as e:
            error_msg = f'Failed to delete file: {str(e)}'
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def get_file(file_path: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Retrieve file from storage.

        Args:
            file_path: Full path to file

        Returns:
            (success, file_content, error_message)
        """
        try:
            path = Path(file_path)

            # Security check - ensure file is within upload folder
            upload_folder = FileStorage.get_upload_folder().resolve()
            file_path_resolved = path.resolve()

            if not str(file_path_resolved).startswith(str(upload_folder)):
                return False, None, 'Invalid file path'

            if path.exists() and path.is_file():
                with open(path, 'rb') as f:
                    content = f.read()
                return True, content, None
            else:
                return False, None, 'File not found'

        except Exception as e:
            error_msg = f'Failed to read file: {str(e)}'
            logger.error(error_msg)
            return False, None, error_msg


class FileUploadRequest:
    """Handles file upload requests from API."""

    @staticmethod
    def process_upload(file_obj, hospital_id: str, user_id: str, \
                      file_type: str = 'document') -> Dict:
        """
        Process uploaded file with full validation.

        Args:
            file_obj: Werkzeug FileStorage object from request.files
            hospital_id: Hospital ID for organization
            user_id: User ID for audit trail
            file_type: Type of file being uploaded (for audit)

        Returns:
            Dictionary with status and results
        """
        try:
            if not file_obj or not file_obj.filename:
                return {
                    'success': False,
                    'error': 'No file provided'
                }

            filename = file_obj.filename
            file_content = file_obj.read()
            file_size = len(file_content)

            # Validate upload
            is_valid, error_msg = FileValidator.validate_upload(
                filename=filename,
                file_size=file_size,
                file_content=file_content
            )

            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg
                }

            # Generate safe filename
            safe_filename = FileStorage.get_safe_filename(
                filename,
                hospital_id,
                user_id
            )

            # Save file
            success, save_error, file_path = FileStorage.save_file(
                file_content=file_content,
                filename=safe_filename
            )

            if not success:
                return {
                    'success': False,
                    'error': save_error
                }

            return {
                'success': True,
                'file_path': file_path,
                'filename': safe_filename,
                'original_filename': secure_filename(filename),
                'file_size': file_size,
                'file_type': file_type,
                'upload_timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            error_msg = f'File upload processing error: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
