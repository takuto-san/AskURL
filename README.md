<img src="assets/askurl-icon.png" alt="AskURL pixel-art icon" width="96">

# AskURL

[日本語](docs/README.ja.md) · **English** · [简体中文](docs/README.zh-CN.md)

AskURL is a command-line tool that reads a public web page and asks a model on Nosana for a short summary or suggested next step. It accepts HTML and plain text and aims for an answer of one or two sentences. Responses are in Japanese by default. Add `--language en` for English.

In Daytona mode, an isolated, temporary sandbox fetches the page. The CLI runs in Docker, sends the extracted text to Nosana, and prints the answer in your terminal.

## Run with Docker

Start Docker Desktop or another Docker engine, then build the image from the repository root.

```sh
docker build -t askurl .
```

### Use a Qwen 3.5 9B deployment

1. Open the [Nosana Qwen template](https://deploy.nosana.com/deployments/create?template=qwen-9b) and choose Qwen 3.5 9B.
2. Choose an RTX 3090, check the hourly rate, and create the deployment. You need GPU credits.
3. When the deployment is running, copy its **Service URL** into the command below. Keep the public endpoint URL private and stop the deployment when you finish testing.

```sh
docker run --rm \
  -e NOSANA_SERVICE_URL='https://your-service-url.example' \
  -e NOSANA_MODEL=qwen3.5:9b \
  askurl https://example.com/
```

The template endpoint does not require a Nosana shared inference API key. The CLI prints a page-fetch confirmation in Japanese, followed by the model's answer. See the [official deployment guide](https://nosana.com/blog/what-ai-models-can-you-run-on-an-3090/#1-can-an-rtx-3090-run-qwen35-9b-for-text-generation).

### Use Nosana's shared inference API

Create a key with the `inference:use` scope. See the [Nosana API key guide](https://learn.nosana.com/api/get-api-key.html).

On macOS with zsh, run the following and paste your key at the hidden input prompt.

```zsh
(
  read -rs 'NOSANA_API_KEY?Nosana API key: ' || exit 1
  printf '\n'
  [[ -n $NOSANA_API_KEY ]] || exit 1
  export NOSANA_API_KEY
  docker run --rm -e NOSANA_API_KEY askurl https://example.com/
)
```

AskURL uses the first available model returned by Nosana. To select a model explicitly, add `-e NOSANA_MODEL=your-model-id` to `docker run`.

### Fetch a page in Daytona

With `--daytona`, AskURL creates a temporary sandbox to fetch and extract the page text. The CLI sends that text to Nosana and requests deletion of the sandbox after the fetch.

Create a key in [Daytona API Keys](https://app.daytona.io/dashboard/keys) with **Sandboxes → Write** (`write:sandboxes`) and **Delete** (`delete:sandboxes`). Copy `.env.example` to `.env` and fill in `DAYTONA_API_KEY` and `NOSANA_SERVICE_URL`. Git and the Docker build both exclude `.env`.

```sh
cp -n .env.example .env
chmod 600 .env
docker build --build-arg INSTALL_DAYTONA=1 -t askurl-daytona .
docker run --rm --env-file .env \
  askurl-daytona --daytona https://raw.githubusercontent.com/takuto-san/AskURL/main/README.md
```

By default, the CLI confirms in Japanese that Daytona fetched the page, then prints the model's answer. Daytona Tier 1 and 2 restrict outbound hosts. This example uses a public file on an allowed GitHub domain. Check your organization policy for other URLs. See [Daytona network limits](https://www.daytona.io/docs/en/network-limits/).

### Customize the prompts

Edit the Japanese (`ja`) or English (`en`) text in [`config/prompts.toml`](config/prompts.toml), then rebuild the Docker image to apply the change.

## Verified behavior

- The Docker CLI fetched `https://example.com/` and displayed a Japanese response from Qwen 3.5 9B on Nosana.
- Daytona mode fetched the public GitHub README inside a real sandbox and displayed the model's answer in the terminal.
- Docker reached the shared inference endpoint. The unauthenticated `/v1/models` request returned HTTP 401. Answer generation through the shared API has not been verified.
