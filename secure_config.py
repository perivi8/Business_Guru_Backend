"""
Secure configuration for Flask application
Implements security best practices
"""
import os
import secrets
from datetime import timedelta

class SecureConfig:
    """Security-hardened configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("FLASK_SECRET_KEY environment variable is required")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable is required for production")
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)  # 1 hour for better security
    JWT_ALGORITHM = 'HS256'
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # Security Headers (Flask-Talisman)
    TALISMAN_CONFIG = {
        'force_https': os.getenv('FLASK_ENV') == 'production',
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,  # 1 year
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': "'self'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data: https:",
            'font-src': "'self'",
            'connect-src': "'self'",
            'frame-ancestors': "'none'"
        },
        'content_security_policy_nonce_in': ['script-src'],
        'feature_policy': {
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'"
        }
    }
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Rate limits for different endpoints
    RATE_LIMITS = {
        'default': '200 per day, 50 per hour',
        'login': '5 per minute',
        'register': '3 per hour',
        'forgot_password': '3 per hour',
        'api': '100 per hour'
    }
    
    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:4200',
        'http://localhost:4201',
        'https://business-guru-vert.vercel.app'
    ]
    
    # Add additional origins from environment
    additional_origins = os.getenv('ADDITIONAL_CORS_ORIGINS', '')
    if additional_origins:
        CORS_ORIGINS.extend(additional_origins.split(','))
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable is required")
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Session Configuration
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Debug Configuration
    DEBUG = os.getenv('FLASK_ENV') != 'production'
    TESTING = False
    
    # Logging Configuration
    LOG_LEVEL = 'INFO' if os.getenv('FLASK_ENV') == 'production' else 'DEBUG'
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = [
            'MONGODB_URI',
            'JWT_SECRET_KEY',
            'FLASK_SECRET_KEY'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    @staticmethod
    def generate_secret_key():
        """Generate a cryptographically secure secret key"""
        return secrets.token_hex(32)  # 256-bit secret

def get_allowed_origins():
    """Get list of allowed CORS origins"""
    return SecureConfig.CORS_ORIGINS

def is_production():
    """Check if running in production mode"""
    return os.getenv('FLASK_ENV') == 'production'
