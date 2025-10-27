"""
Input validation schemas and sanitization utilities
"""
import re
from typing import Dict, Any, Optional, List
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """
    Centralized input validation and sanitization
    """
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate and normalize email address
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        try:
            # Use email-validator library for comprehensive validation
            valid = validate_email(email, check_deliverability=False)
            return valid.email
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> str:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            
        Returns:
            Password if valid
            
        Raises:
            ValidationError: If password is invalid
        """
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required")
        
        if len(password) < min_length:
            raise ValidationError(f"Password must be at least {min_length} characters")
        
        # Check for at least one letter and one number
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError("Password must contain at least one letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number")
        
        return password
    
    @staticmethod
    def validate_username(username: str) -> str:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Sanitized username
            
        Raises:
            ValidationError: If username is invalid
        """
        if not username or not isinstance(username, str):
            raise ValidationError("Username is required")
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if len(username) > 30:
            raise ValidationError("Username must be at most 30 characters")
        
        if not InputValidator.USERNAME_PATTERN.match(username):
            raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")
        
        return username
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """
        Validate phone number
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Sanitized phone number
            
        Raises:
            ValidationError: If phone is invalid
        """
        if not phone or not isinstance(phone, str):
            raise ValidationError("Phone number is required")
        
        # Remove common separators
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not phone.startswith('+'):
            # Assume it needs country code
            raise ValidationError("Phone number must include country code (e.g., +1234567890)")
        
        if not InputValidator.PHONE_PATTERN.match(phone):
            raise ValidationError("Invalid phone number format")
        
        return phone
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If text is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        
        # Strip whitespace
        text = text.strip()
        
        # Check length
        if len(text) > max_length:
            raise ValidationError(f"Text exceeds maximum length of {max_length} characters")
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text
    
    @staticmethod
    def validate_object_id(obj_id: str) -> str:
        """
        Validate MongoDB ObjectId format
        
        Args:
            obj_id: ObjectId string to validate
            
        Returns:
            ObjectId string if valid
            
        Raises:
            ValidationError: If ObjectId is invalid
        """
        if not obj_id or not isinstance(obj_id, str):
            raise ValidationError("ObjectId is required")
        
        # MongoDB ObjectId is 24 hex characters
        if not re.match(r'^[a-f0-9]{24}$', obj_id):
            raise ValidationError("Invalid ObjectId format")
        
        return obj_id
    
    @staticmethod
    def validate_enum(value: str, allowed_values: List[str], field_name: str = "Value") -> str:
        """
        Validate that value is in allowed list
        
        Args:
            value: Value to validate
            allowed_values: List of allowed values
            field_name: Name of field for error message
            
        Returns:
            Value if valid
            
        Raises:
            ValidationError: If value not in allowed list
        """
        if value not in allowed_values:
            raise ValidationError(
                f"{field_name} must be one of: {', '.join(allowed_values)}"
            )
        
        return value
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> str:
        """
        Validate file extension
        
        Args:
            filename: Filename to validate
            allowed_extensions: Set of allowed extensions (without dot)
            
        Returns:
            Filename if valid
            
        Raises:
            ValidationError: If extension not allowed
        """
        if not filename or not isinstance(filename, str):
            raise ValidationError("Filename is required")
        
        if '.' not in filename:
            raise ValidationError("File must have an extension")
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension not in allowed_extensions:
            raise ValidationError(
                f"File extension '.{extension}' not allowed. "
                f"Allowed: {', '.join(allowed_extensions)}"
            )
        
        return filename
    
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            URL if valid
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL is required")
        
        url = url.strip()
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(url):
            raise ValidationError("Invalid URL format")
        
        return url

class LoginValidator:
    """Validator for login requests"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate login request data
        
        Args:
            data: Request data dictionary
            
        Returns:
            Validated and sanitized data
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Invalid request data")
        
        email = InputValidator.validate_email(data.get('email', ''))
        password = data.get('password', '')
        
        if not password:
            raise ValidationError("Password is required")
        
        return {
            'email': email,
            'password': password
        }

class RegistrationValidator:
    """Validator for registration requests"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate registration request data
        
        Args:
            data: Request data dictionary
            
        Returns:
            Validated and sanitized data
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Invalid request data")
        
        username = InputValidator.validate_username(data.get('username', ''))
        email = InputValidator.validate_email(data.get('email', ''))
        password = InputValidator.validate_password(data.get('password', ''))
        confirm_password = data.get('confirmPassword', '')
        
        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        return {
            'username': username,
            'email': email,
            'password': password
        }

class ClientValidator:
    """Validator for client data"""
    
    @staticmethod
    def validate_create(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate client creation data
        
        Args:
            data: Client data dictionary
            
        Returns:
            Validated and sanitized data
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Invalid request data")
        
        validated = {}
        
        # Required fields
        validated['user_name'] = InputValidator.sanitize_string(
            data.get('user_name', ''), max_length=100
        )
        validated['email'] = InputValidator.validate_email(data.get('email', ''))
        validated['mobile_number'] = InputValidator.validate_phone(data.get('mobile_number', ''))
        validated['business_name'] = InputValidator.sanitize_string(
            data.get('business_name', ''), max_length=200
        )
        
        # Optional fields
        if 'district' in data:
            validated['district'] = InputValidator.sanitize_string(
                data['district'], max_length=100
            )
        
        if 'website' in data and data['website']:
            validated['website'] = InputValidator.validate_url(data['website'])
        
        return validated

# Convenience functions
def validate_login(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate login data"""
    return LoginValidator.validate(data)

def validate_registration(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate registration data"""
    return RegistrationValidator.validate(data)

def validate_client_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate client data"""
    return ClientValidator.validate_create(data)
