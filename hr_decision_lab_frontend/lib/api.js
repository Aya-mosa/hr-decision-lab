const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export const LEVELS = [
  { id: "hr_operations", label: "المستوى الأول", subtitle: "الامتثال والسياسات" },
  { id: "hr_business_partner", label: "المستوى الثاني", subtitle: "البيانات والمواءمة مع الإدارات" },
  { id: "strategic_hr_leader", label: "المستوى الثالث", subtitle: "الاستراتيجية والشراكة مع الإدارة العليا" },
];

export const CATEGORIES = [
  { id: "employee_relations", label: "علاقات الموظفين" },
  { id: "performance", label: "الأداء الوظيفي" },
  { id: "recruitment", label: "التوظيف" },
  { id: "talent_management", label: "إدارة المواهب" },
  { id: "retention", label: "الاحتفاظ بالموظفين" },
  { id: "compensation", label: "التعويضات والرواتب" },
  { id: "business_partnering", label: "الشراكة مع الإدارات" },
  { id: "workforce_decisions", label: "قرارات القوى العاملة" },
  { id: "leadership", label: "القيادة" },
  { id: "hr_ethics", label: "أخلاقيات الموارد البشرية" },
  { id: "saudi_hr_practice", label: "ممارسات العمل المحلية" },
];

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `طلب فشل بالكود ${res.status}`);
  }
  return res.json();
}

export function newSessionId() {
  return crypto.randomUUID();
}

export function generateScenario(sessionId, level, category) {
  return fetch(`${API_BASE}/sessions/${sessionId}/scenarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ level, category }),
  }).then(handle);
}

export function submitDecision(sessionId, scenarioId, chosenOptionId) {
  return fetch(`${API_BASE}/sessions/${sessionId}/decisions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario_id: scenarioId, chosen_option_id: chosenOptionId }),
  }).then(handle);
}

export function getReport(sessionId) {
  return fetch(`${API_BASE}/sessions/${sessionId}/report`).then(handle);
}

export function shareResultByEmail(sessionId, toEmail, senderName) {
  return fetch(`${API_BASE}/sessions/${sessionId}/share-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to_email: toEmail, sender_name: senderName || "" }),
  }).then(handle);
}
