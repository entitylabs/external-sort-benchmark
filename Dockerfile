FROM python:3.12-slim

WORKDIR /app

COPY src/ ./src/

CMD ["python", "/app/src/run_benchmark.py", "--help"]
