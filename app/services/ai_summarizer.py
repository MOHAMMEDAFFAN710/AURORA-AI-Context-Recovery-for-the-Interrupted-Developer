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
    parts.append("You are an expert software analyst. Your task is to provide a concise, one-paragraph summary of what this project does based on the provided file snippets.")
    parts.append("Do not include any information about recent commits, TODOs, or next steps. Only describe the project's primary function.")

    parts.append("\nHere are the key files:")
    for p, content in list(file_samples.items())[:5]:
        snippet = _truncate(content, 1000)
        parts.append(f"\nFile: {p}\n---\n{snippet}")

    parts.append("\nBased on these files, what does this project do? Provide only the summary paragraph.")

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


async def generate_explanations(file_samples: Dict[str, str], todos: List[Dict[str, Any]], git_summary: Dict[str, Any]) -> Tuple[str, str, List[Dict[str, str]]]:
    prompt = _build_prompt(file_samples, todos, git_summary)
    hf_text = await call_hf(_truncate(prompt, 8000))

    project_summary = hf_text.strip() if hf_text else "Could not generate a summary for this project."

    return project_summary, "", []
