"""
FastAPI Authentication and Authorization dependencies.
Verifies JWT signatures, user database existence, active status, and role authorization.
"""

from typing import Dict, Any, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from utils.security import decode_access_token
from database import get_db_connection

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Extracts and verifies JWT Bearer token.
    Validates user active status in SQLite.
    Returns authenticated user dict.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists and is active in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = dict(row)
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently inactive. Contact the administrator.",
        )

    return user


def require_roles(allowed_roles: List[str]):
    """Factory dependency restricting endpoint access to specific roles."""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{user_role}' does not have permission for this resource. Required: {', '.join(allowed_roles)}.",
            )
        return current_user
    return role_checker


# Role shortcut dependencies
require_citizen = require_roles(["CITIZEN"])
require_officer = require_roles(["DEPARTMENT_OFFICER"])
require_admin = require_roles(["ADMIN"])
require_officer_or_admin = require_roles(["DEPARTMENT_OFFICER", "ADMIN"])
require_any_authenticated = get_current_user
