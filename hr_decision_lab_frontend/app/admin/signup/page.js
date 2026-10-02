"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { adminSignup, adminLogin } from "@/lib/adminApi";

export default function AdminSignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await adminSignup(email, password);
      await adminLogin(email, password);
      router.push("/admin/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center mb-8">إنشاء حساب مدير</h1>
        <form onSubmit={handleSubmit} className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8">
          <label className="block text-sm text-[var(--color-muted)] mb-2">البريد الإلكتروني</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-[var(--color-line)] bg-transparent px-4 py-3 mb-4 focus:border-[var(--color-gold)] outline-none" />
          <label className="block text-sm text-[var(--color-muted)] mb-2">كلمة المرور</label>
          <input type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-[var(--color-line)] bg-transparent px-4 py-3 mb-6 focus:border-[var(--color-gold)] outline-none" />
          {error && <p className="text-[var(--color-gold)] text-sm mb-4">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "جارٍ الإنشاء..." : "إنشاء الحساب"}
          </button>
        </form>
        <p className="text-center text-sm text-[var(--color-muted)] mt-4">
          عندك حساب بالفعل؟ <Link href="/admin/login" className="text-[var(--color-gold)]">دخول</Link>
        </p>
      </div>
    </main>
  );
}
