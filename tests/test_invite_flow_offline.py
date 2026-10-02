"""
Offline test of the invite/campaign flow (Type 3 & 4), with call_llm
monkeypatched so no real network/API key is needed.

Run: python tests/test_invite_flow_offline.py
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.services import scenario_generator as sg

MOCK_SCENARIO_JSON = json.dumps({
    "scenario_id": "sc_mock_invite",
    "level": "hr_operations",
    "category": "employee_relations",
    "title": "test scenario",
    "situation": "situation text",
    "question": "question text",
    "options": [
        {"option_id": "A", "text": "opt a", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Compliance Guardian"},
        {"option_id": "B", "text": "opt b", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Evidence Seeker"},
        {"option_id": "C", "text": "opt c", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Balanced Practitioner"},
        {"option_id": "D", "text": "opt d", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Employee Advocate"},
    ],
})


def mock_call_llm(system_prompt: str) -> str:
    return MOCK_SCENARIO_JSON


def main():
    sg.call_llm = mock_call_llm

    from app.api.main import app
    client = TestClient(app)

    # 1. Admin signs up and logs in
    resp = client.post("/admin/signup", json={"email": "manager@test.com", "password": "secret123"})
    assert resp.status_code == 200, resp.text
    print("[1] Admin signup -> 200 OK")

    resp = client.post("/admin/login", json={"email": "manager@test.com", "password": "secret123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2] Admin login -> 200 OK, token issued")

    # 2. Admin creates an invite batch of 1 team member
    resp = client.post("/admin/invites", headers=headers, json={
        "invite_type": "team_member",
        "invitees": [{"email": "employee@test.com", "name": "محمد", "level": "hr_operations"}],
    })
    assert resp.status_code == 200, resp.text
    batch_id = resp.json()["batch_id"]
    print(f"[3] POST /admin/invites -> 200 OK, batch_id={batch_id}")

    resp = client.get("/admin/invites", headers=headers)
    assert resp.status_code == 200, resp.text
    invite_id = resp.json()[0]["id"]
    print(f"[4] GET /admin/invites -> 200 OK, invite_id={invite_id}, status={resp.json()[0]['status']}")

    # 3. Invitee opens the link and checks invite info (no auth needed)
    resp = client.get(f"/invites/{invite_id}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["requires_consent"] is False  # team_member, not candidate
    print(f"[5] GET /invites/{{id}} -> 200 OK, level={resp.json()['level']}")

    # 4. Invitee answers 10 scenarios with NO feedback returned
    for i in range(10):
        resp = client.post(f"/invites/{invite_id}/scenarios")
        assert resp.status_code == 200, resp.text
        scenario_id = resp.json()["scenario"]["scenario_id"]

        resp = client.post(f"/invites/{invite_id}/decisions", json={
            "scenario_id": scenario_id, "chosen_option_id": "C",
        })
        assert resp.status_code == 200, resp.text
        body = resp.json()
        # THE KEY ASSERTION: no feedback fields leak through this endpoint
        assert "immediate_result" not in body, "Feedback leaked in Type 3/4 flow!"
        assert "archetype_label" not in body, "Feedback leaked in Type 3/4 flow!"

    assert body["completed"] is True
    print(f"[6] Answered {SCENARIOS_PER_ASSESSMENT if False else 10} scenarios -> "
          f"no feedback ever returned, completed=True on the 10th")

    # 5. Admin checks the invite is now completed and can view the report
    resp = client.get("/admin/invites", headers=headers)
    assert resp.json()[0]["status"] == "completed"
    print("[7] GET /admin/invites -> status is now 'completed'")

    resp = client.get(f"/admin/invites/{invite_id}/report", headers=headers)
    assert resp.status_code == 200, resp.text
    report = resp.json()
    print(f"[8] GET /admin/invites/{{id}}/report -> 200 OK, dominant_archetype={report['dominant_archetype']}")

    print("\n✅ Full invite flow test passed: signup -> login -> invite -> "
          "10 feedback-free answers -> completion -> admin report.")


if __name__ == "__main__":
    main()
