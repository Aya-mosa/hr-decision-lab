from __future__ import annotations
from collections import Counter
from typing import List

from app.schemas.models import DecisionRecord, PatternReport, ArchetypeFrequency, HRLevel
from app.data.archetype_catalog import ARCHETYPE_DETAILS, TARGET_ARCHETYPE_BY_LEVEL


def analyze_session(session_id: str, decisions: List[DecisionRecord]) -> PatternReport:
    if not decisions:
        raise ValueError("Cannot analyze a session with zero decisions")

    levels_seen = {d.level for d in decisions}
    if len(levels_seen) > 1:
        raise ValueError(f"Session '{session_id}' mixes multiple levels ({levels_seen})")
    level: HRLevel = decisions[0].level

    total = len(decisions)
    counter: Counter = Counter(d.archetype_label for d in decisions)
    frequencies = [
        ArchetypeFrequency(archetype_label=label, count=count, total=total)
        for label, count in counter.most_common()
    ]

    dominant = frequencies[0].archetype_label
    details = ARCHETYPE_DETAILS[dominant]
    target = TARGET_ARCHETYPE_BY_LEVEL[level]

    return PatternReport(
        session_id=session_id, level=level, total_scenarios=total,
        archetype_frequencies=frequencies, dominant_archetype=dominant,
        dominant_archetype_ar=details["label_ar"], target_archetype=target,
        target_archetype_ar=ARCHETYPE_DETAILS[target]["label_ar"],
        traits=details["traits"], strengths=details["strengths"],
        risks=details["risks"], growth_area=details["growth_area"],
        narrative_summary=None,
    )
