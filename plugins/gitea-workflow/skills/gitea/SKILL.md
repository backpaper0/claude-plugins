---
name: gitea
description: Gitea APIを使ってプルリクエストの作成やレビューコメントの取得を行う。PRの作成、レビューコメントの確認・返信などGitea操作全般に使用する。
---

# Gitea 操作スキル

このプロジェクトではGitHubではなく**Gitea**をGitホスティングとして使用している。`gh` CLIは利用できないため、すべての操作はGitea REST APIで行う。

## 接続情報の取得

認証情報は環境変数から取得する:
- **ユーザー名**: `GITEA_USERNAME`
- **アクセストークン**: `GITEA_TOKEN`
- **パスワード**: `GITEA_PASSWORD`

APIのベースURLは `git remote get-url origin` の出力から取得する。

```
http://<host>:<port>/<owner>/<repo>.git
```

この情報から以下を組み立てる:
- **API Base**: `http://${GITEA_USERNAME}:${GITEA_TOKEN}@<host>:<port>/api/v1`
- **Owner/Repo**: URLパスから `<owner>/<repo>` を抽出

以降の例では以下の変数を使う:
```
API=http://${GITEA_USERNAME}:${GITEA_TOKEN}@<host>:<port>/api/v1
OWNER_REPO=<owner>/<repo>
```

## プルリクエストの作成

### 手順

1. フィーチャーブランチを作成してプッシュする
2. Gitea APIでPRを作成する

### API

```
POST ${API}/repos/${OWNER_REPO}/pulls
Content-Type: application/json
```

### リクエストボディ

```json
{
  "title": "PRタイトル (70文字以内)",
  "body": "## Summary\n- 変更点1\n- 変更点2\n\n## Test plan\n- [ ] テスト項目\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)",
  "head": "feature-branch-name",
  "base": "main"
}
```

### 実行例

```bash
curl -s -X POST "${API}/repos/${OWNER_REPO}/pulls" \
  -H "Content-Type: application/json" \
  -d '{"title":"...","body":"...","head":"feature-branch","base":"main"}'
```

### レスポンスから取得すべき値

- `html_url`: PRのURL（ユーザーに返す）
- `number`: PR番号（以降のAPI呼び出しで使用）

### 注意事項

- ブランチをpushした際にGiteaが自動でPRを作成する場合がある。`"pull request already exists"` エラーが返ったら、既存PRの一覧を取得して更新する:
  ```
  GET ${API}/repos/${OWNER_REPO}/pulls?state=open
  PATCH ${API}/repos/${OWNER_REPO}/pulls/{index}
  ```

## レビューコメントの取得

### 手順

1. PRのレビュー一覧を取得
2. 各レビューのコメントを取得

### Step 1: レビュー一覧を取得

```
GET ${API}/repos/${OWNER_REPO}/pulls/{index}/reviews
```

レスポンスの各レビューから確認すべきフィールド:
- `id`: レビューID（コメント取得に使用）
- `state`: `REQUEST_CHANGES`, `APPROVED`, `COMMENT` など
- `user.login`: レビュアー名
- `body`: レビュー本文（あれば）

### Step 2: レビューコメントを取得

```
GET ${API}/repos/${OWNER_REPO}/pulls/{index}/reviews/{review_id}/comments
```

レスポンスの各コメントから確認すべきフィールド:
- `id`: コメントID
- `path`: 対象ファイルパス
- `body`: コメント内容
- `diff_hunk`: 該当コードの差分
- `position`: diff内の行位置
- `commit_id`: 対象コミットSHA

## レビューコメントへの返信

Gitea APIには「コメントへの直接返信」機能がない（ソースコードで `replyReviewID` が `0` にハードコードされている）。
そのため、Web UIの内部エンドポイントを利用する専用スクリプトを使用する。

### スクリプト

`gitea/reply_to_review_comment.py` を `uv run` で実行する。

### 認証情報

パスワードは環境変数 `GITEA_PASSWORD` から取得する。

### 実行例

```bash
uv run gitea/reply_to_review_comment.py \
  --url http://<host>:<port> \
  --user "${GITEA_USERNAME}" --password "${GITEA_PASSWORD}" \
  --repo <owner>/<repo> \
  --pr <PR番号> \
  --comment-id <返信先コメントID> \
  --message "返信内容"
```

### 引数

- `--url`: GiteaのベースURL（例: `http://localhost:3000`）
- `--user`: ログインユーザー名
- `--password`: ログインパスワード（APIトークンではない）
- `--repo`: リポジトリ（例: `owner/repo`）
- `--pr`: PR番号
- `--comment-id`: 返信先のレビューコメントID（APIレスポンスの `id` フィールド）
- `--message`: 返信メッセージ本文

### 注意事項

- APIトークンではなくパスワードが必要（Web UIのセッション認証 + CSRF検証のため）
- コメントIDはレビューコメント取得APIのレスポンスに含まれる `id` フィールドを使用する
- スクリプト内部でレビューID（`pull_request_review_id`）を自動解決するため、利用者はコメントIDだけ指定すればよい
