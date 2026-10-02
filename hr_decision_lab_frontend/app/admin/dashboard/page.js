"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { isAdminLoggedIn, adminLogout, createInvites, listInvites } from "@/lib/adminApi";
import { LEVELS } from "@/lib/api";

const STATUS_LABELS = { pending: "لم يبدأ", in_progress: "قيد الإجابة", completed: "اكتمل", expired: "انتهت المهلة" };

export default function AdminDashboardPage() {
  const router = useRouter();
  const [invites, setInvites] = useState(null);
  const [error, setError] = useState("");
  const [inviteType, setInviteType] = useState("team_member");
  const [rows, setRows] = useState([{ email: "", name: "", level: LEVELS[0].id }]);
  const [deadline, setDeadline] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    if (!isAdminLoggedIn()) { router.push("/admin/login"); return; }
    refreshInvites();
  }, []);

  async function refreshInvites() {
    try { setInvites(await listInvites()); } catch (e) { setError(e.message); }
  }

  function updateRow(index, field, value) {
    setRows((prev) => prev.map((r, i) => (i === index ? { ...r, [field]: value } : r)));
  }
  function addRow() { setRows((prev) => [...prev, { email: "", name: "", level: LEVELS[0].id }]); }
  function removeRow(index) { setRows((prev) => prev.filter((_, i) => i !== index)); }

  async function handleCreateBatch(e) {
    e.preventDefault();
    setError(""); setSuccessMsg(""); setSubmitting(true);
    try {
      const invitees = rows.filter((r) => r.email.trim())
        .map((r) => ({ email: r.email.trim(), name: r.name.trim() || null, level: r.level }));
      if (invitees.length === 0) throw new Error("أضيفي بريدًا إلكترونيًا واحدًا على الأقل");
      await createInvites(inviteType, invitees, deadline ? new Date(deadline).toISOString() : null);
      setSuccessMsg(`تم إرسال ${invitees.length} دعوة بنجاح`);
      setRows([{ email: "", name: "", level: LEVELS[0].id }]);
      setDeadline("");
      refreshInvites();
    } catch (e) { setError(e.message); } finally { setSubmitting(false); }
  }

  function handleLogout() { adminLogout(); router.push("/admin/login"); }

  return (
    <main className="flex-1 px-6 py-12">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-10">
          <h1 className="text-2xl font-bold">لوحة تحكم المدير</h1>
          <button onClick={handleLogout} className="text-sm text-[var(--color-muted)] hover:text-[var(--color-gold)]">تسجيل الخروج</button>
        </div>

        <section className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-6 mb-10">
          <h2 className="text-lg font-medium mb-5">إنشاء دفعة دعوات جديدة</h2>
          <form onSubmit={handleCreateBatch}>
            <div className="flex gap-4 mb-5">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" checked={inviteType === "team_member"} onChange={() => setInviteType("team_member")} /> فريق داخلي
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" checked={inviteType === "candidate"} onChange={() => setInviteType("candidate")} /> مرشحون للتوظيف
              </label>
            </div>

            {rows.map((row, i) => (
              <div key={i} className="flex gap-2 mb-3">
                <input type="email" placeholder="البريد الإلكتروني" value={row.email} onChange={(e) => updateRow(i, "email", e.target.value)}
                  className="flex-1 rounded-md border border-[var(--color-line)] bg-transparent px-3 py-2 text-sm focus:border-[var(--color-gold)] outline-none" />
                <input type="text" placeholder="الاسم (اختياري)" value={row.name} onChange={(e) => updateRow(i, "name", e.target.value)}
                  className="w-40 rounded-md border border-[var(--color-line)] bg-transparent px-3 py-2 text-sm focus:border-[var(--color-gold)] outline-none" />
                <select value={row.level} onChange={(e) => updateRow(i, "level", e.target.value)}
                  className="rounded-md border border-[var(--color-line)] bg-[var(--color-ink)] px-3 py-2 text-sm focus:border-[var(--color-gold)] outline-none">
                  {LEVELS.map((lvl) => (<option key={lvl.id} value={lvl.id}>{lvl.label}</option>))}
                </select>
                {rows.length > 1 && (<button type="button" onClick={() => removeRow(i)} className="text-[var(--color-muted)] px-2">×</button>)}
              </div>
            ))}
            <button type="button" onClick={addRow} className="text-sm text-[var(--color-gold)] mb-5">+ إضافة شخص آخر</button>

            <div className="mb-5">
              <label className="block text-sm text-[var(--color-muted)] mb-2">تاريخ نهائي (اختياري)</label>
              <input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)}
                className="rounded-md border border-[var(--color-line)] bg-transparent px-3 py-2 text-sm focus:border-[var(--color-gold)] outline-none" />
            </div>

            {error && <p className="text-[var(--color-gold)] text-sm mb-4">{error}</p>}
            {successMsg && <p className="text-green-400 text-sm mb-4">{successMsg}</p>}

            <button type="submit" disabled={submitting} className="btn-primary">
              {submitting ? "جارٍ الإرسال..." : "إرسال الدعوات"}
            </button>
          </form>
        </section>

        <section>
          <h2 className="text-lg font-medium mb-5">المدعوّون</h2>
          {invites === null && <p className="text-[var(--color-muted)]">جارٍ التحميل...</p>}
          {invites && invites.length === 0 && <p className="text-[var(--color-muted)]">لسه مفيش دعوات مُرسلة.</p>}
          {invites && invites.length > 0 && (
            <div className="flex flex-col gap-2">
              {invites.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between rounded-md border border-[var(--color-line)] px-4 py-3">
                  <div>
                    <p className="font-medium">{inv.name || inv.email}</p>
                    <p className="text-xs text-[var(--color-muted)]">{inv.email}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-[var(--color-muted)]">{STATUS_LABELS[inv.status] || inv.status}</span>
                    {inv.status === "completed" ? (
                      <Link href={`/admin/report/${inv.id}`} className="text-sm text-[var(--color-gold)]">عرض التقرير</Link>
                    ) : (
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(`${window.location.origin}/invite/${inv.id}`);
                          alert("تم نسخ رابط الدعوة");
                        }}
                        className="text-sm text-[var(--color-gold)]"
                      >
                        نسخ رابط الدعوة
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
