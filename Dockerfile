FROM python:3.7-slim

WORKDIR /app

RUN pip install --no-cache-dir xsorted


COPY src/ ./src/

CMD ["python", "/app/src/run_benchmark.py", "--help"]
