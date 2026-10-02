# HR Decision Lab — Backend Skeleton (v0.1)

## البنية

```
app/
  schemas/models.py            -> العقد الأساسي لكل البيانات (Scenario, AnswerOption, PatternReport...)
  prompts/scenario_generator_system_prompt.txt  -> System prompt لوكيل التوليد + few-shot من مثال العميل
  services/scenario_generator.py -> Agent 1: يستدعي LLM ويتحقق من الناتج بالـ schema
  services/evaluator.py          -> Agent 2: lookup بسيط (مفيش LLM call)
  services/pattern_analyzer.py   -> Agent 3: تجميع الوسوم + تصنيف النمط (rule-based)
tests/test_pipeline_offline.py   -> تجربة كاملة للـ pipeline بدون الحاجة لـ API key
```

## اتعمل ✅

- Schema كامل ومتحقق منه بمثال العميل الحقيقي (سيناريو الاستقالات في المبيعات).
- System prompt لوكيل التوليد جاهز بالـ few-shot، مُختبر فعليًا مع OpenRouter (موديل مجاني).
- توليد سيناريو حي شغال end-to-end مع retry تلقائي لو الموديل غلط في الـ schema.
- Evaluator شغال كـ lookup مباشر — مفيش تكلفة LLM إضافية هنا.
- Pattern Analyzer بيجمع الوسوم ويطلع نمط، لكن منطق "فض التعادل" بين الوسوم المتساوية لسه placeholder.
- FastAPI endpoints كاملة (`/sessions/{id}/scenarios`, `/sessions/{id}/decisions`, `/sessions/{id}/report`)، مُختبرة بالكامل offline.
- تخزين مؤقت في الذاكرة (in-memory) — مش قاعدة بيانات حقيقية بعد، ده الخطوة الجاية.

## تشغيل السيرفر محليًا

```
uvicorn app.api.main:app --reload
```
بعدها افتحي http://127.0.0.1:8000/docs عشان تجربي الـ endpoints من واجهة تفاعلية جاهزة (Swagger UI) — مفيش حاجة تانية محتاجة تعمليها.

## محتاجين نحسمه مع العميل قبل الاستمرار

1. القائمة الكاملة للـ Behavior Tags (عندنا 5 بس من مثال واحد).
2. هل الأنماط النهائية (Decision Styles) قائمة مغلقة ولا مفتوحة؟
3. لما يتساوى أكتر من وسم في التكرار، إزاي نحدد "النمط المسيطر"؟
4. مثال أو اتنين من مستويات/فئات مختلفة، للتأكد إن الأسلوب ثابت.

## الخطوة الجاية

بمجرد ما يوصل رد العميل، التعديل هيكون في مكانين بس:
`app/schemas/models.py` (BehaviorTag, DecisionStyle) و `app/services/pattern_analyzer.py` (TAG_TO_STYLE mapping).
باقي الكود (Generator, Evaluator, API) مش هيتلمس.

## تجربة التوليد الحي (Gemini)

1. احصلي على مفتاح مجاني من https://aistudio.google.com/apikey
2. حطيه كمتغير بيئة (PowerShell):
   ```
   $env:GEMINI_API_KEY="your_key_here"
   ```
3. شغّلي:
   ```
   python tests/test_live_generation.py
   ```

ده هيولّد سيناريو حقيقي من Gemini ويتحقق منه ضد الـ schema بتاعنا. لو فشل التحقق (schema validation error)، معناها الـ prompt محتاج تعديل بسيط — الرسالة هتوضح بالظبط إيه اللي غلط.

بعد كده: بناء FastAPI endpoints (`/generate-scenario`, `/submit-decision`, `/session/{id}/report`) وربطها بقاعدة بيانات.
