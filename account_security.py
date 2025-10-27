"""
Account security module for login attempt tracking and lockout
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import threading

class AccountSecurityManager:
    """
    Manages failed login attempts and account lockouts
    Thread-safe implementation for production use
    """
    
    def __init__(self, 
                 max_attempts: int = 5,
                 lockout_duration_minutes: int = 15,
                 attempt_window_minutes: int = 30):
        """
        Initialize account security manager
        
        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: How long to lock account
            attempt_window_minutes: Time window to count attempts
        """
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.attempt_window = timedelta(minutes=attempt_window_minutes)
        
        # Store failed attempts: {email: [timestamp1, timestamp2, ...]}
        self.failed_attempts: Dict[str, list] = {}
        
        # Store lockouts: {email: lockout_until_timestamp}
        self.lockouts: Dict[str, datetime] = {}
        
        # Thread lock for thread-safe operations
        self.lock = threading.Lock()
    
    def is_locked(self, email: str) -> bool:
        """
        Check if account is currently locked
        
        Args:
            email: User email address
            
        Returns:
            True if account is locked, False otherwise
        """
        with self.lock:
            if email not in self.lockouts:
                return False
            
            lockout_until = self.lockouts[email]
            
            # Check if lockout has expired
            if datetime.utcnow() >= lockout_until:
                # Lockout expired, remove it
                del self.lockouts[email]
                if email in self.failed_attempts:
                    del self.failed_attempts[email]
                return False
            
            return True
    
    def get_lockout_time_remaining(self, email: str) -> Optional[int]:
        """
        Get remaining lockout time in seconds
        
        Args:
            email: User email address
            
        Returns:
            Seconds remaining or None if not locked
        """
        with self.lock:
            if email not in self.lockouts:
                return None
            
            lockout_until = self.lockouts[email]
            remaining = (lockout_until - datetime.utcnow()).total_seconds()
            
            return max(0, int(remaining))
    
    def record_failed_attempt(self, email: str) -> Dict[str, any]:
        """
        Record a failed login attempt
        
        Args:
            email: User email address
            
        Returns:
            Dictionary with lockout status and remaining attempts
        """
        with self.lock:
            now = datetime.utcnow()
            
            # Initialize attempts list if needed
            if email not in self.failed_attempts:
                self.failed_attempts[email] = []
            
            # Add current attempt
            self.failed_attempts[email].append(now)
            
            # Remove old attempts outside the window
            cutoff_time = now - self.attempt_window
            self.failed_attempts[email] = [
                attempt for attempt in self.failed_attempts[email]
                if attempt > cutoff_time
            ]
            
            # Count recent attempts
            recent_attempts = len(self.failed_attempts[email])
            
            # Check if should lock account
            if recent_attempts >= self.max_attempts:
                lockout_until = now + self.lockout_duration
                self.lockouts[email] = lockout_until
                
                return {
                    'locked': True,
                    'attempts': recent_attempts,
                    'lockout_until': lockout_until.isoformat(),
                    'lockout_duration_minutes': self.lockout_duration.total_seconds() / 60
                }
            
            # Not locked yet
            remaining_attempts = self.max_attempts - recent_attempts
            
            return {
                'locked': False,
                'attempts': recent_attempts,
                'remaining_attempts': remaining_attempts,
                'max_attempts': self.max_attempts
            }
    
    def record_successful_login(self, email: str):
        """
        Clear failed attempts after successful login
        
        Args:
            email: User email address
        """
        with self.lock:
            if email in self.failed_attempts:
                del self.failed_attempts[email]
            if email in self.lockouts:
                del self.lockouts[email]
    
    def unlock_account(self, email: str):
        """
        Manually unlock an account (admin action)
        
        Args:
            email: User email address
        """
        with self.lock:
            if email in self.lockouts:
                del self.lockouts[email]
            if email in self.failed_attempts:
                del self.failed_attempts[email]
    
    def get_account_status(self, email: str) -> Dict[str, any]:
        """
        Get current security status for an account
        
        Args:
            email: User email address
            
        Returns:
            Dictionary with account security status
        """
        with self.lock:
            if email in self.lockouts:
                remaining = self.get_lockout_time_remaining(email)
                return {
                    'locked': True,
                    'lockout_remaining_seconds': remaining,
                    'lockout_until': self.lockouts[email].isoformat()
                }
            
            if email in self.failed_attempts:
                now = datetime.utcnow()
                cutoff_time = now - self.attempt_window
                recent_attempts = [
                    attempt for attempt in self.failed_attempts[email]
                    if attempt > cutoff_time
                ]
                
                return {
                    'locked': False,
                    'failed_attempts': len(recent_attempts),
                    'remaining_attempts': self.max_attempts - len(recent_attempts)
                }
            
            return {
                'locked': False,
                'failed_attempts': 0,
                'remaining_attempts': self.max_attempts
            }
    
    def cleanup_expired_data(self):
        """
        Clean up expired lockouts and old attempts
        Should be called periodically
        """
        with self.lock:
            now = datetime.utcnow()
            
            # Remove expired lockouts
            expired_lockouts = [
                email for email, lockout_until in self.lockouts.items()
                if now >= lockout_until
            ]
            for email in expired_lockouts:
                del self.lockouts[email]
            
            # Remove old attempts
            cutoff_time = now - self.attempt_window
            for email in list(self.failed_attempts.keys()):
                self.failed_attempts[email] = [
                    attempt for attempt in self.failed_attempts[email]
                    if attempt > cutoff_time
                ]
                
                # Remove empty lists
                if not self.failed_attempts[email]:
                    del self.failed_attempts[email]

# Global instance
account_security = AccountSecurityManager(
    max_attempts=5,
    lockout_duration_minutes=15,
    attempt_window_minutes=30
)
