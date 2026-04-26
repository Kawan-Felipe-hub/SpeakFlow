from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class TutorLLMResult:
    reply_text: str
    corrections: list[str]
    vocab_suggestions: list[dict[str, str]]  # [{front, back}]
    raw: dict[str, Any]


def build_tutor_user_prompt(*, transcript: str) -> str:
    return (
        "Transcrição do aluno (em inglês, pode ter erros):\n"
        f"{transcript}\n\n"
        "Responda seguindo o formato JSON solicitado."
    )


async def groq_chat_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    messages: list[dict[str, str]],
    timeout_s: float = 20.0,
) -> dict[str, Any]:
    """
    Calls Groq Chat Completions API and returns parsed JSON from assistant content.
    We instruct the model to return a strict JSON object.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model,
        "temperature": 0.6,
        "messages": [{"role": "system", "content": system_prompt}, *messages],
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except Exception:
        # fallback: return raw content
        return {"reply_text": str(content), "corrections": [], "vocab_suggestions": [], "_raw": data}


async def tutor_reply(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    history: list[dict[str, str]],
    transcript: str,
) -> TutorLLMResult:
    """
    Returns the tutor response + corrections + vocab suggestions.
    history is a list of {role: user|assistant, content: ...} for context.
    """
    user_msg = {"role": "user", "content": build_tutor_user_prompt(transcript=transcript)}
    obj = await groq_chat_json(
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        messages=[*history, user_msg],
    )

    reply_text = str(obj.get("reply_text") or "").strip()
    corrections = obj.get("corrections") or []
    if not isinstance(corrections, list):
        corrections = []
    corrections = [str(x) for x in corrections][:5]

    vocab = obj.get("vocab_suggestions") or []
    vocab_suggestions: list[dict[str, str]] = []
    if isinstance(vocab, list):
        for item in vocab:
            if not isinstance(item, dict):
                continue
            front = str(item.get("front") or "").strip()
            back = str(item.get("back") or "").strip()
            if front and back:
                vocab_suggestions.append({"front": front, "back": back})

    return TutorLLMResult(
        reply_text=reply_text,
        corrections=corrections,
        vocab_suggestions=vocab_suggestions,
        raw=obj,
    )

