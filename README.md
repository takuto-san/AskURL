# AskURL

公開ページの URL を渡すと、本文を取得し、Nosana のモデルが要点や次の対応を日本語で 1〜2 文にまとめる CLI です。HTML とプレーンテキストに対応しています。

## Docker で実行する

Docker Desktop を起動し、リポジトリのルートでイメージをビルドします。

```sh
docker build -t askurl .
```

### Qwen3.5-9B テンプレートを使う

1. [Nosana の Qwen テンプレート](https://deploy.nosana.com/deployments/create?template=qwen-9b)を開き、Qwen 3.5 9B を選びます。
2. RTX 3090 を選択し、時間あたりの料金を確認してデプロイを作成します。GPU クレジットが必要です。
3. 起動後、デプロイ詳細の **Service URL** を取得し、下のコマンドに入れます。公開エンドポイントなので URL の共有は控え、疎通確認が終わったらデプロイを停止します。

```sh
docker run --rm \
  -e NOSANA_SERVICE_URL='https://実際のサービスURL' \
  -e NOSANA_MODEL=qwen3.5:9b \
  askurl https://example.com/
```

このテンプレートのサービス URL には、Nosana の共有推論 API キーは不要です。`ページ本文を取得しました。` に続いて、モデルの回答が表示されれば成功です。[テンプレートの公式手順](https://nosana.com/blog/what-ai-models-can-you-run-on-an-3090/#1-can-an-rtx-3090-run-qwen35-9b-for-text-generation)

### Nosana の共有推論 API を使う

`inference:use` 権限付きの API キーが必要です。[Nosana のキー発行手順](https://learn.nosana.com/api/get-api-key.html)を参照してください。

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

- Docker コンテナで `https://example.com/` の本文を取得し、Nosana 上の Qwen 3.5 9B が返した日本語の回答をターミナルに表示できることを確認済みです。
- 共有推論 API には Docker コンテナから到達でき、未認証の `/v1/models` は `HTTP 401` を返すことを確認済みです。共有推論 API での回答生成は未確認です。
