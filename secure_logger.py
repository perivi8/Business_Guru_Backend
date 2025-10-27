"""
Secure logging service for production use.
Prevents logging of sensitive data like tokens, passwords, and secrets.
"""
import logging
import os
import sys
from datetime import datetime
import json

class SecureLogger:
    """
    Production-safe logger that filters sensitive data
    """
    
    # Sensitive keywords to filter from logs
    SENSITIVE_KEYWORDS = [
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'bearer', 'jwt', 'credential',
        'mongodb_uri', 'smtp_password', 'private_key'
    ]
    
    def __init__(self, name='tmis-backend', log_level=None):
        """
        Initialize secure logger
        
        Args:
            name: Logger name
            log_level: Logging level (defaults to INFO in production, DEBUG in development)
        """
        self.logger = logging.getLogger(name)
        
        # Set log level based on environment
        if log_level is None:
            flask_env = os.getenv('FLASK_ENV', 'development')
            log_level = logging.INFO if flask_env == 'production' else logging.DEBUG
        
        self.logger.setLevel(log_level)
        
        # Create console handler with formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            
            # JSON formatter for structured logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.is_production = os.getenv('FLASK_ENV') == 'production'
    
    def _sanitize_message(self, message, *args):
        """
        Remove sensitive data from log messages
        
        Args:
            message: Log message
            args: Additional arguments
            
        Returns:
            Sanitized message string
        """
        # Convert message to string
        msg_str = str(message)
        
        # In production, redact sensitive information
        if self.is_production:
            msg_lower = msg_str.lower()
            for keyword in self.SENSITIVE_KEYWORDS:
                if keyword in msg_lower:
                    # Find and redact the value after the keyword
                    msg_str = msg_str.replace(msg_str, '[REDACTED - Contains sensitive data]')
                    break
        
        # Handle additional arguments
        if args:
            try:
                msg_str = msg_str % args
            except (TypeError, ValueError):
                # If formatting fails, just append args
                msg_str = f"{msg_str} {args}"
        
        return msg_str
    
    def debug(self, message, *args, **kwargs):
        """Log debug message (only in development)"""
        if not self.is_production:
            sanitized = self._sanitize_message(message, *args)
            self.logger.debug(sanitized, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log info message"""
        sanitized = self._sanitize_message(message, *args)
        self.logger.info(sanitized, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning message"""
        sanitized = self._sanitize_message(message, *args)
        self.logger.warning(sanitized, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log error message"""
        sanitized = self._sanitize_message(message, *args)
        self.logger.error(sanitized, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log critical message"""
        sanitized = self._sanitize_message(message, *args)
        self.logger.critical(sanitized, **kwargs)
    
    def security_event(self, event_type, details=None):
        """
        Log security-related events
        
        Args:
            event_type: Type of security event (e.g., 'failed_login', 'unauthorized_access')
            details: Additional details (will be sanitized)
        """
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details if details else {}
        }
        
        # Remove sensitive data from details
        if isinstance(details, dict):
            for key in list(event_data['details'].keys()):
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYWORDS):
                    event_data['details'][key] = '[REDACTED]'
        
        self.warning(f"SECURITY_EVENT: {json.dumps(event_data)}")

# Global logger instance
secure_logger = SecureLogger()

# Convenience functions
def debug(message, *args, **kwargs):
    secure_logger.debug(message, *args, **kwargs)

def info(message, *args, **kwargs):
    secure_logger.info(message, *args, **kwargs)

def warning(message, *args, **kwargs):
    secure_logger.warning(message, *args, **kwargs)

def error(message, *args, **kwargs):
    secure_logger.error(message, *args, **kwargs)

def critical(message, *args, **kwargs):
    secure_logger.critical(message, *args, **kwargs)

def security_event(event_type, details=None):
    secure_logger.security_event(event_type, details)
