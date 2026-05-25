FROM python:3.13-slim

# Security: run as non-root
RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

WORKDIR /sandbox

# Install test runner and linter only
COPY sandbox/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tests are mounted at runtime, not baked in
USER sandbox

ENTRYPOINT ["python", "/sandbox/runner.py"]
