"""
File upload validation and handling utilities for DataCure.
Ensures secure file uploads with proper validation and scanning.
"""
import os
import mimetypes
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import logging

logger = logging.getLogger(__name__)


class FileUploadValidator:
    """
    Validates file uploads for security and compliance.
    """
    
    # Allowed extensions by category
    ALLOWED_EXTENSIONS = {
        'documents': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'},
        'images': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'},
        'medical': {'dcm', 'dicom', 'nifti', 'nii'},
        'archives': {'zip', 'rar', '7z', 'tar', 'gz'}
    }
    
    # Default allowed extensions
    DEFAULT_ALLOWED = {'pdf', 'jpg', 'jpeg', 'png', 'dcm', 'xls', 'xlsx', 'doc', 'docx'}
    
    # File size limits (in bytes)
    FILE_SIZE_LIMITS = {
        'default': 50 * 1024 * 1024,  # 50 MB
        'image': 10 * 1024 * 1024,    # 10 MB
        'document': 25 * 1024 * 1024,  # 25 MB
        'medical': 100 * 1024 * 1024   # 100 MB
    }
    
    # MIME type whitelist
    ALLOWED_MIMETYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/plain',
        'application/dicom',
        'application/x-nifti',
        'application/zip'
    }
    
    @classmethod
    def validate_file(cls, file_obj, allowed_extensions=None, category=None, max_size=None):
        """
        Validate uploaded file.
        
        Args:
            file_obj: FileStorage object from Flask
            allowed_extensions: Set of allowed extensions (overrides default)
            category: File category for size limits ('image', 'document', 'medical')
            max_size: Maximum file size in bytes (overrides default)
        
        Returns:
            (is_valid, error_message)
        """
        errors = []
        
        # 1. Check if file exists
        if not file_obj or file_obj.filename == '':
            return False, 'No file selected'
        
        # 2. Get filename and extension
        filename = secure_filename(file_obj.filename)
        if not filename:
            return False, 'Invalid filename'
        
        file_ext = cls._get_extension(filename).lower()
        
        # 3. Validate extension
        if allowed_extensions is None:
            allowed_extensions = cls.DEFAULT_ALLOWED
        
        if file_ext not in allowed_extensions:
            return False, f'File type .{file_ext} not allowed. Allowed types: {", ".join(allowed_extensions)}'
        
        # 4. Check file size
        file_size = len(file_obj.read())
        file_obj.seek(0)  # Reset file pointer
        
        if max_size is None:
            max_size = cls.FILE_SIZE_LIMITS.get(category or 'default', cls.FILE_SIZE_LIMITS['default'])
        
        if file_size == 0:
            return False, 'File is empty'
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f'File size exceeds {max_mb:.1f} MB limit'
        
        # 5. Validate MIME type
        mime_type = cls._get_mimetype(filename)
        if mime_type not in cls.ALLOWED_MIMETYPES:
            errors.append(f'MIME type {mime_type} not allowed')
        
        # 6. Scan for malicious content (basic checks)
        errors.extend(cls._scan_for_malicious_content(file_obj, file_ext))
        
        if errors:
            return False, '; '.join(errors)
        
        return True, None
    
    @classmethod
    def sanitize_filename(cls, filename, max_length=255):
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
        
        Returns:
            Sanitized filename
        """
        # Use werkzeug's secure_filename
        safe_name = secure_filename(filename)
        
        if not safe_name:
            safe_name = 'upload'
        
        # Limit length
        if len(safe_name) > max_length:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:max_length - len(ext) - 1] + ext
        
        return safe_name
    
    @classmethod
    def _get_extension(cls, filename):
        """
        Get file extension safely.
        """
        if '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()
    
    @classmethod
    def _get_mimetype(cls, filename):
        """
        Get MIME type of file.
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @classmethod
    def _scan_for_malicious_content(cls, file_obj, file_ext):
        """
        Basic scan for malicious content.
        For production, integrate with antivirus API (ClamAV, etc.)
        """
        errors = []
        
        # Read file content
        file_obj.seek(0)
        content = file_obj.read(1024)  # Read first 1KB
        file_obj.seek(0)
        
        # Check for null bytes (common in malicious files)
        if b'\x00' in content and file_ext not in {'dcm', 'nifti', 'nii'}:
            errors.append('File contains suspicious content (null bytes)')
        
        # Check for executable patterns in documents
        if file_ext in {'pdf', 'doc', 'docx'}:
            if b'javascript' in content.lower() or b'activex' in content.lower():
                errors.append('File contains potentially malicious scripts')
        
        return errors


class FileUploadManager:
    """
    Manages file uploads, storage, and cleanup.
    """
    
    def __init__(self, upload_folder):
        """
        Initialize file upload manager.
        
        Args:
            upload_folder: Path to upload folder
        """
        self.upload_folder = upload_folder
        self._ensure_upload_folder()
    
    def _ensure_upload_folder(self):
        """
        Ensure upload folder exists.
        """
        Path(self.upload_folder).mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_obj, subfolder='', allowed_extensions=None):
        """
        Save uploaded file securely.
        
        Args:
            file_obj: FileStorage object
            subfolder: Subfolder within upload_folder
            allowed_extensions: Allowed file extensions
        
        Returns:
            (is_success, filepath, error_message)
        """
        # Validate file
        is_valid, error_msg = FileUploadValidator.validate_file(
            file_obj,
            allowed_extensions=allowed_extensions
        )
        
        if not is_valid:
            return False, None, error_msg
        
        try:
            # Sanitize filename
            filename = FileUploadValidator.sanitize_filename(file_obj.filename)
            
            # Create subfolder if provided
            if subfolder:
                subfolder_path = os.path.join(self.upload_folder, subfolder)
                Path(subfolder_path).mkdir(parents=True, exist_ok=True)
                filepath = os.path.join(subfolder_path, filename)
            else:
                filepath = os.path.join(self.upload_folder, filename)
            
            # Avoid overwriting existing files
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    new_filename = f"{name}_{counter}{ext}"
                    if subfolder:
                        filepath = os.path.join(self.upload_folder, subfolder, new_filename)
                    else:
                        filepath = os.path.join(self.upload_folder, new_filename)
                    counter += 1
            
            # Save file
            file_obj.save(filepath)
            logger.info(f"File uploaded successfully: {filepath}")
            
            return True, filepath, None
        
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return False, None, f'Error saving file: {str(e)}'
    
    def delete_file(self, filepath):
        """
        Delete uploaded file.
        
        Args:
            filepath: Path to file
        
        Returns:
            (is_success, error_message)
        """
        try:
            # Verify file is within upload folder
            filepath = os.path.abspath(filepath)
            upload_folder = os.path.abspath(self.upload_folder)
            
            if not filepath.startswith(upload_folder):
                return False, 'Invalid file path'
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
                return True, None
            else:
                return False, 'File not found'
        
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False, str(e)
    
    def get_file_info(self, filepath):
        """
        Get file information.
        
        Args:
            filepath: Path to file
        
        Returns:
            Dictionary with file info
        """
        try:
            filepath = os.path.abspath(filepath)
            upload_folder = os.path.abspath(self.upload_folder)
            
            if not filepath.startswith(upload_folder):
                return None
            
            if not os.path.exists(filepath):
                return None
            
            stat_info = os.stat(filepath)
            
            return {
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'size': stat_info.st_size,
                'created_at': stat_info.st_ctime,
                'modified_at': stat_info.st_mtime,
                'mime_type': FileUploadValidator._get_mimetype(filepath)
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
