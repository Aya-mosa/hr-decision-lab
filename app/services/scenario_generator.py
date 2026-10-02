"""
Agent 1 — Scenario Generator.
"""
from __future__ import annotations
import json
from pathlib import Path
from pydantic import ValidationError
import requests

from app.schemas.models import Scenario, HRLevel, ScenarioCategory
from app.data.archetype_catalog import ARCHETYPES_BY_LEVEL, LEVEL_CRITERIA

BASE_TEMPLATE_PATH = Path(__file__).parent.parent / "prompts" / "scenario_generator_base_template.txt"
FEW_SHOTS_DIR = Path(__file__).parent.parent / "prompts" / "few_shots"

FEW_SHOT_FILE_BY_LEVEL = {
    HRLevel.OPERATIONS: "level1_example.json",
    HRLevel.BUSINESS_PARTNER: "level2_example.json",
    HRLevel.STRATEGIC_LEADER: "level3_example.json",
}


def load_system_prompt(level: HRLevel, category: ScenarioCategory) -> str:
    template = BASE_TEMPLATE_PATH.read_text(encoding="utf-8")
    archetype_list = ", ".join(ARCHETYPES_BY_LEVEL[level])
    criteria_list = ", ".join(f"{name} ({weight}%)" for name, weight in LEVEL_CRITERIA[level])
    few_shot_example = (FEW_SHOTS_DIR / FEW_SHOT_FILE_BY_LEVEL[level]).read_text(encoding="utf-8")
    return template.format(
        level=level.value, category=category.value,
        archetype_list=archetype_list, criteria_list=criteria_list,
        few_shot_example=few_shot_example,
    )


def _extract_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    decoder = json.JSONDecoder()
    obj, _end_index = decoder.raw_decode(text)
    return obj


OPENROUTER_MODEL = "google/gemini-2.5-flash"


def call_llm(system_prompt: str) -> str:
    import os
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Get a free key from https://openrouter.ai/keys"
        )
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.9,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response shape: {data}") from e
    if not content:
        raise RuntimeError(f"OpenRouter returned an empty response. Full response: {data}")
    return content


def generate_scenario(level: HRLevel, category: ScenarioCategory, max_retries: int = 2) -> Scenario:
    system_prompt = load_system_prompt(level, category)
    last_error = None

    for attempt in range(max_retries + 1):
        prompt = system_prompt
        if last_error:
            prompt += (
                f"\n\nمحاولتك السابقة فشلت بهذا الخطأ بالضبط:\n{last_error}\n"
                f"أعد إخراج نفس السيناريو بصيغة JSON صحيحة تمامًا، مصححًا هذا الخطأ فقط."
            )
        try:
            raw_output = call_llm(prompt)
        except (RuntimeError, requests.exceptions.RequestException) as e:
            last_error = str(e)
            if attempt == max_retries:
                raise RuntimeError(f"Scenario generation failed after {max_retries + 1} attempts: {last_error}") from e
            continue

        try:
            data = _extract_json(raw_output)
        except json.JSONDecodeError as e:
            last_error = f"JSON syntax error: {e}"
            if attempt == max_retries:
                raise ValueError(f"LLM output was not valid JSON after {max_retries + 1} attempts: {e}") from e
            continue

        try:
            return Scenario(**data)
        except ValidationError as e:
            last_error = str(e)
            if attempt == max_retries:
                raise ValueError(f"LLM output failed schema validation after {max_retries + 1} attempts: {e}") from e
