# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Claude Code用の自作プラグインをホスティングするマーケットプレイスリポジトリ。

## 開発コマンド

開発環境は`mise`で管理（Python 3.14 + uv）。

```bash
# Pythonコードのフォーマット・Lint自動修正
mise run fix

# フォーマット検証・Lint・型チェック
mise run check

# 特定ファイルのみ対象
mise run fix plugins/transcript-utils/skills/youtube-summary/scripts/get_title.py
mise run check plugins/transcript-utils/skills/youtube-summary/scripts/get_title.py
```

## アーキテクチャ

### マーケットプレイス構成

`.claude-plugin/marketplace.json`がマーケットプレイスの定義ファイル。`plugins`配列に各プラグインの`name`と`source`パスを登録する。

### プラグイン構造

各プラグインは`plugins/<plugin-name>/`配下に以下の構成を持つ:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # メタデータ（name, version, keywords）
├── README.md
├── commands/                # コマンド定義（.mdファイル）
└── skills/                  # スキル定義
    └── <skill-name>/
        ├── SKILL.md         # スキル定義ファイル
        └── scripts/         # ヘルパースクリプト
```

- **コマンド** (`commands/*.md`): YAML front matterで`allowed-tools`を定義。ユーザーが明示的に呼び出すワークフロー。
- **スキル** (`skills/*/SKILL.md`): YAML front matterで`name`, `description`, `args`, `allowed-tools`を定義。条件に応じて自動的に呼び出される機能。

### 現在のプラグイン

| プラグイン | 種類 | 概要 |
|---|---|---|
| git-operations | commands | 変更を論理単位で複数コミットに分割 |
| gitlab-workflow | commands | GitLab MRの作成・レビュー対応・返信 |
| transcript-utils | skills | YouTube動画のトランスクリプト取得・要約 |

## 規約

- **言語**: ドキュメント・コミットメッセージ・ユーザー向けテキストはすべて日本語
- **コミットメッセージ**: 日本語で記述し、`Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`フッターを付加
- **Pythonスクリプト**: PEP 723のインラインスクリプトメタデータを使用（`pyproject.toml`不要）
- **コード品質**: ruff（フォーマット・Lint）+ ty（型チェック）
