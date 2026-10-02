from __future__ import annotations
from app.schemas.models import HRLevel

ARCHETYPE_DETAILS = {
    "Compliance Guardian": {
        "label_ar": "حارس الامتثال", "traits": "يرجع دائمًا للسياسة والنظام قبل القرار",
        "strengths": "قوي في الالتزام وتقليل المخاطر", "risks": "قد يصبح جامدًا وغير مرن",
        "growth_area": "Judgment + فهم سياق الحالة",
    },
    "Balanced Practitioner": {
        "label_ar": "الممارس المتوازن", "traits": "يراجع السياسة والوقائع ويسمع الأطراف قبل القرار",
        "strengths": "توازن جيد بين compliance والعدالة", "risks": "قد يكون أبطأ قليلًا في اتخاذ القرار",
        "growth_area": "سرعة الحسم مع المحافظة على الجودة",
    },
    "Manager-Led Executor": {
        "label_ar": "منفذ المدير", "traits": "يميل لتنفيذ طلب المدير دون تحدٍ كافٍ",
        "strengths": "سرعة التنفيذ ودعم العمليات", "risks": "ضعف الاستقلالية وارتفاع مخاطر القرارات الخاطئة",
        "growth_area": "Courage + Fact Finding + HR Judgment",
    },
    "Employee Advocate": {
        "label_ar": "مدافع الموظف", "traits": "يميل إلى حماية الموظف وتقليل الإجراءات عليه",
        "strengths": "تعاطف وعدالة عالية", "risks": "قد يضعف accountability",
        "growth_area": "التوازن بين employee experience والانضباط",
    },
    "Rapid Resolver": {
        "label_ar": "الحاسم السريع", "traits": "يتخذ قرارًا سريعًا لتجنب إطالة المشكلة",
        "strengths": "سرعة وحسم", "risks": "قد يتجاوز التوثيق أو التحقيق",
        "growth_area": "Process Discipline + Risk Awareness",
    },
    "Evidence Seeker": {
        "label_ar": "المحقق الدقيق", "traits": "يطلب معلومات ووثائق كثيرة قبل القرار",
        "strengths": "قرارات قابلة للدفاع عنها", "risks": "Analysis paralysis",
        "growth_area": "تحديد متى أصبحت المعلومات كافية لاتخاذ القرار",
    },
    "Data-Driven Analyst": {
        "label_ar": "المحلل القائم على البيانات",
        "traits": "يطلب البيانات ويقسم المشكلة إلى شرائح ويبحث عن patterns",
        "strengths": "قوي في التشخيص والموضوعية", "risks": "قد ينسى الجانب الإنساني أو سرعة التنفيذ",
        "growth_area": "Stakeholder Influence + Action Orientation",
    },
    "Business Partner": {
        "label_ar": "شريك الأعمال", "traits": "يوازن بين HR وFinance وOperations واحتياجات الأعمال",
        "strengths": "حلول عملية وقابلة للتنفيذ", "risks": "قد يقدم تنازلات زائدة لإرضاء الإدارات",
        "growth_area": "المحافظة على HR principles",
    },
    "Consensus Builder": {
        "label_ar": "صانع التوافق", "traits": "يبحث عن موافقة جميع الأطراف قبل التحرك",
        "strengths": "علاقات قوية وتقليل المقاومة", "risks": "بطء القرار أو حلول وسط ضعيفة",
        "growth_area": "Decision Courage",
    },
    "HR Functional Expert": {
        "label_ar": "خبير HR التقليدي",
        "traits": "يقدم حلولًا قوية من منظور HR لكن دون ربط كافٍ بالأعمال",
        "strengths": "معرفة فنية ممتازة", "risks": "قد يُنظر إليه كـ HR فقط وليس Business Partner",
        "growth_area": "Commercial Acumen",
    },
    "Quick-Fix Manager": {
        "label_ar": "مدير الحلول السريعة",
        "traits": "يقفز إلى زيادة راتب أو تدريب أو توظيف دون تشخيص عميق",
        "strengths": "سرعة الاستجابة", "risks": "علاج الأعراض وليس الأسباب",
        "growth_area": "Root Cause Analysis",
    },
    "Problem Diagnostician": {
        "label_ar": "المشخّص الاستراتيجي",
        "traits": "يبدأ بالسؤال: لماذا حدثت المشكلة؟ ثم يختبر عدة فرضيات",
        "strengths": "جودة عالية في الحلول", "risks": "قد يقضي وقتًا أطول في التحليل",
        "growth_area": "Execution + Stakeholder Mobilization",
    },
    "Strategic People Leader": {
        "label_ar": "قائد الموارد البشرية الاستراتيجي",
        "traits": "يربط قرارات المواهب باستراتيجية الشركة والنمو والقدرات المستقبلية",
        "strengths": "نظرة شاملة وطويلة المدى", "risks": "قد تصبح الحلول معقدة أكثر من اللازم",
        "growth_area": "Execution Simplicity",
    },
    "Commercial CHRO": {
        "label_ar": "القائد التجاري", "traits": "يبدأ بالتكلفة والإيرادات والإنتاجية والقيمة التجارية",
        "strengths": "Credibility عالية مع CEO/CFO", "risks": "احتمال التقليل من culture وpeople impact",
        "growth_area": "Human & Cultural Judgment",
    },
    "Enterprise Architect": {
        "label_ar": "مهندس المؤسسة", "traits": "يعيد التفكير في الهيكل والمهارات والأدوار والأتمتة",
        "strengths": "قوي في transformation", "risks": "قد يركز على design أكثر من واقعية التنفيذ",
        "growth_area": "Change Management",
    },
    "Culture & People Champion": {
        "label_ar": "حامي الثقافة", "traits": "يعطي وزنًا كبيرًا للثقافة والثقة والمواهب",
        "strengths": "يحافظ على الاستدامة والالتزام", "risks": "قد يقاوم قرارات تجارية صعبة",
        "growth_area": "Financial Acumen + Trade-offs",
    },
    "Executive Follower": {
        "label_ar": "منفذ الإدارة العليا", "traits": "يميل لموافقة CEO/CFO بسرعة وتنفيذ التوجيه",
        "strengths": "alignment وسرعة عالية", "risks": "HR يفقد دوره كشريك يتحدى الافتراضات",
        "growth_area": "Executive Courage",
    },
    "Strategic Trade-off Leader": {
        "label_ar": "قائد المفاضلات", "traits": "يقارن عدة سيناريوهات ويشرح تكلفة وفائدة كل خيار",
        "strengths": "Judgment ناضج جدًا", "risks": "يحتاج بيانات جيدة واتصالًا قويًا لدعم قراراته",
        "growth_area": "Executive Communication",
    },
    "Transformation Leader": {
        "label_ar": "قائد التحول",
        "traits": "يرى القرارات كفرصة لإعادة تصميم workforce وليس حل المشكلة فقط",
        "strengths": "يبني قدرات مستقبلية", "risks": "احتمال التغيير المفرط",
        "growth_area": "Sequencing + Change Capacity",
    },
}

ARCHETYPES_BY_LEVEL = {
    HRLevel.OPERATIONS: [
        "Compliance Guardian", "Balanced Practitioner", "Manager-Led Executor",
        "Employee Advocate", "Rapid Resolver", "Evidence Seeker",
    ],
    HRLevel.BUSINESS_PARTNER: [
        "Data-Driven Analyst", "Business Partner", "Consensus Builder",
        "HR Functional Expert", "Quick-Fix Manager", "Problem Diagnostician",
    ],
    HRLevel.STRATEGIC_LEADER: [
        "Strategic People Leader", "Commercial CHRO", "Enterprise Architect",
        "Culture & People Champion", "Executive Follower",
        "Strategic Trade-off Leader", "Transformation Leader",
    ],
}

TARGET_ARCHETYPE_BY_LEVEL = {
    HRLevel.OPERATIONS: "Balanced Practitioner",
    HRLevel.BUSINESS_PARTNER: "Data-Driven Analyst",
    HRLevel.STRATEGIC_LEADER: "Strategic Trade-off Leader",
}

LEVEL_CRITERIA = {
    HRLevel.OPERATIONS: [
        ("Compliance & Policy Application", 30), ("Fact Finding & Documentation", 20),
        ("Consistency & Fairness", 15), ("Risk Identification", 15),
        ("Process Discipline", 10), ("Communication & Employee Handling", 10),
    ],
    HRLevel.BUSINESS_PARTNER: [
        ("Problem Diagnosis & Root Cause", 20), ("Data Analysis & Evidence", 20),
        ("Business Judgment", 20), ("Stakeholder Alignment", 15),
        ("Solution Quality", 15), ("Risk & People Impact", 10),
    ],
    HRLevel.STRATEGIC_LEADER: [
        ("Strategic Business Understanding", 25), ("Enterprise Impact", 20),
        ("Scenario & Trade-off Thinking", 15), ("Financial & Commercial Acumen", 15),
        ("Executive Influence & Alignment", 15), ("Long-term People & Capability Impact", 10),
    ],
}
