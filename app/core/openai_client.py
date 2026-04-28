import os
from typing import List
import openai
from ..config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key


async def embed_texts(texts: List[str]) -> List[List[float]]:
    if not settings.openai_api_key:
        return [[0.0] * 1536 for _ in texts]

    response = openai.Embedding.create(model="text-embedding-3-small", input=texts)
    return [item["embedding"] for item in response["data"]]


async def summarize_issue(root_cause: str, evidence: List[str]) -> str:
    if not settings.openai_api_key:
        return root_cause

    prompt = (
        "You are a backend debugging assistant. Summarize the root cause and explain why this issue occurred."
        "\n\nRoot cause:\n" + root_cause
        + "\n\nEvidence:\n" + "\n".join(evidence)
        + "\n\nResponse:"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=250,
    )
    return response["choices"][0]["message"]["content"].strip()
