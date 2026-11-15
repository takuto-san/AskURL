FROM python:3.12-slim
WORKDIR /app
ARG INSTALL_DAYTONA=0
RUN if [ "$INSTALL_DAYTONA" = "1" ]; then pip install --no-cache-dir daytona==0.231.1; fi
COPY main.py prompt.py ./
COPY adapters/ ./adapters/
COPY config/prompts.toml ./config/prompts.toml
ENTRYPOINT ["python", "/app/main.py"]
