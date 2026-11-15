FROM python:3.12-slim
WORKDIR /app
COPY main.py triage.py ./
COPY adapters/ ./adapters/
ENTRYPOINT ["python", "/app/main.py"]
