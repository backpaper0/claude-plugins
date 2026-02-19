---
name: youtube-summary
description: YouTube動画のトランスクリプトを取得して内容を要約する。YouTube URLまたは動画IDが指定された場合に使用する。
args:
  video:
    description: YouTube動画のURL（例：https://www.youtube.com/watch?v=xxxxx）または動画ID
    required: true
  lang:
    description: 字幕の言語コード（例：ja, en）。デフォルトはja
    required: false
allowed-tools: Read, Bash, Write
disable-model-invocation: true
context: fork
---

# YouTube動画要約

## 1. 動画IDの抽出

{{video}} にYouTube動画のURLが渡された場合、そのURLから動画IDを抽出する。
{{video}} に動画IDが渡された場合は何もせず次へ進む。

## 2. 動画のタイトルを取得

Pythonスクリプトを使用してYouTube動画のタイトルを取得する。
スクリプトのパスは、このスキルのBase directoryからの相対パスで解決すること。

```bash
uv run --script {{Base directory}}/scripts/get_title.py --vid "{{動画ID}}"
```

## 3. トランスクリプトのダウンロード

Pythonスクリプトを使用してYouTube動画のトランスクリプトをVTT形式でダウンロードする。
スクリプトのパスは、このスキルのBase directoryからの相対パスで解決すること。

言語コード: {{lang}} （指定がない場合は `ja` を使用）

```bash
uv run --script {{Base directory}}/scripts/download_transcript.py --vid "{{動画ID}}" --lang "{{lang}}"
```

注意：
- 字幕が見つからない場合は、別の言語（en等）で再試行

## 4. VTTファイルの読み取り

保存されたVTTファイルを読み取る。

VTTファイルの形式：
```
WEBVTT

00:00:00.000 --> 00:00:05.000
テキスト行1

00:00:05.000 --> 00:00:10.000
テキスト行2
```

## 3. 内容の要約

トランスクリプトの内容を以下の形式で要約する：

### 要約の構成

1. **概要**（2-3文）
   - 動画の主題と目的を簡潔に説明

2. **主要なポイント**（箇条書き、5-10項目）
   - 動画で述べられている重要な情報やアイデア
   - 具体的な数字やデータがあれば含める

3. **詳細な内容**（セクション別）
   - 動画の流れに沿って主要なトピックをセクション分け
   - 各セクションに見出しと要約を記載

4. **結論・まとめ**
   - 動画の結論や視聴者へのメッセージ

### 要約時の注意点

- 話者の意図を正確に反映する
- 専門用語は文脈から適切に解釈する
- 冗長な表現や繰り返しは省略する
- 時系列の情報は整理して論理的に構成する

## 出力

次のファイルへ要約結果を出力する。

-  `$PWD/{{動画のタイトル}}_{{動画ID}}.md` 

注意：
- {{動画のタイトル}}はスラッシュを含む場合があるため、サブディレクトリへ出力しないよう注意すること