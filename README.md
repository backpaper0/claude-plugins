# Claude Plugins

自作のプラグインをホスティングするマーケットプレイスです。

マーケットプレイスを追加してプラグインをインストールすると使えるようになります。

```bash
# マーケットプレイスを追加する
claude plugin marketplace add backpaper0/claude-plugins

# プラグインをインストールする
claude plugin install git-operations@urgm-plugins
claude plugin install gitlab-workflow@urgm-plugins
claude plugin install cc-dev@urgm-plugins
```

不要になったらプラグインをアンインストールしてマーケットプレイスを削除してください。

```bash
# プラグインをアンインストールする
claude plugin uninstall git-operations@urgm-plugins
claude plugin uninstall gitlab-workflow@urgm-plugins
claude plugin uninstall cc-dev@urgm-plugins

# マーケットプレイスを削除する
claude plugin marketplace remove urgm-plugins
```

## GitHub Copilotで使う

このリポジトリのスキルは [`npx skills`](https://github.com/vercel-labs/skills) を使ってGitHub Copilot（Copilot CLIなど）にもインストールできます。

```bash
# スキルをインストールする（インストール対象を選ぶプロンプトが表示されます）
npx skills add backpaper0/claude-plugins -a github-copilot
```

プロジェクト直下の`.agents/skills/`にコピーされます（`-g`を付けるとユーザーグローバルの`~/.copilot/skills/`にインストールされます）。

不要になったら削除してください。

```bash
npx skills remove --all -a github-copilot
```
