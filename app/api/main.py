from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.schemas.models import HRLevel, ScenarioCategory, Scenario, PatternReport
from app.services.scenario_generator import generate_scenario
from app.services.evaluator import build_decision_record
from app.services.pattern_analyzer import analyze_session
from app.services.report_writer import polish_report
from app.services.email_sender import send_email, share_result_email_html
from app.data.archetype_catalog import ARCHETYPE_DETAILS
from app import store
from app.db import init_db
from app.api import admin as admin_router
from app.api import invites as invites_router

app = FastAPI(title="HR Decision Lab API", version="0.4.0")
init_db()


allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router.router)
app.include_router(invites_router.router)


class GenerateScenarioRequest(BaseModel):
    level: HRLevel
    category: ScenarioCategory


class SubmitDecisionRequest(BaseModel):
    scenario_id: str
    chosen_option_id: str


class ShareResultRequest(BaseModel):
    to_email: str
    sender_name: str = ""


@app.post("/sessions/{session_id}/scenarios", response_model=Scenario)
def create_scenario(session_id: str, req: GenerateScenarioRequest):
    try:
        scenario = generate_scenario(req.level, req.category)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scenario generation failed: {e}")
    store.save_scenario(scenario)
    return scenario


@app.post("/sessions/{session_id}/decisions")
def submit_decision(session_id: str, req: SubmitDecisionRequest):
    try:
        scenario = store.get_scenario(req.scenario_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        record = build_decision_record(session_id, scenario, req.chosen_option_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    store.save_decision(session_id, record)
    chosen_option = next(o for o in scenario.options if o.option_id == req.chosen_option_id)
    details = ARCHETYPE_DETAILS[chosen_option.archetype_label]
    return {
        "immediate_result": chosen_option.immediate_result,
        "long_term_consequences": chosen_option.long_term_consequences,
        "archetype_label": chosen_option.archetype_label,
        "archetype_label_ar": details["label_ar"],
        "traits": details["traits"],
    }


@app.get("/sessions/{session_id}/report", response_model=PatternReport)
def get_report(session_id: str):
    try:
        decisions = store.get_decisions(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    report = analyze_session(session_id, decisions)
    try:
        report = polish_report(report)
    except Exception as e:
        print(f"[report_writer] narrative polishing failed: {type(e).__name__}: {e}")
    return report


@app.post("/sessions/{session_id}/share-email")
def share_result_by_email(session_id: str, req: ShareResultRequest):
    """Type 2: user shares their OWN already-computed result with a friend/colleague."""
    try:
        decisions = store.get_decisions(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    report = analyze_session(session_id, decisions)
    try:
        report = polish_report(report)
    except Exception:
        pass

    import os
    app_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    html = share_result_email_html(
        sender_name=req.sender_name, dominant_archetype_ar=report.dominant_archetype_ar,
        dominant_archetype=report.dominant_archetype, narrative_summary=report.narrative_summary or "",
        app_url=app_url,
    )
    try:
        send_email(req.to_email, "شارك معك نتيجته في مختبر قرار الموارد البشرية", html)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}
