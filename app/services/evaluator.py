from __future__ import annotations
from app.schemas.models import Scenario, AnswerOption, DecisionRecord


def evaluate_decision(scenario: Scenario, chosen_option_id: str) -> AnswerOption:
    for option in scenario.options:
        if option.option_id == chosen_option_id:
            return option
    raise ValueError(f"Option '{chosen_option_id}' not found in scenario {scenario.scenario_id}")


def build_decision_record(session_id: str, scenario: Scenario, chosen_option_id: str) -> DecisionRecord:
    chosen = evaluate_decision(scenario, chosen_option_id)
    return DecisionRecord(
        session_id=session_id, scenario_id=scenario.scenario_id, level=scenario.level,
        chosen_option_id=chosen_option_id, archetype_label=chosen.archetype_label,
    )
