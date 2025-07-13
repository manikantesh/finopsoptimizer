"""
Security enhancements for FinOpsOptimizer.
"""

import os
import logging
import hashlib
import hmac
import base64
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path

from .config import Config


class SecurityManager:
    """
    Security manager for FinOpsOptimizer.
    
    Provides encryption, key management, and security validation.
    """
    
    def __init__(self, config: Config):
        """
        Initialize SecurityManager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption key
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security settings
        self.max_login_attempts = config.security.get('max_login_attempts', 5)
        self.session_timeout = config.security.get('session_timeout', 3600)  # 1 hour
        self.password_min_length = config.security.get('password_min_length', 8)
        
        # Track login attempts
        self.login_attempts = {}
    
    def _get_or_create_key(self) -> bytes:
        """
        Get or create encryption key.
        
        Returns:
            Encryption key
        """
        key_file = Path(self.config.output_dir) / ".encryption_key"
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"Error reading encryption key: {e}")
        
        # Generate new key
        key = Fernet.generate_key()
        
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
        except Exception as e:
            self.logger.error(f"Error saving encryption key: {e}")
        
        return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """
        Hash password securely.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        try:
            salt, hash_hex = hashed_password.split('$')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # iterations
            )
            return hmac.compare_digest(hash_obj.hex(), hash_hex)
        except Exception as e:
            self.logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        # Check length
        if len(password) < self.password_min_length:
            errors.append(f"Password must be at least {self.password_min_length} characters")
        
        # Check for common patterns
        if password.lower() in ['password', '123456', 'admin']:
            errors.append("Password is too common")
        
        # Check character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not has_upper:
            warnings.append("Consider adding uppercase letters")
        if not has_lower:
            warnings.append("Consider adding lowercase letters")
        if not has_digit:
            warnings.append("Consider adding numbers")
        if not has_special:
            warnings.append("Consider adding special characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'strength_score': self._calculate_strength_score(password)
        }
    
    def _calculate_strength_score(self, password: str) -> int:
        """
        Calculate password strength score.
        
        Args:
            password: Password to score
            
        Returns:
            Strength score (0-100)
        """
        score = 0
        
        # Length bonus
        score += min(len(password) * 4, 40)
        
        # Character type bonuses
        if any(c.isupper() for c in password):
            score += 10
        if any(c.islower() for c in password):
            score += 10
        if any(c.isdigit() for c in password):
            score += 10
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 15
        
        # Entropy bonus
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 20)
        
        return min(score, 100)
    
    def check_login_attempts(self, username: str) -> Dict[str, Any]:
        """
        Check login attempts for user.
        
        Args:
            username: Username
            
        Returns:
            Login attempt status
        """
        now = datetime.now()
        
        if username not in self.login_attempts:
            return {'allowed': True, 'remaining_attempts': self.max_login_attempts}
        
        attempts = self.login_attempts[username]
        
        # Remove old attempts
        attempts = [attempt for attempt in attempts 
                   if now - attempt['timestamp'] < timedelta(minutes=15)]
        
        if len(attempts) >= self.max_login_attempts:
            return {
                'allowed': False,
                'remaining_attempts': 0,
                'lockout_until': (attempts[0]['timestamp'] + timedelta(minutes=15)).isoformat()
            }
        
        self.login_attempts[username] = attempts
        
        return {
            'allowed': True,
            'remaining_attempts': self.max_login_attempts - len(attempts)
        }
    
    def record_login_attempt(self, username: str, success: bool) -> None:
        """
        Record login attempt.
        
        Args:
            username: Username
            success: Whether login was successful
        """
        now = datetime.now()
        
        if username not in self.login_attempts:
            self.login_attempts[username] = []
        
        self.login_attempts[username].append({
            'timestamp': now,
            'success': success
        })
        
        # Keep only recent attempts
        self.login_attempts[username] = [
            attempt for attempt in self.login_attempts[username]
            if now - attempt['timestamp'] < timedelta(minutes=15)
        ]
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid
        """
        # In production, this would check against a database
        # For now, we'll use a simple hash check
        expected_key = self.config.security.get('api_key_hash')
        if not expected_key:
            return False
        
        return hmac.compare_digest(
            hashlib.sha256(api_key.encode()).hexdigest(),
            expected_key
        )
    
    def generate_api_key(self) -> str:
        """
        Generate new API key.
        
        Returns:
            New API key
        """
        return secrets.token_urlsafe(32)
    
    def sanitize_input(self, data: str) -> str:
        """
        Sanitize user input.
        
        Args:
            data: Input data
            
        Returns:
            Sanitized data
        """
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        return data.strip()
    
    def validate_json_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON payload for security.
        
        Args:
            payload: JSON payload
            
        Returns:
            Validation results
        """
        errors = []
        
        # Check for potentially dangerous keys
        dangerous_keys = ['__class__', '__dict__', '__module__', 'eval', 'exec']
        for key in payload.keys():
            if any(dk in str(key).lower() for dk in dangerous_keys):
                errors.append(f"Dangerous key found: {key}")
        
        # Check for potentially dangerous values
        for key, value in payload.items():
            if isinstance(value, str):
                if len(value) > 10000:  # Limit string length
                    errors.append(f"Value too long for key: {key}")
                if any(dk in value.lower() for dk in dangerous_keys):
                    errors.append(f"Dangerous value found for key: {key}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def audit_log(self, action: str, user: str, details: Dict[str, Any]) -> None:
        """
        Log security audit event.
        
        Args:
            action: Action performed
            user: User performing action
            details: Additional details
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'details': details,
            'ip_address': self._get_client_ip()
        }
        
        audit_file = Path(self.config.output_dir) / "audit.log"
        audit_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(audit_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Error writing audit log: {e}")
    
    def _get_client_ip(self) -> str:
        """
        Get client IP address.
        
        Returns:
            Client IP address
        """
        # This would be implemented based on your web framework
        # For now, return a placeholder
        return "127.0.0.1"
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate security report.
        
        Returns:
            Security report
        """
        return {
            'encryption_enabled': True,
            'password_policy': {
                'min_length': self.password_min_length,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True
            },
            'login_security': {
                'max_attempts': self.max_login_attempts,
                'lockout_duration': 15,  # minutes
                'session_timeout': self.session_timeout
            },
            'audit_logging': True,
            'input_sanitization': True,
            'api_key_validation': True
        }


class RateLimiter:
    """
    Rate limiter for API endpoints.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize RateLimiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            identifier: Request identifier (IP, user ID, etc.)
            
        Returns:
            True if request is allowed
        """
        now = datetime.now()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if now - timestamp < timedelta(seconds=self.window_seconds)
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get remaining requests for identifier.
        
        Args:
            identifier: Request identifier
            
        Returns:
            Number of remaining requests
        """
        now = datetime.now()
        
        if identifier not in self.requests:
            return self.max_requests
        
        # Remove old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if now - timestamp < timedelta(seconds=self.window_seconds)
        ]
        
        return max(0, self.max_requests - len(self.requests[identifier])) 