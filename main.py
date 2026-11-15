import argparse
import sys
import tomllib
from pathlib import Path

from adapters import daytona, nosana, web


PROMPTS_PATH = Path(__file__).with_name("config") / "prompts.toml"


def load_prompt(language: str) -> str:
    with PROMPTS_PATH.open("rb") as config:
        instruction = tomllib.load(config).get(language)
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError(f"Missing prompt for language: {language}")
    return instruction.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="URLの内容を読み、次の対応を提案する")
    parser.add_argument("url", help="公開ページのURL")
    parser.add_argument("--daytona", action="store_true", help="Daytona のサンドボックスで本文を取得する")
    parser.add_argument("--language", choices=("ja", "en"), default="ja", help="回答の言語")
    args = parser.parse_args()
    english = args.language == "en"

    def show_sandbox(sandbox_id: str) -> None:
        print(f"[Daytona] Started temporary sandbox {sandbox_id[:8]}...", file=sys.stderr)

    try:
        if args.daytona:
            page = daytona.read_page(args.url, on_started=show_sandbox if english else None)
            message = "[Daytona] Fetched and extracted the page inside the sandbox." if english else "Daytona でページ本文を取得しました。"
        else:
            page = web.read_page(args.url)
            message = "[AskURL] Fetched the page." if english else "ページ本文を取得しました。"
        print(message, file=sys.stderr)
        if english:
            print("[Nosana] Generating a response from the extracted text.", file=sys.stderr)
        result = nosana.complete(load_prompt(args.language), page)
    except (OSError, ValueError) as exc:
        print(f"{'Error' if english else 'エラー'}: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
