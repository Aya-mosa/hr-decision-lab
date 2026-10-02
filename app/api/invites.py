from __future__ import annotations
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import invites as invite_service
from app.services.scenario_generator import generate_scenario
from app.services.evaluator import build_decision_record
from app import store
from app.schemas.models import HRLevel, ScenarioCategory
from app.config import SCENARIOS_PER_ASSESSMENT

router = APIRouter(prefix="/invites", tags=["invites"])


def _check_not_expired(invite) -> None:
    if invite.deadline:
        deadline = invite.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if deadline < datetime.now(timezone.utc) and invite.status != "completed":
            raise HTTPException(status_code=410, detail="انتهت مهلة هذه الدعوة")


@router.get("/{invite_id}")
def get_invite_info(invite_id: str):
    try:
        invite = invite_service.get_invite(invite_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "invite_type": invite.invite_type, "level": invite.level, "name": invite.name,
        "status": invite.status, "deadline": invite.deadline, "consented": bool(invite.consented),
        "requires_consent": invite.invite_type == "candidate",
    }


@router.post("/{invite_id}/consent")
def give_consent(invite_id: str):
    try:
        invite_service.mark_consented(invite_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok": True}


@router.post("/{invite_id}/scenarios")
def generate_invite_scenario(invite_id: str):
    try:
        invite = invite_service.get_invite(invite_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    _check_not_expired(invite)

    if invite.invite_type == "candidate" and not invite.consented:
        raise HTTPException(status_code=403, detail="يجب الموافقة أولًا قبل بدء التقييم")
    if invite.status == "completed":
        raise HTTPException(status_code=400, detail="تم إكمال هذا التقييم بالفعل")

    if not invite.session_id:
        session_id = str(uuid.uuid4())
        invite_service.start_invite_session(invite_id, session_id)
        invite = invite_service.get_invite(invite_id)

    level = HRLevel(invite.level)
    category = random.choice(list(ScenarioCategory))
    try:
        scenario = generate_scenario(level, category)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scenario generation failed: {e}")
    store.save_scenario(scenario)

    answered_so_far = len(_safe_get_decisions(invite.session_id))
    return {"scenario": scenario, "scenario_number": answered_so_far + 1, "total_required": SCENARIOS_PER_ASSESSMENT}


class SubmitInviteDecisionRequest(BaseModel):
    scenario_id: str
    chosen_option_id: str


@router.post("/{invite_id}/decisions")
def submit_invite_decision(invite_id: str, req: SubmitInviteDecisionRequest):
    try:
        invite = invite_service.get_invite(invite_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    _check_not_expired(invite)

    if not invite.session_id:
        raise HTTPException(status_code=400, detail="لم يبدأ التقييم بعد")

    try:
        scenario = store.get_scenario(req.scenario_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        record = build_decision_record(invite.session_id, scenario, req.chosen_option_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    store.save_decision(invite.session_id, record)

    total_answered = len(_safe_get_decisions(invite.session_id))
    is_complete = total_answered >= SCENARIOS_PER_ASSESSMENT
    if is_complete and invite.status != "completed":
        invite_service.complete_invite(invite_id)

    return {"scenario_number": total_answered, "total_required": SCENARIOS_PER_ASSESSMENT, "completed": is_complete}


def _safe_get_decisions(session_id: str):
    try:
        return store.get_decisions(session_id)
    except KeyError:
        return []
