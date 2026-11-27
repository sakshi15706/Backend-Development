"""First-run setup: make sure an admin account exists."""
import logging

from sqlalchemy.orm import Session

from app import auth, models

log = logging.getLogger(__name__)


def ensure_admin(db: Session, email: str, password: str) -> bool:
    """Creates the admin if no user with that email exists. Never overwrites an existing account.
    Returns True when a new admin was created."""
    email = email.lower()
    if db.query(models.Student).filter_by(email=email).first():
        return False
    db.add(models.Student(name="Administrator", email=email, branch="CSE", role="admin",
                          hashed_password=auth.hash_password(password)))
    db.commit()
    log.info("created admin account %s", email)
    return True
