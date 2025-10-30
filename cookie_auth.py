"""
HttpOnly Cookie Authentication Module
Secure JWT token management using HttpOnly cookies
"""
from flask import make_response, request
from datetime import timedelta
import os

class CookieAuth:
    """
    Handles secure cookie-based authentication
    """
    
    # Cookie configuration
    COOKIE_NAME = 'access_token'
    COOKIE_HTTPONLY = True
    COOKIE_SECURE = True  # HTTPS only in production
    COOKIE_SAMESITE = 'None'  # Required for cross-origin (Vercel -> Render)
    COOKIE_MAX_AGE = 7200  # 2 hours in seconds
    COOKIE_PATH = '/'
    
    @staticmethod
    def is_production():
        """Check if running in production environment"""
        return os.getenv('FLASK_ENV') == 'production'
    
    @staticmethod
    def set_auth_cookie(response, token):
        """
        Set JWT token in HttpOnly cookie
        
        Args:
            response: Flask response object
            token: JWT token string
            
        Returns:
            Modified response with cookie set
        """
        response.set_cookie(
            CookieAuth.COOKIE_NAME,
            value=token,
            httponly=CookieAuth.COOKIE_HTTPONLY,
            secure=CookieAuth.is_production(),  # HTTPS only in production
            samesite=CookieAuth.COOKIE_SAMESITE,
            max_age=CookieAuth.COOKIE_MAX_AGE,
            path=CookieAuth.COOKIE_PATH
        )
        return response
    
    @staticmethod
    def clear_auth_cookie(response):
        """
        Clear authentication cookie (logout)
        
        Args:
            response: Flask response object
            
        Returns:
            Modified response with cookie cleared
        """
        response.set_cookie(
            CookieAuth.COOKIE_NAME,
            value='',
            httponly=CookieAuth.COOKIE_HTTPONLY,
            secure=CookieAuth.is_production(),
            samesite=CookieAuth.COOKIE_SAMESITE,
            max_age=0,
            path=CookieAuth.COOKIE_PATH
        )
        return response
    
    @staticmethod
    def get_token_from_cookie():
        """
        Extract JWT token from cookie
        
        Returns:
            Token string or None
        """
        return request.cookies.get(CookieAuth.COOKIE_NAME)
    
    @staticmethod
    def get_token_from_request():
        """
        Get token from cookie or Authorization header (fallback)
        
        Returns:
            Token string or None
        """
        # Try cookie first (preferred)
        token = CookieAuth.get_token_from_cookie()
        if token:
            return token
        
        # Fallback to Authorization header for backward compatibility
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        
        return None
