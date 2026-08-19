# cc-utils

特定の職種やドメインに限らない、汎用的なタスクを支援するエージェントスキル集。

- `xlsx-to-markdown`: Excelで作られた設計書・仕様書（1シートに見出し・本文・表・図が詰め込まれた「シート内文書」形式のもの）を、忠実なMarkdownドキュメントへ変換する。図はテキストラベルが取得できる範囲でMermaid図として再現する

各スキルは独立しており、他のスキルへの依存はない。

## インストール

```bash
# マーケットプレイスを追加する（未追加の場合）
claude plugin marketplace add backpaper0/claude-plugins

# プラグインをインストールする
claude plugin install cc-utils@urgm-plugins
```

インストール後は以下のように呼び出す。

```
/cc-utils:xlsx-to-markdown
```
