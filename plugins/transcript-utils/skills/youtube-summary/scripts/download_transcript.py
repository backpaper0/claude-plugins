# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "youtube-transcript-api>=1.2.4",
# ]
# ///

import argparse
import os
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="YouTube動画のトランスクリプトをダウンロード"
    )
    parser.add_argument("--vid", required=True, help="YouTube動画ID")
    parser.add_argument(
        "--lang", default="ja", help="トランスクリプトの言語 (デフォルト: ja)"
    )
    args = parser.parse_args()

    transcripts_path = os.getenv("TRANSCRIPTS_PATH")
    transcripts = (
        Path(transcripts_path)
        if transcripts_path
        else Path.home() / ".cache" / "transcripts"
    )
    file = transcripts / f"{args.vid}.vtt"

    if not file.exists():
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(args.vid, languages=[args.lang])

        formatter = WebVTTFormatter()
        vtt = formatter.format_transcript(fetched_transcript)

        if not transcripts.exists():
            transcripts.mkdir(parents=True)
        file.write_text(vtt)

    print(f"VTTファイルの保存先: {file.absolute()}")


if __name__ == "__main__":
    main()
