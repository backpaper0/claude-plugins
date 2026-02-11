# Claude Plugins

自作のプラグインをホスティングするマーケットプレイスです。

マーケットプレイスを追加してプラグインをインストールすると使えるようになります。

```bash
# マーケットプレイスを追加する
claude plugin marketplace add backpaper0/claude-plugins

# プラグインをインストールする
claude plugin install git-operations@urgm-plugins
claude plugin install transcript-utils@urgm-plugins
claude plugin install gitlab-workflow@urgm-plugins
```

不要になったらプラグインをアンインストールしてマーケットプレイスを削除してください。

```bash
# プラグインをアンインストールする
claude plugin uninstall git-operations@urgm-plugins
claude plugin uninstall transcript-utils@urgm-plugins
claude plugin uninstall gitlab-workflow@urgm-plugins

# マーケットプレイスを削除する
claude plugin marketplace remove urgm-plugins
```
