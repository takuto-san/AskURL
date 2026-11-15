# AskURL

公開ページの URL を渡すと、本文を取得し、Nosana のモデルが要点や次の対応を日本語で 1〜2 文にまとめる CLI です。HTML とプレーンテキストに対応しています。

## Docker で実行する

Docker Desktop を起動し、リポジトリのルートでイメージをビルドします。

```sh
docker build -t askurl .
```

Nosana の共有推論 API を使うには、`inference:use` 権限付きの API キーが必要です。[Nosana のキー発行手順](https://learn.nosana.com/api/get-api-key.html)を参照してください。

Mac のターミナル（zsh）で以下を実行します。プロンプトが表示されたらキーを貼り付けて Enter を押します。入力は画面に表示されません。

```zsh
(
  read -rs 'NOSANA_API_KEY?Nosana API キー: ' || exit 1
  printf '\n'
  [[ -n $NOSANA_API_KEY ]] || exit 1
  export NOSANA_API_KEY
  docker run --rm -e NOSANA_API_KEY askurl https://example.com/
)
```

`ページ本文を取得しました。` に続いて、モデルの回答が表示されれば成功です。既定では Nosana のモデル一覧の先頭を使います。モデルを固定する場合は、`docker run` に `-e NOSANA_MODEL=モデルID` を追加してください。

## 動作確認の状況

- Docker のビルドと、コンテナから `https://example.com/` の本文を取得できることを確認済みです。
- コンテナから Nosana の `/v1/models` に到達し、未認証で `HTTP 401` が返ることを確認済みです。
- 有効なキーを使った実際の回答生成は未確認です。リクエスト生成と回答表示は模擬 HTTP 応答で確認済みです。

現行版の接続先は `https://inference.nosana.com/v1` です。テンプレートから立ち上げた個別のデプロイへの接続には、デプロイ先の URL を設定できるようにする変更が必要です。
