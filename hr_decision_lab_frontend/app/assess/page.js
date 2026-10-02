"use client";

import { useState } from "react";
import {
  LEVELS,
  CATEGORIES,
  newSessionId,
  generateScenario,
  submitDecision,
  getReport,
  shareResultByEmail,
} from "@/lib/api";
import { downloadPatternCard } from "@/lib/patternCard";

const SCENARIOS_PER_ASSESSMENT = 10;

function randomCategory() {
  return CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)].id;
}

export default function AssessPage() {
  const [phase, setPhase] = useState("level-select");
  const [userName, setUserName] = useState("");
  const [level, setLevel] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [scenarioCount, setScenarioCount] = useState(0);
  const [lastDecision, setLastDecision] = useState(null);
  const [report, setReport] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function startLevel(chosenLevel) {
    setLevel(chosenLevel);
    const sid = newSessionId();
    setSessionId(sid);
    setScenarioCount(0);
    await loadNextScenario(sid, chosenLevel);
  }

  async function loadNextScenario(sid, lvl) {
    setPhase("loading");
    setErrorMessage("");
    try {
      const s = await generateScenario(sid, lvl, randomCategory());
      setScenario(s);
      setPhase("scenario");
    } catch (e) {
      setErrorMessage(e.message);
      setPhase("error");
    }
  }

  async function chooseOption(optionId) {
    setPhase("loading");
    try {
      const result = await submitDecision(sessionId, scenario.scenario_id, optionId);
      setLastDecision(result);
      setScenarioCount((c) => c + 1);
      setPhase("result");
    } catch (e) {
      setErrorMessage(e.message);
      setPhase("error");
    }
  }

  async function viewReport() {
    setPhase("loading");
    try {
      const r = await getReport(sessionId);
      setReport(r);
      setPhase("report");
    } catch (e) {
      setErrorMessage(e.message);
      setPhase("error");
    }
  }

  function restart() {
    setPhase("level-select");
    setLevel(null);
    setSessionId(null);
    setScenario(null);
    setScenarioCount(0);
    setLastDecision(null);
    setReport(null);
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl">
        <header className="mb-10 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-[var(--color-paper)]">
            مختبر قرار الموارد البشرية
          </h1>
          <p className="mt-2 text-sm text-[var(--color-muted)]">
            سيناريوهات واقعية لاختبار وتطوير نمط اتخاذ القرار المهني
          </p>
        </header>

        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8">
          {phase === "level-select" && (
            <LevelSelect userName={userName} onNameChange={setUserName} onSelect={startLevel} />
          )}

          {phase === "loading" && (
            <p className="text-center text-[var(--color-muted)] py-12">جارٍ التحميل...</p>
          )}

          {phase === "error" && (
            <div className="text-center py-8">
              <p className="text-[var(--color-gold)] font-medium mb-4">حدث خطأ</p>
              <p className="text-sm text-[var(--color-muted)] mb-6">{errorMessage}</p>
              <button onClick={restart} className="btn-primary">البدء من جديد</button>
            </div>
          )}

          {phase === "scenario" && scenario && (
            <ScenarioView
              scenario={scenario}
              scenarioNumber={scenarioCount + 1}
              totalRequired={SCENARIOS_PER_ASSESSMENT}
              onChoose={chooseOption}
            />
          )}

          {phase === "result" && lastDecision && (
            <ResultView
              decision={lastDecision}
              scenarioCount={scenarioCount}
              totalRequired={SCENARIOS_PER_ASSESSMENT}
              onNext={() => loadNextScenario(sessionId, level)}
              onViewReport={viewReport}
            />
          )}

          {phase === "report" && report && (
            <ReportView report={report} userName={userName} sessionId={sessionId} onRestart={restart} />
          )}
        </div>
      </div>
    </main>
  );
}

function LevelSelect({ userName, onNameChange, onSelect }) {
  return (
    <div>
      <div className="mb-6">
        <label className="block text-sm text-[var(--color-muted)] mb-2">
          اسمك (اختياري — يظهر على بطاقة النمط القابلة للمشاركة)
        </label>
        <input
          type="text"
          value={userName}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="مثال: آية"
          className="w-full rounded-md border border-[var(--color-line)] bg-transparent px-4 py-3 text-[var(--color-paper)] placeholder:text-[var(--color-muted)]/60 focus:border-[var(--color-gold)] outline-none"
        />
      </div>
      <h2 className="text-lg font-medium mb-6 text-center">اختر المستوى</h2>
      <div className="flex flex-col gap-3">
        {LEVELS.map((lvl) => (
          <button
            key={lvl.id}
            onClick={() => onSelect(lvl.id)}
            className="text-right rounded-md border border-[var(--color-line)] px-5 py-4 hover:border-[var(--color-gold)] transition-colors"
          >
            <div className="font-medium">{lvl.label}</div>
            <div className="text-sm text-[var(--color-muted)] mt-1">{lvl.subtitle}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ScenarioView({ scenario, scenarioNumber, totalRequired, onChoose }) {
  return (
    <div>
      <p className="text-xs text-[var(--color-gold)] mb-2">
        سيناريو {scenarioNumber} من {totalRequired}
      </p>
      <h2 className="text-xl font-bold mb-4">{scenario.title}</h2>
      <p className="leading-relaxed text-[var(--color-paper)]/90 mb-6">{scenario.situation}</p>
      <p className="font-medium mb-4">{scenario.question}</p>
      <div className="flex flex-col gap-3">
        {scenario.options.map((opt) => (
          <button
            key={opt.option_id}
            onClick={() => onChoose(opt.option_id)}
            className="text-right rounded-md border border-[var(--color-line)] px-5 py-4 hover:border-[var(--color-gold)] transition-colors"
          >
            <span className="text-[var(--color-gold)] ml-2">{opt.option_id}.</span>
            {opt.text}
          </button>
        ))}
      </div>
    </div>
  );
}

function ResultView({ decision, scenarioCount, totalRequired, onNext, onViewReport }) {
  const isLast = scenarioCount >= totalRequired;
  return (
    <div>
      <p className="text-sm text-[var(--color-muted)] mb-1">النتيجة الفورية</p>
      <p className="leading-relaxed mb-4">{decision.immediate_result}</p>

      <p className="text-sm text-[var(--color-muted)] mb-1">آثار على المدى الطويل</p>
      <ul className="list-disc pr-5 mb-6 space-y-1">
        {decision.long_term_consequences.map((c, i) => (
          <li key={i} className="text-[var(--color-paper)]/90">{c}</li>
        ))}
      </ul>

      <div className="rounded-md border border-[var(--color-gold-dim)] px-4 py-3 mb-8">
        <p className="text-xs text-[var(--color-muted)] mb-1">السلوك الذي ظهر في قرارك</p>
        <p className="font-medium">{decision.archetype_label_ar}</p>
      </div>

      {isLast ? (
        <button onClick={onViewReport} className="btn-primary w-full">
          عرض تقرير نمط قرارك النهائي
        </button>
      ) : (
        <button onClick={onNext} className="btn-primary w-full">
          السيناريو التالي ({scenarioCount} من {totalRequired})
        </button>
      )}
    </div>
  );
}

function ReportView({ report, userName, sessionId, onRestart }) {
  const total = report.total_scenarios;
  const [shareEmail, setShareEmail] = useState("");
  const [shareStatus, setShareStatus] = useState(""); // "", "sending", "sent", "error"
  const [shareError, setShareError] = useState("");

  async function handleShare(e) {
    e.preventDefault();
    setShareStatus("sending");
    setShareError("");
    try {
      await shareResultByEmail(sessionId, shareEmail, userName);
      setShareStatus("sent");
    } catch (err) {
      setShareStatus("error");
      setShareError(err.message);
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-1">تقرير نمط قرارك</h2>
      <p className="text-sm text-[var(--color-muted)] mb-6">
        مبني على {total} {total === 1 ? "سيناريو" : "سيناريوهات"}
      </p>

      <div className="flex flex-col gap-2 mb-6">
        {report.archetype_frequencies.map((f) => (
          <div key={f.archetype_label} className="flex items-center gap-3">
            <div className="w-40 text-sm shrink-0">{f.archetype_label}</div>
            <div className="flex-1 h-2 rounded-full bg-[var(--color-line)] overflow-hidden">
              <div className="h-full bg-[var(--color-gold)]" style={{ width: `${(f.count / f.total) * 100}%` }} />
            </div>
            <div className="text-xs text-[var(--color-muted)] w-10 text-left">{f.count}/{f.total}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-xs text-[var(--color-muted)] mb-1">نمطك المسيطر</p>
          <p className="font-medium text-[var(--color-gold)]">
            {report.dominant_archetype_ar} — {report.dominant_archetype}
          </p>
        </div>
        <div>
          <p className="text-xs text-[var(--color-muted)] mb-1">النمط المستهدف لهذا المستوى</p>
          <p className="font-medium">{report.target_archetype_ar} — {report.target_archetype}</p>
        </div>
      </div>

      {report.narrative_summary && (
        <div className="rounded-md border border-[var(--color-line)] px-5 py-4 mb-8 leading-relaxed">
          {report.narrative_summary}
        </div>
      )}

      <div className="flex gap-3 mb-3">
        <button onClick={() => downloadPatternCard(report, userName)} className="btn-secondary flex-1">
          تحميل بطاقة النمط للمشاركة
        </button>
        <button onClick={onRestart} className="btn-primary flex-1">بدء جلسة جديدة</button>
      </div>

      {/* --- Type 2: share result via email --- */}
      <div className="rounded-md border border-[var(--color-line)] px-5 py-4 mt-6">
        <p className="text-sm font-medium mb-3">شارك نتيجتك مع صديق أو زميل عن طريق الإيميل</p>
        <form onSubmit={handleShare} className="flex gap-2">
          <input
            type="email"
            required
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            placeholder="بريد صديقك الإلكتروني"
            className="flex-1 rounded-md border border-[var(--color-line)] bg-transparent px-3 py-2 text-sm focus:border-[var(--color-gold)] outline-none"
          />
          <button type="submit" disabled={shareStatus === "sending"} className="btn-secondary">
            {shareStatus === "sending" ? "جارٍ الإرسال..." : "إرسال"}
          </button>
        </form>
        {shareStatus === "sent" && (
          <p className="text-green-400 text-sm mt-2">تم إرسال نتيجتك بنجاح!</p>
        )}
        {shareStatus === "error" && (
          <p className="text-[var(--color-gold)] text-sm mt-2">{shareError}</p>
        )}
      </div>
    </div>
  );
}
