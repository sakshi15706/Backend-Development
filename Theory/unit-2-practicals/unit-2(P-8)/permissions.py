"""Centralised authorization (RBAC).  Authentication (who are you?) stays in auth.py.

Rules from the lecture that are implemented here
  * permissions are assigned to ROLES, users inherit them from their role
  * DENY BY DEFAULT: anything not listed below is forbidden
  * LEAST PRIVILEGE: each role gets only what it needs
  * OWNERSHIP checks: a student may touch their own record only
  * one central place for the rules + AUDIT LOG of every decision
"""
import logging

from fastapi import Depends, HTTPException, status

import models
from auth import get_current_user

audit = logging.getLogger("authz")

STUDENT_PERMS = {"students:read_own", "students:update_own", "courses:read", "grades:read_own"}
FACULTY_PERMS = {"students:read", "courses:read", "grades:read", "grades:write"}
ADMIN_PERMS = {
    "students:read", "students:write", "students:delete",
    "courses:read", "courses:write", "courses:delete",
    "grades:read", "grades:write",
    "roles:manage",
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": ADMIN_PERMS,
    "faculty": FACULTY_PERMS,
    "student": STUDENT_PERMS,
}
ROLES = tuple(ROLE_PERMISSIONS)


def permissions_of(user: models.Student) -> set[str]:
    # unknown / corrupted role => empty set => everything denied
    return ROLE_PERMISSIONS.get(user.role, set())


def has_permission(user: models.Student, permission: str) -> bool:
    return permission in permissions_of(user)


def _deny(user: models.Student, needed: str, target: str) -> HTTPException:
    audit.warning("DENY  user=%s role=%s needs=%s on %s", user.id, user.role, needed, target)
    return HTTPException(status.HTTP_403_FORBIDDEN, f"Permission denied: {needed} required")


def require_permission(permission: str):
    """Dependency: the caller's role must include `permission`."""
    def dependency(current: models.Student = Depends(get_current_user)) -> models.Student:
        if not has_permission(current, permission):
            raise _deny(current, permission, "endpoint")
        audit.info("ALLOW user=%s role=%s has=%s", current.id, current.role, permission)
        return current
    return dependency


def require_permission_or_own(permission: str, own_permission: str):
    """Dependency for /students/{student_id}/...:
    allowed when the role has `permission` (any student), OR has `own_permission` AND it is their own record."""
    def dependency(student_id: int, current: models.Student = Depends(get_current_user)) -> models.Student:
        if has_permission(current, permission):
            audit.info("ALLOW user=%s role=%s has=%s", current.id, current.role, permission)
            return current
        if has_permission(current, own_permission) and current.id == student_id:
            audit.info("ALLOW user=%s role=%s has=%s on own record", current.id, current.role, own_permission)
            return current
        raise _deny(current, f"{permission} (or {own_permission} on your own record)", f"student {student_id}")
    return dependency
