from __future__ import annotations
from typing import List
import uuid

from app.schemas.models import Scenario, DecisionRecord
from app.db import SessionLocal
from app.db_models import ScenarioORM, DecisionORM


def new_session_id() -> str:
    return str(uuid.uuid4())


def save_scenario(scenario: Scenario) -> None:
    db = SessionLocal()
    try:
        row = ScenarioORM(
            scenario_id=scenario.scenario_id, level=scenario.level.value,
            category=scenario.category.value, data_json=scenario.model_dump_json(),
        )
        db.merge(row)
        db.commit()
    finally:
        db.close()


def get_scenario(scenario_id: str) -> Scenario:
    db = SessionLocal()
    try:
        row = db.get(ScenarioORM, scenario_id)
        if row is None:
            raise KeyError(f"Scenario '{scenario_id}' not found")
        return Scenario.model_validate_json(row.data_json)
    finally:
        db.close()


def save_decision(session_id: str, decision: DecisionRecord) -> None:
    db = SessionLocal()
    try:
        row = DecisionORM(
            session_id=session_id, scenario_id=decision.scenario_id, level=decision.level.value,
            chosen_option_id=decision.chosen_option_id, archetype_label=decision.archetype_label,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


def get_decisions(session_id: str) -> List[DecisionRecord]:
    db = SessionLocal()
    try:
        rows = db.query(DecisionORM).filter(DecisionORM.session_id == session_id).all()
        if not rows:
            raise KeyError(f"Session '{session_id}' has no decisions yet")
        return [
            DecisionRecord(
                session_id=r.session_id, scenario_id=r.scenario_id, level=r.level,
                chosen_option_id=r.chosen_option_id, archetype_label=r.archetype_label,
            ) for r in rows
        ]
    finally:
        db.close()
