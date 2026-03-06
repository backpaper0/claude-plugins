---
name: analyze-session
description: 現在のセッションを解析し、使用トークン数やツール・スキルの実行状況を可視化します。
disable-model-invocation: true
---

# セッションログ解析スキル

## 実行手順

次のコマンドを実行して、セッションログを解析する。

```
uvx uvx git+https://github.com/backpaper0/session-analyzer.git@v0.2.0 ${CLAUDE_SESSION_ID}
```

解析結果(HTMLファイル)のパスが標準出力へ書き出されるので、次のコマンドを使用して開く。

- macOSの場合: `open <解析結果のパス>`
- Windowsの場合: `start <解析結果のパス>`
