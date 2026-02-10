# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "requests>=2.32.5",
# ]
# ///
import argparse

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube動画のタイトルを取得")
    parser.add_argument("--vid", required=True, help="YouTube動画ID")
    args = parser.parse_args()
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={args.vid}&format=json"
    resp = requests.get(url)
    body = resp.json()
    title = body["title"]
    print(f"動画のタイトル: {title}")


if __name__ == "__main__":
    main()
