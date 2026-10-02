"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getInviteInfo, giveConsent, generateInviteScenario, submitInviteDecision } from "@/lib/adminApi";

export default function InviteTakePage() {
  const { inviteId } = useParams();
  const [phase, setPhase] = useState("loading");
  const [scenario, setScenario] = useState(null);
  const [scenarioNumber, setScenarioNumber] = useState(0);
  const [totalRequired, setTotalRequired] = useState(10);
  const [errorMessage, setErrorMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getInviteInfo(inviteId)
      .then((info) => {
        if (info.status === "completed") setPhase("already_done");
        else if (info.requires_consent && !info.consented) setPhase("consent");
        else loadNextScenario();
      })
      .catch((e) => { setErrorMessage(e.message); setPhase("error"); });
  }, [inviteId]);

  async function handleConsent() {
    try { await giveConsent(inviteId); await loadNextScenario(); }
    catch (e) { setErrorMessage(e.message); setPhase("error"); }
  }

  async function loadNextScenario() {
    setPhase("loading");
    try {
      const data = await generateInviteScenario(inviteId);
      setScenario(data.scenario);
      setScenarioNumber(data.scenario_number);
      setTotalRequired(data.total_required);
      setPhase("scenario");
    } catch (e) { setErrorMessage(e.message); setPhase("error"); }
  }

  async function chooseOption(optionId) {
    setSubmitting(true);
    try {
      const result = await submitInviteDecision(inviteId, scenario.scenario_id, optionId);
      if (result.completed) setPhase("done"); else await loadNextScenario();
    } catch (e) { setErrorMessage(e.message); setPhase("error"); }
    finally { setSubmitting(false); }
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl">
        <header className="mb-10 text-center"><h1 className="text-3xl font-bold tracking-tight">مختبر قرار الموارد البشرية</h1></header>
        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8">
          {phase === "loading" && <p className="text-center text-[var(--color-muted)] py-12">جارٍ التحميل...</p>}
          {phase === "error" && <p className="text-center text-[var(--color-gold)] py-8">{errorMessage}</p>}
          {phase === "already_done" && <p className="text-center text-[var(--color-muted)] py-12">لقد أكملتِ هذا التقييم بالفعل. شكرًا لمشاركتك.</p>}

          {phase === "consent" && (
            <div className="text-center py-4">
              <h2 className="text-lg font-medium mb-4">قبل البدء</h2>
              <p className="leading-relaxed mb-8 text-[var(--color-paper)]/90">
                هذا التقييم جزء من عملية التوظيف. ستتم مشاركة نتيجتك (نمط اتخاذ القرار المهني) مع مسؤول التوظيف كجزء من تقييم طلبك. بالضغط على "أوافق"، فأنتِ توافقين على ذلك.
              </p>
              <button onClick={handleConsent} className="btn-primary">أوافق، ابدأ التقييم</button>
            </div>
          )}

          {phase === "scenario" && scenario && (
            <div>
              <p className="text-xs text-[var(--color-gold)] mb-2">سيناريو {scenarioNumber} من {totalRequired}</p>
              <h2 className="text-xl font-bold mb-4">{scenario.title}</h2>
              <p className="leading-relaxed text-[var(--color-paper)]/90 mb-6">{scenario.situation}</p>
              <p className="font-medium mb-4">{scenario.question}</p>
              <div className="flex flex-col gap-3">
                {scenario.options.map((opt) => (
                  <button key={opt.option_id} disabled={submitting} onClick={() => chooseOption(opt.option_id)}
                    className="text-right rounded-md border border-[var(--color-line)] px-5 py-4 hover:border-[var(--color-gold)] transition-colors disabled:opacity-50">
                    <span className="text-[var(--color-gold)] ml-2">{opt.option_id}.</span>{opt.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {phase === "done" && (
            <div className="text-center py-8">
              <h2 className="text-xl font-bold mb-3">شكرًا لك</h2>
              <p className="text-[var(--color-muted)]">تم إرسال نتيجتك بنجاح. سيتم التواصل معك إذا كانت هناك خطوة تالية.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
