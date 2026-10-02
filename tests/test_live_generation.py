"""
Live test — actually calls Gemini and generates a real scenario.
Run this on YOUR machine (not in the sandbox), after setting GEMINI_API_KEY.

Windows (PowerShell):
    $env:OPENROUTER_API_KEY="your_key_here"
    python tests/test_live_generation.py

Get a free key from: https://openrouter.ai/keys
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.models import HRLevel, ScenarioCategory
from app.services.scenario_generator import generate_scenario


def main():
    level = HRLevel.BUSINESS_PARTNER
    category = ScenarioCategory.PERFORMANCE

    print(f"Requesting a live scenario from Gemini: level={level.value}, category={category.value}")
    print("(this calls the real API — may take a few seconds)\n")

    scenario = generate_scenario(level, category)

    print(f"✅ Generated & validated: {scenario.title}\n")
    print(scenario.situation)
    print(f"\nSoal: {scenario.question}\n")
    for opt in scenario.options:
        print(f"  {opt.option_id}) {opt.text}")
        print(f"     tags: {[t.value for t in opt.behavior_tags]}")
    print("\n✅ Live generation + schema validation passed.")


if __name__ == "__main__":
    main()
