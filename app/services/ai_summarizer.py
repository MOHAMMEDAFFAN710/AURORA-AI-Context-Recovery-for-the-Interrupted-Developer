import json
from typing import Any, Dict, List, Tuple
import httpx
from app.config import settings


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _build_prompt(file_samples: Dict[str, str], todos: List[Dict[str, Any]], git_summary: Dict[str, Any]) -> str:
    parts: List[str] = []
    parts.append("You are an assistant that writes concise software project briefings.")
    parts.append("Summarize what the project does, what was recently worked on, and next steps.")
    if git_summary.get("repo_found"):
        parts.append("Recent commits:")
        for c in git_summary.get("commits", [])[:5]:
            parts.append(f"- {c['date']} {c['author']} {c['commit']} {c['message']}")
    if todos:
        parts.append("Unfinished work:")
        for t in todos[:20]:
            parts.append(f"- {t['kind']} {t['file_path']}:{t['line']} {t['text']}")
    parts.append("Key files:")
    for p, content in list(file_samples.items())[:5]:
        snippet = _truncate(content, 1200)
        parts.append(f"File: {p}\n{snippet}")
    parts.append("Return two sections: PROJECT_EXPLANATION and DEVELOPER_BRIEFING.")
    return "\n".join(parts)


async def call_hf(prompt: str) -> str:
    if not settings.hf_api_url or not settings.hf_api_key:
        return ""
    headers = {"Authorization": f"Bearer {settings.hf_api_key}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(settings.hf_api_url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        if isinstance(data, list) and data and isinstance(data[0], str):
            return data[0]
        if isinstance(data, str):
            return data
        return ""


async def generate_explanations(file_samples: Dict[str, str], todos: List[Dict[str, Any]], git_summary: Dict[str, Any]) -> Tuple[str, str]:
    prompt = _build_prompt(file_samples, todos, git_summary)
    hf_text = await call_hf(_truncate(prompt, 8000))
    if hf_text:
        text = hf_text
    else:
        next_steps: List[str] = []
        if todos:
            for t in todos[:5]:
                next_steps.append(f"- {t['kind']} in {t['file_path']} line {t['line']}: {t['text']}")
        recent = ", ".join([c["message"] for c in git_summary.get("commits", [])[:3]]) if git_summary.get("repo_found") else ""
        explanation = "This project contains source files and appears to be an active codebase."
        briefing_lines = []
        if recent:
            briefing_lines.append(f"Recent activity: {recent}")
        if next_steps:
            briefing_lines.append("Suggested next steps:")
            briefing_lines.extend(next_steps)
        text = f"PROJECT_EXPLANATION:\n{explanation}\n\nDEVELOPER_BRIEFING:\n" + ("\n".join(briefing_lines) or "Focus on the highest-priority TODOs.")
    if "PROJECT_EXPLANATION:" in text and "DEVELOPER_BRIEFING:" in text:
        parts = text.split("DEVELOPER_BRIEFING:", 1)
        proj = parts[0].replace("PROJECT_EXPLANATION:", "").strip()
        dev = parts[1].strip()
        return proj, dev
    return text.strip(), "Review TODOs and recent commits to plan next steps."
