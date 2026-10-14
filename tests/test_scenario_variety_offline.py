"""
Offline test: scenarios inside one survey must not repeat.

Mimics the real frontend order (prefetch the next scenario while the current one
is still unanswered) with call_llm monkeypatched, and checks that
  1. every scenario in a 10-scenario invite session gets a different category,
  2. the prompt sent to the model lists the scenarios already seen
     (including the one currently shown but not answered yet),
  3. a scenario that is too similar to a previous one is regenerated.

Run: python tests/test_scenario_variety_offline.py
"""
import os
import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DB_FILE = Path("test_variety.db")
os.environ["DATABASE_URL"] = f"sqlite:///./{DB_FILE}"
os.environ["ALLOW_ADMIN_SIGNUP"] = "true"
if DB_FILE.exists():
    DB_FILE.unlink()

from fastapi.testclient import TestClient
from app.services import scenario_generator as sg

prompts: list[str] = []
counter = {"n": 0}
force_duplicate_once = {"title": None}


def mock_call_llm(system_prompt: str) -> str:
    prompts.append(system_prompt)
    category = re.search(r"\ncategory: (\w+)", system_prompt).group(1)
    if force_duplicate_once["title"]:
        title = force_duplicate_once["title"]
        force_duplicate_once["title"] = None
        situation = "موقف مكرر بالنص نفسه تقريبا"
    else:
        counter["n"] += 1
        title = f"عنوان فريد رقم {counter['n']} {'x' * counter['n']}"
        situation = f"موقف مختلف تمامًا رقم {counter['n']} " + "ب" * (counter["n"] * 7)
    return json.dumps({
        "scenario_id": f"sc_{counter['n']}_{len(prompts)}",
        "level": "hr_operations",
        "category": category,
        "title": title,
        "situation": situation,
        "question": "ماذا ستفعل؟",
        "options": [
            {"option_id": o, "text": f"خيار {o}", "immediate_result": "r", "long_term_consequences": ["c"],
             "archetype_label": a}
            for o, a in zip("ABCD", ["Compliance Guardian", "Evidence Seeker",
                                      "Balanced Practitioner", "Employee Advocate"])
        ],
    }, ensure_ascii=False)


def main():
    sg.call_llm = mock_call_llm
    from app.api.main import app
    client = TestClient(app)

    client.post("/admin/signup", json={"email": "m@test.com", "password": "secret123"})
    token = client.post("/admin/login", json={"email": "m@test.com", "password": "secret123"}).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/admin/invites", headers=headers, json={
        "invite_type": "team_member",
        "invitees": [{"email": "e@test.com", "name": "x", "level": "hr_operations"}],
    })
    invite_id = client.get("/admin/invites", headers=headers).json()[0]["id"]

    # --- invite flow, in the same order as the frontend: first scenario, then prefetch next ---
    categories, titles = [], []
    first = client.post(f"/invites/{invite_id}/scenarios", json={"current_scenario_id": None}).json()
    current = first["scenario"]
    for n in range(1, 11):
        categories.append(current["category"])
        titles.append(current["title"])
        nxt = None
        if n < 10:  # prefetch while `current` is still unanswered
            nxt = client.post(f"/invites/{invite_id}/scenarios",
                              json={"current_scenario_id": current["scenario_id"]}).json()["scenario"]
            last_prompt = prompts[-1]
            assert current["title"] in last_prompt, "avoid-list must include the scenario currently shown"
        done = client.post(f"/invites/{invite_id}/decisions",
                           json={"scenario_id": current["scenario_id"], "chosen_option_id": "A"}).json()
        assert done["scenario_number"] == n
        if nxt:
            current = nxt
    assert done["completed"] is True
    assert len(set(categories)) == 10, f"categories repeated: {categories}"
    assert len(set(titles)) == 10
    print(f"[1] invite flow: 10 scenarios, 10 distinct categories -> {categories}")
    print("[2] every prefetch prompt contained the scenarios already shown")

    # --- public flow: client sends `previous`; a near-duplicate result is regenerated ---
    before = len(prompts)
    force_duplicate_once["title"] = "طلب إنذار نهائي لموظف"
    resp = client.post("/sessions/s1/scenarios", json={
        "level": "hr_operations", "category": "retention",
        "previous": [{"title": "طلب إنذار نهائي لموظف", "situation": "موقف مكرر بالنص نفسه تقريبا"}],
    })
    assert resp.status_code == 200, resp.text
    assert len(prompts) - before == 2, "duplicate should trigger exactly one regeneration"
    assert resp.json()["title"] != "طلب إنذار نهائي لموظف"
    assert "طلب إنذار نهائي لموظف" in prompts[before]
    print("[3] near-duplicate scenario was regenerated (2 model calls)")

    print("\n✅ Scenario variety test passed.")


if __name__ == "__main__":
    try:
        main()
    finally:
        if DB_FILE.exists():
            DB_FILE.unlink()
