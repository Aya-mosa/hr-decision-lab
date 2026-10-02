"""
End-to-end test of Generator -> Evaluator -> Pattern Analyzer using the
client's real Level 2 worked example, WITHOUT calling a live LLM.

Run: python3 tests/test_pipeline_offline.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.models import Scenario, AnswerOption, HRLevel, ScenarioCategory
from app.services.evaluator import build_decision_record
from app.services.pattern_analyzer import analyze_session


def build_client_example_scenario() -> Scenario:
    return Scenario(
        scenario_id="example_l2_001",
        level=HRLevel.BUSINESS_PARTNER,
        category=ScenarioCategory.RETENTION,
        title="ارتفاع معدل الاستقالات في إدارة المبيعات",
        situation="ارتفع معدل دوران الموظفين في إدارة المبيعات من 11% إلى 23%...",
        question="بصفتك HR Business Partner، ما الإجراء الذي ستتخذه؟",
        options=[
            AnswerOption(option_id="A", text="زيادة رواتب الجميع 15%", immediate_result="ترتفع رضا المبيعات",
                long_term_consequences=["تكلفة مرتفعة"], archetype_label="Quick-Fix Manager"),
            AnswerOption(option_id="B", text="رفض الزيادة ومطالبة المدير بمعالجة القيادة", immediate_result="تجنب التكلفة",
                long_term_consequences=["قد تستمر الاستقالات"], archetype_label="HR Functional Expert"),
            AnswerOption(option_id="C", text="تحليل شامل وخطة مشتركة مع Sales وFinance", immediate_result="صورة دقيقة للمشكلة",
                long_term_consequences=["تعديل رواتب فئات محددة"], archetype_label="Data-Driven Analyst"),
            AnswerOption(option_id="D", text="Retention Bonus لأفضل الموظفين فقط", immediate_result="حماية المواهب بتكلفة أقل",
                long_term_consequences=["لا تعالج مشكلة القيادة"], archetype_label="Business Partner"),
        ],
    )


def main():
    session_id = "test_session_1"
    scenario = build_client_example_scenario()
    print(f"[1] Scenario built & validated: {scenario.title}")

    # Simulate the user picking option C (the client's "target" behavior)
    # across 3 repeated scenarios.
    decisions = [build_decision_record(session_id, scenario, "C") for _ in range(3)]
    print(f"[2] Evaluator produced {len(decisions)} decision records via lookup (no LLM call)")

    report = analyze_session(session_id, decisions)
    print("[3] Pattern report generated:")
    print(f"    Dominant archetype : {report.dominant_archetype}")
    print(f"    Target archetype   : {report.target_archetype}")
    print(f"    Traits             : {report.traits}")
    print(f"    Strengths          : {report.strengths}")
    print(f"    Risks              : {report.risks}")
    print(f"    Growth area        : {report.growth_area}")

    assert report.dominant_archetype == "Data-Driven Analyst"
    assert report.dominant_archetype == report.target_archetype  # this session hit the client's ideal pattern
    print("\n✅ Pipeline test passed — schema, evaluator, and analyzer all work correctly.")


if __name__ == "__main__":
    main()
