import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.services import scenario_generator as sg

MOCK = json.dumps({
    "scenario_id": "sc1", "level": "hr_operations", "category": "employee_relations",
    "title": "t", "situation": "s", "question": "q",
    "options": [
        {"option_id": "A", "text": "a", "immediate_result": "r", "long_term_consequences": ["c"], "archetype_label": "Compliance Guardian"},
        {"option_id": "B", "text": "b", "immediate_result": "r", "long_term_consequences": ["c"], "archetype_label": "Evidence Seeker"},
        {"option_id": "C", "text": "c", "immediate_result": "r", "long_term_consequences": ["c"], "archetype_label": "Balanced Practitioner"},
        {"option_id": "D", "text": "d", "immediate_result": "r", "long_term_consequences": ["c"], "archetype_label": "Employee Advocate"},
    ],
})

def mock_call_llm(p): return MOCK
sg.call_llm = mock_call_llm

from app.api.main import app
client = TestClient(app)

# Single-player flow + Type 2 share
r = client.post("/sessions/s1/scenarios", json={"level": "hr_operations", "category": "employee_relations"})
assert r.status_code == 200, r.text
r = client.post("/sessions/s1/decisions", json={"scenario_id": "sc1", "chosen_option_id": "C"})
assert r.status_code == 200, r.text
r = client.get("/sessions/s1/report")
assert r.status_code == 200, r.text
print("[1] Single-player flow OK, dominant:", r.json()["dominant_archetype"])

r = client.post("/sessions/s1/share-email", json={"to_email": "friend@test.com", "sender_name": "Aya"})
# email not configured -> expect 502, which is the correct behavior, not a crash
assert r.status_code == 502, r.text
print("[2] share-email correctly reports 502 (SMTP not configured) instead of crashing")

# Admin + invite flow
r = client.post("/admin/signup", json={"email": "m@test.com", "password": "secret123"})
assert r.status_code == 200, r.text
r = client.post("/admin/login", json={"email": "m@test.com", "password": "secret123"})
token = r.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
r = client.post("/admin/invites", headers=headers, json={
    "invite_type": "team_member", "invitees": [{"email": "e@test.com", "name": "X", "level": "hr_operations"}],
})
assert r.status_code == 200, r.text
r = client.get("/admin/invites", headers=headers)
invite_id = r.json()[0]["id"]
for i in range(10):
    r = client.post(f"/invites/{invite_id}/scenarios")
    sid = r.json()["scenario"]["scenario_id"]
    r = client.post(f"/invites/{invite_id}/decisions", json={"scenario_id": sid, "chosen_option_id": "C"})
    assert "immediate_result" not in r.json()
assert r.json()["completed"] is True
r = client.get(f"/admin/invites/{invite_id}/report", headers=headers)
assert r.status_code == 200, r.text
print("[3] Full invite flow OK, dominant:", r.json()["dominant_archetype"])

print("\n✅ All smoke tests passed.")
