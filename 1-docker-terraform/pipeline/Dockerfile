# 1. Chọn Base Image
FROM python:3.13-slim

# 2. Cài đặt uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# 3. Setup thư mục
WORKDIR /app

# 4. Copy file định nghĩa thư viện
COPY pyproject.toml uv.lock ./

# 5. Cài đặt thư viện
# BỎ cờ --system.
# Thêm --no-cache để giảm dung lượng image (optional)
RUN uv sync --frozen --no-cache

# QUAN TRỌNG: Thêm đường dẫn của môi trường ảo vào PATH
# Điều này giúp khi gõ "python", nó sẽ dùng python trong .venv vừa tạo
ENV PATH="/app/.venv/bin:$PATH"

# 6. Copy source code
COPY pipeline.py pipeline.py

# 7. Chạy lệnh
# Vì đã set PATH ở trên, ta chỉ cần gọi python trực tiếp
ENTRYPOINT ["python", "pipeline.py"]