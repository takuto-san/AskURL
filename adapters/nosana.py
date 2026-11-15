import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

BASE_URL = "https://inference.nosana.com/v1"


def request_json(
    base_url: str, path: str, key: str, payload: dict | None = None, *, timeout: int = 45
) -> dict:
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        raise OSError(f"Nosana API {path} が HTTP {exc.code} を返しました。") from exc
    except TimeoutError as exc:
        raise OSError(f"Nosana API {path} が {timeout} 秒以内に応答しませんでした。") from exc
    except (URLError, json.JSONDecodeError) as exc:
        raise OSError(f"Nosana API {path} から応答を受け取れませんでした。") from exc


def complete(instruction: str, page: str) -> str:
    service_url = os.environ.get("NOSANA_SERVICE_URL", "").strip().rstrip("/")
    if service_url:
        parsed = urlsplit(service_url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("NOSANA_SERVICE_URL に Nosana デプロイの HTTPS URL を設定してください。")
        base_url = service_url if parsed.path.endswith("/v1") else f"{service_url}/v1"
        key = ""
    else:
        base_url = BASE_URL
        key = os.environ.get("NOSANA_API_KEY", "").strip()
        if not key:
            raise ValueError("NOSANA_SERVICE_URL または NOSANA_API_KEY を実行環境に設定してください。")

    model = os.environ.get("NOSANA_MODEL", "").strip()
    if not model:
        models = request_json(base_url, "/models", key).get("data", [])
        if not models:
            raise ValueError("Nosanaで現在利用できるモデルが見つかりませんでした。")
        model = models[0]["id"]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": page},
        ],
    }
    timeout = 45
    if service_url:
        payload.update(reasoning_effort="none", max_tokens=256)
        timeout = 120
    result = request_json(base_url, "/chat/completions", key, payload, timeout=timeout)
    choices = result.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Nosanaから回答本文が返りませんでした。NOSANA_MODEL を変更して試してください。")
    return content.strip()
