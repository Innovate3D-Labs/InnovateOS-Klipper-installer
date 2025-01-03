from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, List
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)
RATE_LIMIT_GENERAL = "100/minute"
RATE_LIMIT_AUTH = "5/minute"
RATE_LIMIT_INSTALL = "3/minute"

# API Key configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class SecurityConfig:
    def __init__(self):
        self.allowed_origins: List[str] = [
            "http://localhost:3000",
            "https://innovateos.dev"
        ]
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = ["*"]
        self.allow_credentials = True
        self.max_age = 600

    def get_cors_middleware(self):
        return CORSMiddleware(
            allow_origins=self.allowed_origins,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            allow_credentials=self.allow_credentials,
            max_age=self.max_age
        )

class InputValidator:
    @staticmethod
    def validate_port(port: str) -> bool:
        """Validate serial port name"""
        if not port:
            return False
        # Windows: COM1, COM2, etc.
        # Linux: /dev/ttyUSB0, /dev/ttyACM0, etc.
        port_pattern = r'^(COM\d+|/dev/tty(USB|ACM|S)\d+)$'
        return bool(re.match(port_pattern, port))

    @staticmethod
    def validate_firmware_version(version: str) -> bool:
        """Validate firmware version string"""
        if not version:
            return False
        # Format: v1.2.3 or master
        version_pattern = r'^(v\d+\.\d+\.\d+|master)$'
        return bool(re.match(version_pattern, version))

    @staticmethod
    def sanitize_printer_name(name: str) -> str:
        """Sanitize printer name to prevent path traversal"""
        # Remove any characters that could be used for path traversal
        return re.sub(r'[^\w\s-]', '', name)

    @staticmethod
    def validate_config_values(config: dict) -> List[str]:
        """Validate printer configuration values"""
        errors = []
        
        # Validate dimensions
        for axis in ['x', 'y', 'z']:
            if config.get('bed_size', {}).get(axis, 0) <= 0:
                errors.append(f"Invalid {axis} dimension")

        # Validate speeds and accelerations
        if config.get('max_velocity', 0) <= 0:
            errors.append("Invalid max velocity")
        if config.get('max_accel', 0) <= 0:
            errors.append("Invalid max acceleration")

        return errors

class SecurityMiddleware:
    def __init__(self):
        self.blocked_ips: dict = {}
        self.failed_attempts: dict = {}
        self.block_duration = timedelta(minutes=15)
        self.max_failed_attempts = 5

    async def check_ip(self, request: Request):
        """Check if IP is blocked"""
        client_ip = request.client.host
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[client_ip]:
                raise HTTPException(
                    status_code=403,
                    detail="IP temporarily blocked due to suspicious activity"
                )
            else:
                del self.blocked_ips[client_ip]
                if client_ip in self.failed_attempts:
                    del self.failed_attempts[client_ip]

    async def record_failed_attempt(self, request: Request):
        """Record failed attempt and block IP if necessary"""
        client_ip = request.client.host
        
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = 1
        else:
            self.failed_attempts[client_ip] += 1
            
        if self.failed_attempts[client_ip] >= self.max_failed_attempts:
            self.blocked_ips[client_ip] = datetime.now() + self.block_duration
            logger.warning(f"IP {client_ip} blocked due to multiple failed attempts")

async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    """Verify API key if present"""
    if api_key is None:
        return None
        
    # In production, verify against secure storage
    valid_api_keys = ["test_key"]  # Replace with secure key storage
    
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return api_key

def setup_security(app):
    """Configure security settings for the application"""
    security_config = SecurityConfig()
    security_middleware = SecurityMiddleware()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **security_config.__dict__
    )
    
    # Add rate limiting
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        await limiter.check_request(request)
        response = await call_next(request)
        return response
    
    # Add security checks
    @app.middleware("http")
    async def security_middleware_handler(request: Request, call_next):
        await security_middleware.check_ip(request)
        
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            if e.status_code in [401, 403]:
                await security_middleware.record_failed_attempt(request)
            raise
        
    # Configure security headers
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
