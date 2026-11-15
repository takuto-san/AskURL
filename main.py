import argparse
import sys

from adapters import daytona, nosana, web
from triage import decide_action


def main() -> int:
    parser = argparse.ArgumentParser(description="URLの内容を読み、次の対応を提案する")
    parser.add_argument("url", help="公開ページのURL")
    parser.add_argument("--daytona", action="store_true", help="Daytona のサンドボックスで本文を取得する")
    args = parser.parse_args()

    try:
        if args.daytona:
            page = daytona.read_page(args.url)
            print("Daytona でページ本文を取得しました。", file=sys.stderr)
        else:
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
