---
allowed-tools: Bash(git:*), Bash(glab:*), Read, Grep, Glob
---

# GitLab Merge Request 作成

GitLab にMerge Requestを作成する。現在のブランチの変更内容を分析し、適切なタイトルとdescriptionを自動生成する。

## 手順

### 1. 情報収集（並列実行）

以下のコマンドを**並列で**実行して、現在のブランチの状態を把握する:

- `git status` — 未コミットの変更・未追跡ファイルを確認
- `git diff main...HEAD --stat` — mainブランチからの変更ファイル一覧
- `git diff main...HEAD` — 完全なdiff
- `git log --oneline main..HEAD` — コミット履歴
- `git remote -v` — リモート情報
- `git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || echo "no-upstream"` — リモートにプッシュ済みか確認

### 2. 分析・MR作成

収集した情報を元に:

1. **変更内容を分析**して、MRのタイトルとdescriptionを起草する
2. タイトルは日本語で、簡潔に変更の目的を表現する（70文字以内）
3. descriptionは以下のフォーマットで日本語で作成:

```
## 概要
（1〜3行で変更の目的・背景を説明）

## 変更内容
（変更したファイルと内容をbulletで列挙）

## テスト計画
（テスト方法をbulletで列挙）
```

4. リモートにブランチが未プッシュの場合は `git push -u origin <current-branch>` でプッシュする
5. 以下のコマンドでMRを作成する（descriptionはHEREDOCで渡す）:

```
glab mr create --title "タイトル" --description "$(cat <<'EOF'
## 概要
...

## 変更内容
...

## テスト計画
...
EOF
)" --target-branch main
```

ターゲットブランチはデフォルトで `main` とする。

### 3. 結果報告

MR作成が成功したら、MRのURLをユーザーに表示する。失敗した場合はエラー内容を報告し、対処法を提案する。

次のアクションをサジェストする:

- `/review-fix` — レビューコメントが付いたらコードを修正
- `/resolve-conflicts` — コンフリクトが発生した場合に解消

## 注意事項

- 未コミットの変更がある場合は、MR作成前にユーザーに警告する
- コミットがない（mainと差分がない）場合は、MRを作成せずにユーザーに通知する
- `glab` コマンドが利用できない場合は、インストール方法を案内する（miseでのインストールを推奨）
