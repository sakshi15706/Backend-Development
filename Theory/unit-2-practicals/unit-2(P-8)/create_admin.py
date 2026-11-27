"""Creates an admin user (self-registration can only create students).

    python create_admin.py admin@upes.ac.in "Admin@12345" "Admin User"
"""
import sys

import auth
import models
from database import Base, SessionLocal, engine

if len(sys.argv) < 3:
    sys.exit('usage: python create_admin.py <email> <password> ["Full Name"]')

email, password = sys.argv[1].lower(), sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else "Administrator"

Base.metadata.create_all(engine)
with SessionLocal() as db:
    user = db.query(models.Student).filter_by(email=email).first()
    if user:
        user.role = "admin"
        user.hashed_password = auth.hash_password(password)
        print(f"Existing user {email} promoted to admin and password reset")
    else:
        db.add(models.Student(name=name, email=email, branch="CSE", role="admin",
                              hashed_password=auth.hash_password(password)))
        print(f"Admin {email} created")
    db.commit()
