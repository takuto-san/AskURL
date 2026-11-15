import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://inference.nosana.com/v1"


def request_json(path: str, key: str, payload: dict | None = None) -> dict:
    request = Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=45) as response:
            return json.load(response)
    except HTTPError as exc:
        raise OSError(f"Nosana API {path} が HTTP {exc.code} を返しました。") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OSError(f"Nosana API {path} から応答を受け取れませんでした。") from exc


def complete(instruction: str, page: str) -> str:
    key = os.environ.get("NOSANA_API_KEY", "").strip()
    if not key:
        raise ValueError("NOSANA_API_KEY を実行環境に設定してください。")

    model = os.environ.get("NOSANA_MODEL", "").strip()
    if not model:
        models = request_json("/models", key).get("data", [])
        if not models:
            raise ValueError("Nosanaで現在利用できるモデルが見つかりませんでした。")
        model = models[0]["id"]

    result = request_json("/chat/completions", key, {
        "model": model,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": page},
        ],
    })
    choices = result.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Nosanaから回答本文が返りませんでした。NOSANA_MODEL を変更して試してください。")
    return content.strip()
