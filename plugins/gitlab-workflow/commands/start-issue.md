---
allowed-tools: Bash(git:*), Bash(glab:*), Read, Grep, Glob
---

# GitLab Issue から実装を開始

GitLab issueの内容を読み取り、対応するブランチを作成して実装を開始する。

引数としてissue番号（IID）を受け取る: `$ARGUMENTS`

- 引数がない場合はユーザーにissue番号の入力を求める

## 手順

### 1. 情報収集（並列実行）

以下のコマンドを**並列で**実行する:

- `git status` — 未コミット変更の確認
- `git remote -v` — リモート情報の取得（project-pathの抽出用）
- `git rev-parse --abbrev-ref HEAD` — 現在のブランチ確認
- `glab api projects/<project-path>/issues/<iid>` — issueの詳細取得

`<project-path>` はリモートURLから判別する（`/` は `%2F` にエンコードする）。

### 2. 検証

- 未コミット変更がある場合 → 「未コミットの変更があります。先にコミットまたはスタッシュしてください」と案内して**終了**
- issueが存在しない場合 → 「Issue #<iid> が見つかりません」と通知して**終了**
- issueが `closed` の場合 → 「Issue #<iid> はクローズ済みです」と警告して**終了**

### 3. issue内容の分析・表示

issueの情報をユーザーに表示する:

```
## Issue #<iid>: <title>

**ラベル**: <labels>

### 説明
<description>
```

issueの内容を分析し、実装すべき内容を整理して提示する。

### 4. ブランチの作成

1. ブランチ名を自動生成する: `feature/<iid>-<title-slug>`
   - タイトルからスラッグを生成する方法:
     - 小文字化
     - スペース・アンダースコアをハイフンに変換
     - 英数字とハイフン以外の文字を除去（日本語等も除去）
     - 連続するハイフンを1つに統合
     - 先頭・末尾のハイフンを除去
     - 50文字に制限
2. 提案したブランチ名をユーザーに確認する
3. mainブランチの最新を取得してブランチを作成する:

```
git fetch origin && git switch -c <branch-name> origin/main
```

### 5. 実装の開始

1. issue内容に基づいてコードベースを調査・分析する
   - 関連するファイルをGlob・Grep・Readで探索する
   - 既存のコードパターンやアーキテクチャを理解する
2. 実装方針をユーザーに提示する
3. **ユーザーの承認を得てから**実装を開始する
4. 実装完了後、変更したファイルを個別に `git add` でステージングしてコミットする:

```
git commit -m "$(cat <<'EOF'
<実装内容を簡潔に日本語で記述>

Refs #<iid>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### 6. 完了報告

実装完了後、以下の表形式でサマリーを報告する:

| 項目 | 内容 |
|------|------|
| Issue | #<iid> <title> |
| ブランチ | <branch-name> |
| 実装内容 | <実装した内容の要約> |
| コミット | <short-hash> <commit-message> |

次のアクションをサジェストする:

- `/create-mr` — Merge Requestを作成してレビューを依頼

## 注意事項

- リモートへのpushは自動では行わない（`/create-mr` コマンドに任せる）
- 実装方針は必ずユーザーの承認を得てから着手する
- 実装中に不明点がある場合はユーザーに確認する
- `glab` コマンドが利用できない場合は、インストール方法を案内する（miseでのインストールを推奨）
