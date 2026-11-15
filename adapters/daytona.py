import json
import os
import shlex
import sys
from collections.abc import Callable
from pathlib import Path

from adapters import web


def read_page(url: str, *, on_started: Callable[[str], None] | None = None) -> str:
    if not os.environ.get("DAYTONA_API_KEY", "").strip():
        raise ValueError("DAYTONA_API_KEY を実行環境に設定してください。")
    try:
        from daytona import CreateSandboxFromSnapshotParams, Daytona, DaytonaError
    except ImportError as exc:
        raise OSError("Docker build 時に --build-arg INSTALL_DAYTONA=1 を指定してください。") from exc

    # Run the same extractor inside Daytona, passing the URL as an argument.
    source = Path(web.__file__).read_text(encoding="utf-8")
    source += "\nimport json, sys\nprint(json.dumps(read_page(sys.argv[1])))\n"
    command = shlex.join(["python3", "-c", source, url])
    try:
        client = Daytona()
        sandbox = client.create(
            CreateSandboxFromSnapshotParams(ephemeral=True, auto_stop_interval=5, public=False),
            timeout=60,
        )
        try:
            if on_started is not None:
                on_started(sandbox.id)
            response = sandbox.process.exec(command, timeout=35)
        finally:
            try:
                client.delete(sandbox, timeout=15)
            except DaytonaError:
                print(f"Daytona のサンドボックス {sandbox.id} の削除を確認できませんでした。", file=sys.stderr)
    except DaytonaError as exc:
        raise OSError(f"Daytona での処理に失敗しました（{type(exc).__name__}）。") from exc

    if response.exit_code != 0:
        last_line = response.result.strip().splitlines()[-1:] if response.result else []
        detail = last_line[0] if last_line else f"終了コード {response.exit_code}"
        raise OSError(f"Daytona でページを取得できませんでした（{detail}）。")
    try:
        page = json.loads(response.result)
    except json.JSONDecodeError as exc:
        raise OSError("Daytona の本文取得結果を読み込めませんでした。") from exc
    if not isinstance(page, str) or not page.strip():
        raise OSError("Daytona からページ本文が返りませんでした。")
    return page
