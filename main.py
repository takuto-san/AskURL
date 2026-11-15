import argparse
import sys

from adapters import nosana, web
from triage import decide_action


def main() -> int:
    parser = argparse.ArgumentParser(description="URLの内容を読み、次の対応を提案する")
    parser.add_argument("url", help="公開ページのURL")
    args = parser.parse_args()

    try:
        page = web.read_page(args.url)
        print("ページ本文を取得しました。", file=sys.stderr)
        result = decide_action(page, nosana.complete)
    except (OSError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
