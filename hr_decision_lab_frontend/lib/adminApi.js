const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `طلب فشل بالكود ${res.status}`);
  }
  return res.json();
}

function authHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("admin_token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function adminSignup(email, password) {
  return fetch(`${API_BASE}/admin/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }).then(handle);
}

export async function adminLogin(email, password) {
  const data = await fetch(`${API_BASE}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }).then(handle);
  localStorage.setItem("admin_token", data.token);
  return data.token;
}

export function adminLogout() {
  localStorage.removeItem("admin_token");
}

export function isAdminLoggedIn() {
  return typeof window !== "undefined" && !!localStorage.getItem("admin_token");
}

export function createInvites(inviteType, invitees, deadline) {
  return fetch(`${API_BASE}/admin/invites`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ invite_type: inviteType, invitees, deadline: deadline || null }),
  }).then(handle);
}

export function listInvites() {
  return fetch(`${API_BASE}/admin/invites`, { headers: authHeaders() }).then(handle);
}

export function getInviteReport(inviteId) {
  return fetch(`${API_BASE}/admin/invites/${inviteId}/report`, { headers: authHeaders() }).then(handle);
}

export function getInviteInfo(inviteId) {
  return fetch(`${API_BASE}/invites/${inviteId}`).then(handle);
}

export function giveConsent(inviteId) {
  return fetch(`${API_BASE}/invites/${inviteId}/consent`, { method: "POST" }).then(handle);
}

export function generateInviteScenario(inviteId) {
  return fetch(`${API_BASE}/invites/${inviteId}/scenarios`, { method: "POST" }).then(handle);
}

export function submitInviteDecision(inviteId, scenarioId, chosenOptionId) {
  return fetch(`${API_BASE}/invites/${inviteId}/decisions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario_id: scenarioId, chosen_option_id: chosenOptionId }),
  }).then(handle);
}
