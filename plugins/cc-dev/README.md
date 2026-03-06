# cc-dev

Claude Codeのスキル開発やサブエージェント開発をサポートする

## インストール

```bash
# マーケットプレイスを追加する（未追加の場合）
claude plugin marketplace add backpaper0/claude-plugins

# プラグインをインストールする
claude plugin install cc-dev@urgm-plugins

# 必要に応じてuvをインストールする
mise use uv
```

## コマンド一覧

### `/analyze-session` — セッションログを解析

現在のセッションを解析し、使用トークン数やツール・スキルの実行状況を可視化します。

```
/analyze-session
```

