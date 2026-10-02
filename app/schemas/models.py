"""
Core data contracts for HR Decision Lab.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class HRLevel(str, Enum):
    OPERATIONS = "hr_operations"
    BUSINESS_PARTNER = "hr_business_partner"
    STRATEGIC_LEADER = "strategic_hr_leader"


class ScenarioCategory(str, Enum):
    EMPLOYEE_RELATIONS = "employee_relations"
    PERFORMANCE = "performance"
    RECRUITMENT = "recruitment"
    TALENT_MANAGEMENT = "talent_management"
    RETENTION = "retention"
    COMPENSATION = "compensation"
    BUSINESS_PARTNERING = "business_partnering"
    WORKFORCE_DECISIONS = "workforce_decisions"
    LEADERSHIP = "leadership"
    HR_ETHICS = "hr_ethics"
    SAUDI_HR_PRACTICE = "saudi_hr_practice"


class AnswerOption(BaseModel):
    option_id: str
    text: str
    immediate_result: str
    long_term_consequences: List[str]
    archetype_label: str = Field(
        ..., description="Must be one of the closed catalog names for this scenario's level"
    )


class Scenario(BaseModel):
    scenario_id: str
    level: HRLevel
    category: ScenarioCategory
    title: str
    situation: str
    question: str
    options: List[AnswerOption] = Field(..., min_length=3, max_length=5)

    @model_validator(mode="after")
    def _validate_archetypes_match_level(self) -> "Scenario":
        from app.data.archetype_catalog import ARCHETYPES_BY_LEVEL
        allowed = set(ARCHETYPES_BY_LEVEL[self.level])
        for option in self.options:
            if option.archetype_label not in allowed:
                raise ValueError(
                    f"archetype_label '{option.archetype_label}' is not valid for level "
                    f"'{self.level.value}'. Allowed values: {sorted(allowed)}"
                )
        return self


class DecisionRecord(BaseModel):
    session_id: str
    scenario_id: str
    level: HRLevel
    chosen_option_id: str
    archetype_label: str


class ArchetypeFrequency(BaseModel):
    archetype_label: str
    count: int
    total: int

    @property
    def ratio(self) -> float:
        return self.count / self.total if self.total else 0.0


class PatternReport(BaseModel):
    session_id: str
    level: HRLevel
    total_scenarios: int
    archetype_frequencies: List[ArchetypeFrequency]
    dominant_archetype: str
    dominant_archetype_ar: str
    target_archetype: str
    target_archetype_ar: str
    traits: str
    strengths: str
    risks: str
    growth_area: str
    narrative_summary: Optional[str] = None
