import requests     # type: ignore
import json
import re
from typing import Dict, List

IAM_TOKEN = "..."
FOLDER_ID = "..."
MODEL_URI = "..."
API_URL   = "..."


def clean_text(text: str) -> str:
    cleaned = re.sub(r"[\u200e\u200f\u202a-\u202e\u2060\uFEFF]", "", text)
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
    return cleaned.strip()


def _call_gpt(system_prompt: str, user_prompt: str,
              *, temperature: float = 0.2, max_tokens: int = 300) -> str:
    payload = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user",   "text": user_prompt}
        ]
    }
    headers = {
        "Authorization": f"Api-Key {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["result"]["alternatives"][0]["message"]["text"].strip()

def analyze_email(text: str) -> Dict[str, str | List[str]]:
    system_prompt = (
        "Ты помощник, который анализирует письмо и возвращает JSON с тремя полями:\n"
        "summary — одно короткое предложение о сути письма на русском;\n"
        "tasks   — список (1‑3) задач/действий для пользователя, на русском;\n"
        "reply   — вежливый русский ответ на письмо.\n"
        "Верни только JSON, без форматирования и комментариев."
    )
    user_prompt = (
        "Проанализируй письмо ниже и выдай JSON с ключами summary, tasks, reply.\n\n"
        f"Письмо:\n{text.strip()}"
    )

    raw = _call_gpt(system_prompt, user_prompt)

    try:
        json_text = re.search(r"\{.*\}", raw, flags=re.DOTALL).group(0)  # type: ignore
        parsed = json.loads(json_text)
        if isinstance(parsed.get("tasks"), str):
            parsed["tasks"] = [parsed["tasks"]]
        return {
            "summary": parsed.get("summary", ""),
            "tasks":   parsed.get("tasks", []),
            "reply":   parsed.get("reply", "")
        }
    except Exception:
        return {
            "summary": "(не удалось распарсить)",
            "tasks":   [],
            "reply":   raw
        }
