from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services import admin_auth, invites as invite_service, pattern_analyzer, report_writer
from app import store

router = APIRouter(prefix="/admin", tags=["admin"])
bearer_scheme = HTTPBearer()


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    try:
        return admin_auth.get_admin_id_from_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class InviteePayload(BaseModel):
    email: str
    name: Optional[str] = None
    level: str


class CreateInvitesRequest(BaseModel):
    invite_type: str
    invitees: List[InviteePayload]
    deadline: Optional[datetime] = None


@router.post("/signup")
def signup(req: SignupRequest):
    try:
        admin_id = admin_auth.create_admin(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"admin_id": admin_id}


@router.post("/login")
def login(req: LoginRequest):
    try:
        token = admin_auth.login(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"token": token}


@router.post("/invites")
def create_invites(req: CreateInvitesRequest, admin_id: str = Depends(require_admin)):
    try:
        batch_id = invite_service.create_invite_batch(
            admin_id=admin_id, invite_type=req.invite_type,
            invitees=[i.model_dump() for i in req.invitees], deadline=req.deadline,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"batch_id": batch_id}


@router.get("/invites")
def list_invites(admin_id: str = Depends(require_admin)):
    rows = invite_service.list_invites_for_admin(admin_id)
    return [
        {"id": r.id, "batch_id": r.batch_id, "invite_type": r.invite_type, "email": r.email,
         "name": r.name, "level": r.level, "status": r.status, "deadline": r.deadline,
         "created_at": r.created_at}
        for r in rows
    ]


@router.get("/invites/{invite_id}/report")
def get_invite_report(invite_id: str, admin_id: str = Depends(require_admin)):
    try:
        invite = invite_service.get_invite(invite_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if invite.admin_id != admin_id:
        raise HTTPException(status_code=403, detail="This invite does not belong to you")
    if invite.status != "completed" or not invite.session_id:
        raise HTTPException(status_code=400, detail="This participant hasn't finished the assessment yet")

    decisions = store.get_decisions(invite.session_id)
    report = pattern_analyzer.analyze_session(invite.session_id, decisions)
    try:
        report = report_writer.polish_report(report)
    except Exception:
        pass
    return report
