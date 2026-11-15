<img src="../assets/askurl-icon.png" alt="AskURL 像素风图标" width="96">

# AskURL

[日本語](README.ja.md) · [English](../README.md) · **简体中文**

AskURL 是一个命令行工具。输入公开网页的 URL 后，它会提取正文，并让 Nosana 上的模型用一到两句话给出摘要或后续处理建议。支持 HTML 和纯文本。默认用日语回答，添加 `--language en` 可切换为英语。

在 Daytona 模式下，网页正文由隔离的临时沙箱提取。运行在 Docker 中的 CLI 会把正文发送给 Nosana，并在终端显示模型的回答。

## 演示

[观看终端演示（英语，MP4）](../assets/askurl-demo-en.mp4)。视频展示了 Daytona 如何在临时沙箱内获取网页正文，以及 Nosana 生成的简短英文回答如何显示在终端中。

## 使用 Docker 运行

启动 Docker Desktop 或其他 Docker 引擎，然后在仓库根目录构建镜像。

```sh
docker build -t askurl .
```

### 使用 Qwen 3.5 9B 部署

1. 打开 [Nosana 的 Qwen 模板](https://deploy.nosana.com/deployments/create?template=qwen-9b)，选择 Qwen 3.5 9B。
2. 选择 RTX 3090，确认每小时费率并创建部署。此操作需要 GPU 额度。
3. 部署启动后，将 **Service URL** 填入下面的命令。请妥善保管公开端点的地址，并在测试结束后停止部署。

```sh
docker run --rm \
  -e NOSANA_SERVICE_URL='https://your-service-url.example' \
  -e NOSANA_MODEL=qwen3.5:9b \
  askurl https://example.com/
```

模板提供的服务端点无需 Nosana 共享推理 API 密钥。CLI 会先用日语确认正文已获取，然后显示模型的回答。参见 [Nosana 官方部署指南](https://nosana.com/blog/what-ai-models-can-you-run-on-an-3090/#1-can-an-rtx-3090-run-qwen35-9b-for-text-generation)。

### 使用 Nosana 的共享推理 API

创建带有 `inference:use` 权限的密钥。参见 [Nosana API 密钥指南](https://learn.nosana.com/api/get-api-key.html)。

在 macOS 的 zsh 中运行以下命令。出现提示后粘贴密钥并按回车，输入不会显示在屏幕上。

```zsh
(
  read -rs 'NOSANA_API_KEY?Nosana API 密钥: ' || exit 1
  printf '\n'
  [[ -n $NOSANA_API_KEY ]] || exit 1
  export NOSANA_API_KEY
  docker run --rm -e NOSANA_API_KEY askurl https://example.com/
)
```

AskURL 默认使用 Nosana 返回的第一个可用模型。如需指定模型，可在 `docker run` 中添加 `-e NOSANA_MODEL=your-model-id`。

### 在 Daytona 中获取网页正文

指定 `--daytona` 后，AskURL 会创建临时沙箱来获取并提取网页正文。获取完成后，CLI 会请求删除沙箱，并将提取的正文发送给 Nosana。

在 [Daytona API Keys 页面](https://app.daytona.io/dashboard/keys) 创建密钥，并为 **Sandboxes** 启用 **Write**（`write:sandboxes`）和 **Delete**（`delete:sandboxes`）权限。将 `.env.example` 复制为 `.env`，填写 `DAYTONA_API_KEY` 和 `NOSANA_SERVICE_URL`。Git 和 Docker 构建都会排除 `.env`。

```sh
cp -n .env.example .env
chmod 600 .env
docker build --build-arg INSTALL_DAYTONA=1 -t askurl-daytona .
docker run --rm --env-file .env \
  askurl-daytona --daytona https://raw.githubusercontent.com/takuto-san/AskURL/main/README.md
```

终端会先用日语确认 Daytona 已获取正文，然后显示模型的回答。Daytona 的 Tier 1 和 Tier 2 会限制沙箱可以访问的外部域名。本示例使用许可列表中的 GitHub 公共文件。测试其他 URL 前，请确认所在组织的网络策略。参见 [Daytona 网络限制](https://www.daytona.io/docs/en/network-limits/)。

### 自定义提示词

在 [`config/prompts.toml`](../config/prompts.toml) 中编辑日语（`ja`）或英语（`en`）提示词，然后重新构建 Docker 镜像以应用更改。

## 已验证的功能

- Docker 容器可以获取 `https://example.com/` 的正文并显示 Nosana 上 Qwen 3.5 9B 返回的日语回答。
- Daytona 模式可以在真实沙箱中获取 GitHub 的公开 README，并在终端显示模型的回答。
- Docker 可以连接到 Nosana 的共享推理端点，未认证的 `/v1/models` 请求返回 HTTP 401。尚未验证共享推理 API 的回答生成功能。
