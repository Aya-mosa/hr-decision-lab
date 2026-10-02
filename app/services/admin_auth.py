from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.db_models import AdminUserORM, AdminSessionORM

TOKEN_LIFETIME = timedelta(days=7)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()


def create_admin(email: str, password: str) -> str:
    db = SessionLocal()
    try:
        existing = db.query(AdminUserORM).filter(AdminUserORM.email == email).first()
        if existing:
            raise ValueError(f"An account with email '{email}' already exists")
        salt = secrets.token_hex(16)
        admin = AdminUserORM(
            id=secrets.token_hex(16), email=email,
            password_hash=_hash_password(password, salt), password_salt=salt,
        )
        db.add(admin)
        db.commit()
        return admin.id
    finally:
        db.close()


def login(email: str, password: str) -> str:
    db = SessionLocal()
    try:
        admin = db.query(AdminUserORM).filter(AdminUserORM.email == email).first()
        if not admin or _hash_password(password, admin.password_salt) != admin.password_hash:
            raise ValueError("Invalid email or password")
        token = secrets.token_urlsafe(32)
        session = AdminSessionORM(
            token=token, admin_id=admin.id,
            expires_at=datetime.now(timezone.utc) + TOKEN_LIFETIME,
        )
        db.add(session)
        db.commit()
        return token
    finally:
        db.close()


def get_admin_id_from_token(token: str) -> str:
    db = SessionLocal()
    try:
        session = db.get(AdminSessionORM, token)
        if not session:
            raise ValueError("Invalid session token")
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise ValueError("Session token expired — please log in again")
        return session.admin_id
    finally:
        db.close()
