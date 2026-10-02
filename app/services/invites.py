from __future__ import annotations
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.db import SessionLocal
from app.db_models import InviteORM, AdminUserORM
from app.services.email_sender import send_email, invite_email_html, results_ready_email_html

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")


def create_invite_batch(admin_id: str, invite_type: str, invitees: List[dict],
                         deadline: Optional[datetime] = None) -> str:
    if invite_type not in ("team_member", "candidate"):
        raise ValueError("invite_type must be 'team_member' or 'candidate'")

    batch_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        for person in invitees:
            invite = InviteORM(
                id=str(uuid.uuid4()), batch_id=batch_id, admin_id=admin_id,
                invite_type=invite_type, email=person["email"], name=person.get("name"),
                level=person["level"], deadline=deadline, status="pending", consented=0,
                created_at=datetime.now(timezone.utc),
            )
            db.add(invite)
        db.commit()
        invites = db.query(InviteORM).filter(InviteORM.batch_id == batch_id).all()
        for invite in invites:
            _send_invite_email(invite)
    finally:
        db.close()
    return batch_id


def _send_invite_email(invite: InviteORM) -> None:
    invite_url = f"{FRONTEND_BASE_URL}/invite/{invite.id}"
    deadline_text = invite.deadline.strftime("%Y-%m-%d") if invite.deadline else ""
    html = invite_email_html(
        name=invite.name or "", invite_url=invite_url, deadline_text=deadline_text,
        is_candidate=(invite.invite_type == "candidate"),
    )
    try:
        send_email(invite.email, "دعوة لإكمال تقييم — مختبر قرار الموارد البشرية", html)
    except RuntimeError:
        pass


def get_invite(invite_id: str) -> InviteORM:
    db = SessionLocal()
    try:
        invite = db.get(InviteORM, invite_id)
        if invite is None:
            raise KeyError(f"Invite '{invite_id}' not found")
        return invite
    finally:
        db.close()


def mark_consented(invite_id: str) -> None:
    db = SessionLocal()
    try:
        invite = db.get(InviteORM, invite_id)
        if invite is None:
            raise KeyError(f"Invite '{invite_id}' not found")
        invite.consented = 1
        db.commit()
    finally:
        db.close()


def start_invite_session(invite_id: str, session_id: str) -> None:
    db = SessionLocal()
    try:
        invite = db.get(InviteORM, invite_id)
        if invite is None:
            raise KeyError(f"Invite '{invite_id}' not found")
        invite.session_id = session_id
        invite.status = "in_progress"
        db.commit()
    finally:
        db.close()


def complete_invite(invite_id: str) -> None:
    db = SessionLocal()
    try:
        invite = db.get(InviteORM, invite_id)
        if invite is None:
            raise KeyError(f"Invite '{invite_id}' not found")
        invite.status = "completed"
        db.commit()

        remaining = (
            db.query(InviteORM)
            .filter(InviteORM.batch_id == invite.batch_id, InviteORM.status != "completed")
            .count()
        )
        if remaining == 0:
            admin = db.get(AdminUserORM, invite.admin_id)
            if admin:
                dashboard_url = f"{FRONTEND_BASE_URL}/admin/dashboard"
                try:
                    send_email(admin.email, "نتائج الدفعة جاهزة — مختبر قرار الموارد البشرية",
                               results_ready_email_html("", dashboard_url))
                except RuntimeError:
                    pass
    finally:
        db.close()


def list_invites_for_admin(admin_id: str) -> List[InviteORM]:
    db = SessionLocal()
    try:
        return (
            db.query(InviteORM).filter(InviteORM.admin_id == admin_id)
            .order_by(InviteORM.created_at.desc()).all()
        )
    finally:
        db.close()
