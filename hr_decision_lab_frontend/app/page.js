import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex-1 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-3xl font-bold tracking-tight mb-2">مختبر قرار الموارد البشرية</h1>
        <p className="text-sm text-[var(--color-muted)] mb-12">
          سيناريوهات واقعية لاختبار وتطوير نمط اتخاذ القرار المهني
        </p>

        <div className="grid sm:grid-cols-2 gap-4">
          <Link
            href="/assess"
            className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8 hover:border-[var(--color-gold)] transition-colors text-right"
          >
            <p className="text-lg font-medium mb-2">عايز أعرف نمط قراري</p>
            <p className="text-sm text-[var(--color-muted)]">
              جربي 10 سيناريوهات واقعية واحصلي على تقرير نمطك في اتخاذ القرار
            </p>
          </Link>

          <Link
            href="/admin/login"
            className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] p-8 hover:border-[var(--color-gold)] transition-colors text-right"
          >
            <p className="text-lg font-medium mb-2">أنا مدير موارد بشرية / مسؤول توظيف</p>
            <p className="text-sm text-[var(--color-muted)]">
              ادعِ فريقك أو المرشحين للتقييم وشوف نتائجهم من لوحة تحكم واحدة
            </p>
          </Link>
        </div>
      </div>
    </main>
  );
}
