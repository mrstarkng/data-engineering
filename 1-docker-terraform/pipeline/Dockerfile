FROM python:3.13.11-slim

# --- THÊM DÒNG NÀY ---
# Cài đặt curl (và cập nhật danh sách gói phần mềm của Linux)
RUN apt-get update && apt-get install -y curl
# ---------------------

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked

COPY ingest_data.py .

ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]