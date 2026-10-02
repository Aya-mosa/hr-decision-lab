"""
Tests the full API layer without hitting a real LLM — call_llm is
monkeypatched to return a fixed, valid scenario JSON.

Run: python tests/test_api_offline.py
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.services import scenario_generator as sg

MOCK_SCENARIO_JSON = json.dumps({
    "scenario_id": "sc_mock_001",
    "level": "hr_business_partner",
    "category": "retention",
    "title": "test scenario",
    "situation": "situation text",
    "question": "question text",
    "options": [
        {"option_id": "A", "text": "opt a", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Quick-Fix Manager"},
        {"option_id": "B", "text": "opt b", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "HR Functional Expert"},
        {"option_id": "C", "text": "opt c", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Data-Driven Analyst"},
        {"option_id": "D", "text": "opt d", "immediate_result": "r", "long_term_consequences": ["c"],
         "archetype_label": "Business Partner"},
    ],
})


def mock_call_llm(system_prompt: str) -> str:
    return MOCK_SCENARIO_JSON


def main():
    sg.call_llm = mock_call_llm  # monkeypatch — no real API call happens

    from app.api.main import app
    client = TestClient(app)

    session_id = "test_session_api"

    resp = client.post(f"/sessions/{session_id}/scenarios", json={
        "level": "hr_business_partner", "category": "retention",
    })
    assert resp.status_code == 200, resp.text
    scenario = resp.json()
    print(f"[1] POST /scenarios -> 200 OK, scenario_id={scenario['scenario_id']}")

    resp = client.post(f"/sessions/{session_id}/decisions", json={
        "scenario_id": scenario["scenario_id"], "chosen_option_id": "C",
    })
    assert resp.status_code == 200, resp.text
    print(f"[2] POST /decisions -> 200 OK, archetype={resp.json()['archetype_label']}")

    resp = client.get(f"/sessions/{session_id}/report")
    assert resp.status_code == 200, resp.text
    report = resp.json()
    print(f"[3] GET /report -> 200 OK, dominant_archetype={report['dominant_archetype']}")

    print("\n✅ Full API pipeline test passed (generate -> decide -> report).")


if __name__ == "__main__":
    main()
