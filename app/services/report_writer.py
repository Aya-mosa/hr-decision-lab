from __future__ import annotations
from app.schemas.models import PatternReport
from app.services import scenario_generator as sg

STYLE_DISPLAY_NAMES = {}  # dominant/target archetype names are already English strings now

NARRATIVE_PROMPT_TEMPLATE = """أنت كاتب تقارير محترف متخصص في تحليل السلوك المهني للموارد البشرية.

مهمتك: تحويل البيانات التالية إلى فقرة تقرير احترافية باللغة العربية الفصحى بالكامل، بأسلوب استشاري، مخاطبة مباشرة بصيغة "أنت".

قاعدة صارمة: كل الحقائق أدناه نهائية ومعطاة لك جاهزة بالعربي — أعد صياغتها بأسلوب أكثر سلاسة فقط، ولا تضف أو تحذف أي حقيقة. ممنوع استخدام أي رمز تقني (snake_case) في الناتج.

البيانات الفعلية لهذا المستخدم:
النمط المسيطر (بالإنجليزي كما هو): {dominant_archetype}
النمط المستهدف الأفضل لهذا المستوى (بالإنجليزي كما هو): {target_archetype}
عدد السيناريوهات: {total_scenarios}
السمات: {traits}
نقاط القوة: {strengths}
المخاطر المحتملة: {risks}
ما يحتاج أن يطوره: {growth_area}

أخرج JSON فقط بالشكل التالي، بدون أي نص خارجه:
{{"narrative_summary": "النص الكامل هنا"}}
"""


def polish_report(report: PatternReport) -> PatternReport:
    prompt = NARRATIVE_PROMPT_TEMPLATE.format(
        dominant_archetype=report.dominant_archetype,
        target_archetype=report.target_archetype,
        total_scenarios=report.total_scenarios,
        traits=report.traits, strengths=report.strengths,
        risks=report.risks, growth_area=report.growth_area,
    )
    raw_output = sg.call_llm(prompt)
    try:
        data = sg._extract_json(raw_output)
        report.narrative_summary = data["narrative_summary"]
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Narrative polishing returned unusable output ({e}). Raw: {raw_output}") from e
    return report
