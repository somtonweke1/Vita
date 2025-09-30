"""
Authentication and authorization dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Optional
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Validate JWT token and extract user information.

    In production, this would:
    1. Validate JWT signature using Auth0 public key
    2. Verify token expiration
    3. Check token audience
    4. Extract user claims (sub, email, roles, permissions)

    For MVP, we'll do basic JWT validation.

    Returns:
        dict: User claims from JWT token

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # Decode JWT
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Extract additional claims
        user_data = {
            "sub": user_id,
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }

        logger.debug(f"Authenticated user: {user_id}")
        return user_data

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in auth: {e}", exc_info=True)
        raise credentials_exception


def require_permission(required_permission: str):
    """
    Dependency factory to check for specific permission.

    Usage:
        @router.post("/members")
        async def create_member(
            member_data: MemberCreate,
            user: dict = Depends(require_permission("write:members"))
        ):
            ...

    Args:
        required_permission: Permission string (e.g., "write:members")

    Returns:
        Dependency function that validates permission
    """
    async def permission_checker(
        current_user: Dict = Depends(get_current_user)
    ) -> Dict:
        permissions = current_user.get("permissions", [])

        if required_permission not in permissions:
            logger.warning(
                f"User {current_user.get('sub')} attempted action requiring "
                f"{required_permission} but has permissions: {permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )

        return current_user

    return permission_checker


def require_role(required_role: str):
    """
    Dependency factory to check for specific role.

    Usage:
        @router.get("/admin/reports")
        async def get_admin_report(
            user: dict = Depends(require_role("admin"))
        ):
            ...

    Args:
        required_role: Role name (e.g., "admin", "care_manager")

    Returns:
        Dependency function that validates role
    """
    async def role_checker(
        current_user: Dict = Depends(get_current_user)
    ) -> Dict:
        roles = current_user.get("roles", [])

        if required_role not in roles:
            logger.warning(
                f"User {current_user.get('sub')} attempted action requiring "
                f"role {required_role} but has roles: {roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )

        return current_user

    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Get current user if token provided, otherwise None.
    Useful for endpoints that work with or without authentication.

    Returns:
        dict: User data if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# Helper function to create JWT tokens (for testing/dev)
def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    Used for:
    - Testing endpoints
    - Development authentication
    - Internal service-to-service auth

    In production, Auth0 handles token creation.

    Args:
        data: Claims to encode in token (sub, email, roles, permissions)

    Returns:
        str: JWT token
    """
    from datetime import datetime, timedelta

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt