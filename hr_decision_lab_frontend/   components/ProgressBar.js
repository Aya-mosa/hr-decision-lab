export default function ProgressBar({ answered, total }) {
  const safeTotal = total > 0 ? total : 1;
  const percent = Math.min(100, Math.round((answered / safeTotal) * 100));

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="text-[var(--color-muted)]">
          السيناريوهات المكتملة: {answered} من {total}
        </span>
        <span className="text-[var(--color-gold)] font-medium">{percent}%</span>
      </div>
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        className="h-2 w-full rounded-full bg-[var(--color-line)] overflow-hidden"
      >
        <div
          className="h-full rounded-full bg-[var(--color-gold)] transition-all duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
