"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { isAdminLoggedIn, getInviteReport } from "@/lib/adminApi";

export default function InviteReportPage() {
  const { inviteId } = useParams();
  const router = useRouter();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAdminLoggedIn()) { router.push("/admin/login"); return; }
    getInviteReport(inviteId).then(setReport).catch((e) => setError(e.message));
  }, [inviteId]);

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl">
        <Link href="/admin/dashboard" className="text-sm text-[var(--color-muted)] mb-6 inline-block">← رجوع للوحة التحكم</Link>
        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8">
          {error && <p className="text-[var(--color-gold)] text-center py-8">{error}</p>}
          {!error && !report && <p className="text-center text-[var(--color-muted)] py-12">جارٍ التحميل...</p>}
          {report && (
            <div>
              <h1 className="text-xl font-bold mb-1">تقرير نمط القرار</h1>
              <p className="text-sm text-[var(--color-muted)] mb-6">مبني على {report.total_scenarios} سيناريوهات</p>
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
                  <p className="text-xs text-[var(--color-muted)] mb-1">النمط المسيطر</p>
                  <p className="font-medium text-[var(--color-gold)]">{report.dominant_archetype_ar} — {report.dominant_archetype}</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--color-muted)] mb-1">النمط المستهدف لهذا المستوى</p>
                  <p className="font-medium">{report.target_archetype_ar} — {report.target_archetype}</p>
                </div>
              </div>
              {report.narrative_summary && (
                <div className="rounded-md border border-[var(--color-line)] px-5 py-4 leading-relaxed">{report.narrative_summary}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
