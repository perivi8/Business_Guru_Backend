"""
Secure file upload handling with validation and sanitization
"""
import os
import magic
import hashlib
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
from secure_logger import secure_logger

class FileSecurityError(Exception):
    """Custom file security error"""
    pass

class SecureFileHandler:
    """
    Secure file upload handler with comprehensive validation
    """
    
    # Allowed file extensions and their MIME types
    ALLOWED_FILES = {
        'pdf': ['application/pdf'],
        'png': ['image/png'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'gif': ['image/gif'],
        'doc': ['application/msword'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB for images
    
    # Dangerous file patterns
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js',
        'jar', 'zip', 'rar', '7z', 'tar', 'gz', 'sh', 'php',
        'asp', 'aspx', 'jsp', 'py', 'rb', 'pl'
    }
    
    def __init__(self, upload_folder: str):
        """
        Initialize secure file handler
        
        Args:
            upload_folder: Directory for file uploads
        """
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def validate_file(self, file, filename: str) -> Tuple[bool, str]:
        """
        Comprehensive file validation
        
        Args:
            file: File object from request
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file:
                return False, "No file provided"
            
            # Check filename
            if not filename:
                return False, "No filename provided"
            
            # Check for dangerous extensions
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if extension in self.DANGEROUS_EXTENSIONS:
                secure_logger.warning(f"Dangerous file extension blocked: {extension}")
                return False, f"File type '.{extension}' is not allowed for security reasons"
            
            # Check if extension is allowed
            if extension not in self.ALLOWED_FILES:
                return False, f"File type '.{extension}' is not allowed"
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > self.MAX_FILE_SIZE:
                return False, f"File size exceeds maximum of {self.MAX_FILE_SIZE / (1024*1024)}MB"
            
            # Additional size check for images
            if extension in ['png', 'jpg', 'jpeg', 'gif']:
                if file_size > self.MAX_IMAGE_SIZE:
                    return False, f"Image size exceeds maximum of {self.MAX_IMAGE_SIZE / (1024*1024)}MB"
            
            # Verify MIME type matches extension
            mime_type = self._get_mime_type(file)
            file.seek(0)  # Reset file pointer
            
            if mime_type not in self.ALLOWED_FILES[extension]:
                secure_logger.warning(
                    f"MIME type mismatch: extension={extension}, mime={mime_type}"
                )
                return False, "File type does not match its extension"
            
            # Check for null bytes (potential attack)
            file_content = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset file pointer
            
            if b'\x00' in file_content:
                secure_logger.warning("Null byte detected in file")
                return False, "Invalid file content detected"
            
            return True, "File is valid"
            
        except Exception as e:
            secure_logger.error(f"File validation error: {str(e)}")
            return False, "File validation failed"
    
    def _get_mime_type(self, file) -> str:
        """
        Get MIME type of file using python-magic
        
        Args:
            file: File object
            
        Returns:
            MIME type string
        """
        try:
            # Read first 2048 bytes for magic number detection
            file_start = file.read(2048)
            file.seek(0)
            
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file_start)
            
            return mime_type
        except Exception as e:
            secure_logger.error(f"MIME type detection error: {str(e)}")
            return "application/octet-stream"
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Use werkzeug's secure_filename
        safe_name = secure_filename(filename)
        
        # Add timestamp to prevent overwrites
        name, ext = os.path.splitext(safe_name)
        timestamp = hashlib.md5(str(os.urandom(16)).encode()).hexdigest()[:8]
        
        return f"{name}_{timestamp}{ext}"
    
    def save_file(self, file, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate and save file securely
        
        Args:
            file: File object from request
            filename: Original filename
            
        Returns:
            Tuple of (success, message, saved_filename)
        """
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(file, filename)
            if not is_valid:
                return False, error_msg, None
            
            # Sanitize filename
            safe_filename = self.sanitize_filename(filename)
            
            # Save file
            file_path = os.path.join(self.upload_folder, safe_filename)
            file.save(file_path)
            
            # Verify file was saved correctly
            if not os.path.exists(file_path):
                return False, "File save failed", None
            
            # Verify file size matches
            saved_size = os.path.getsize(file_path)
            file.seek(0, os.SEEK_END)
            original_size = file.tell()
            
            if saved_size != original_size:
                os.remove(file_path)
                return False, "File integrity check failed", None
            
            secure_logger.info(f"File saved securely: {safe_filename}")
            return True, "File uploaded successfully", safe_filename
            
        except Exception as e:
            secure_logger.error(f"File save error: {str(e)}")
            return False, "File upload failed", None
    
    def delete_file(self, filename: str) -> bool:
        """
        Safely delete a file
        
        Args:
            filename: Filename to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Sanitize filename to prevent path traversal
            safe_filename = secure_filename(filename)
            file_path = os.path.join(self.upload_folder, safe_filename)
            
            # Check file exists and is within upload folder
            if not os.path.exists(file_path):
                return False
            
            # Verify path is within upload folder (prevent path traversal)
            real_path = os.path.realpath(file_path)
            real_upload = os.path.realpath(self.upload_folder)
            
            if not real_path.startswith(real_upload):
                secure_logger.warning(f"Path traversal attempt detected: {filename}")
                return False
            
            os.remove(file_path)
            secure_logger.info(f"File deleted: {safe_filename}")
            return True
            
        except Exception as e:
            secure_logger.error(f"File deletion error: {str(e)}")
            return False
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """
        Get information about an uploaded file
        
        Args:
            filename: Filename to check
            
        Returns:
            Dictionary with file info or None
        """
        try:
            safe_filename = secure_filename(filename)
            file_path = os.path.join(self.upload_folder, safe_filename)
            
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'filename': safe_filename,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
            
        except Exception as e:
            secure_logger.error(f"File info error: {str(e)}")
            return None

# Global instance
secure_file_handler = SecureFileHandler(
    upload_folder=os.getenv('UPLOAD_FOLDER', 'uploads')
)
