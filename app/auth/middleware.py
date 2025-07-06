"""
Authentication middleware for API key validation
"""
import hashlib
import hmac
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json
from loguru import logger

from ..config import get_settings


class APIKeyAuth(HTTPBearer):
    """API Key authentication using HTTP Bearer token"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.settings = get_settings()
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)
        if credentials:
            if not self.verify_api_key(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return credentials
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key against stored keys"""
        # In a real implementation, this would check against a database
        # For now, we'll use a simple HMAC-based verification
        try:
            # Expected format: "mcp_" + base64(hmac(secret, user_id))
            if not api_key.startswith("mcp_"):
                return False
            
            # For demo purposes, accept any properly formatted key
            # In production, implement proper key validation
            return len(api_key) > 10
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return False


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication for all requests"""
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
        
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key required"}
            )
        
        # Handle Bearer token format
        if api_key.startswith("Bearer "):
            api_key = api_key.replace("Bearer ", "")
        
        # Verify API key
        if not self.verify_api_key(api_key):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"}
            )
        
        # Add user context to request
        request.state.user = self.get_user_from_api_key(api_key)
        request.state.api_key = api_key
        
        response = await call_next(request)
        return response
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        try:
            if not api_key.startswith("mcp_"):
                return False
            
            # Simple validation - in production, check against database
            return len(api_key) > 10
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return False
    
    def get_user_from_api_key(self, api_key: str) -> Dict[str, Any]:
        """Extract user information from API key"""
        # In a real implementation, this would query the database
        # For now, return a mock user
        return {
            "user_id": "demo_user",
            "permissions": ["viewer", "moderator"],
            "tenant_id": "demo_tenant"
        }


def generate_api_key(user_id: str, secret: str) -> str:
    """Generate API key for a user"""
    # Create HMAC signature
    message = f"{user_id}:{secret}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Format as API key
    return f"mcp_{signature[:32]}"


def validate_permissions(required_permissions: list, user_permissions: list) -> bool:
    """Validate if user has required permissions"""
    return any(perm in user_permissions for perm in required_permissions)


class PermissionChecker:
    """Class to check user permissions"""
    
    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions
    
    def __call__(self, request: Request) -> bool:
        user = getattr(request.state, 'user', None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_permissions = user.get('permissions', [])
        if not validate_permissions(self.required_permissions, user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return True 