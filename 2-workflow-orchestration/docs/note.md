# NOTES: KESTRA DATA PIPELINES

**Chủ đề:** Workflow Orchestration & ETL Design Patterns
**Công cụ:** Kestra, Docker, PostgreSQL, Python

---

## 1. Anatomy of a Flow (Giải phẫu một quy trình)

Mọi Flow trong Kestra đều tuân theo cấu trúc: **Inputs -> Variables -> Tasks -> Triggers**.

### 🔹 Dynamic Inputs & Variables (Tính linh hoạt)

Thay vì code cứng (Hard-coding), ta sử dụng `Inputs` để tham số hóa và `Variables` để xử lý logic chuỗi bằng ngôn ngữ template **Pebble**.

```yaml
# 1. Định nghĩa tham số đầu vào
inputs:
  - id: taxi_type
    type: SELECT
    values: [yellow, green]
    defaults: yellow

# 2. Xử lý logic biến (Pebble Template)
variables:
  # Tự động ghép chuỗi dựa trên input
  filename: "{{ inputs.taxi_type }}_tripdata.csv"
  
  # Tạo tên bảng trong Database
  db_table: "public.{{ inputs.taxi_type }}_trips"

```

---

## 2. Execution Environments (Môi trường thực thi)

Kestra tách biệt hoàn toàn môi trường điều phối (Orchestrator) và môi trường xử lý (Worker).

### 🔹 Docker Runner Pattern (Sự cô lập)

Chạy các tác vụ nặng (Python, Node, R) trong Container riêng biệt để tránh xung đột thư viện (Dependency Hell).

**Code ví dụ (Trích xuất & Chuyển đổi):**

```yaml
tasks:
  - id: python_transform
    type: io.kestra.plugin.scripts.python.Script
    
    # [QUAN TRỌNG] Chỉ định chạy trong Docker
    taskRunner:
      type: io.kestra.plugin.core.runner.Process # Hoặc docker.Docker
    containerImage: python:3.11-alpine  # Ảnh môi trường sạch
    
    # Cơ chế truyền file vào/ra container
    inputFiles:
      raw_data.json: "{{ outputs.previous_task.uri }}"
    outputFiles:
      - "*.parquet"  # Lấy tất cả file parquet sau khi xử lý xong
      
    # Code Python thực thi
    script: |
      import os
      import json
      
      # Đọc file từ Kestra chuyển vào
      with open("raw_data.json", "r") as f:
          data = json.load(f)
          
      # ... Xử lý dữ liệu ...
      
      # Gửi biến nhỏ về Kestra (Metrics/Status)
      from kestra import Kestra
      Kestra.outputs({'processed_rows': len(data)})

```

---

## 3. ETL Design Patterns (Các mẫu thiết kế ETL cốt lõi)

Đây là phần quan trọng nhất để phân biệt một script nghiệp dư và một pipeline chuyên nghiệp.

### 🔹 Pattern A: The Staging Area (Bảng đệm)

Không bao giờ nạp thẳng vào bảng chính (Production Table). Hãy dùng bảng tạm (Staging).

**Quy trình chuẩn:**

1. `CREATE TABLE staging` (Giống bảng chính).
2. `TRUNCATE staging` (Xóa sạch rác cũ).
3. `COPY` data vào staging (Tốc độ cao).
4. `MERGE` từ staging sang chính.

**Code ví dụ (SQL):**

```yaml
  - id: load_to_staging
    type: io.kestra.plugin.jdbc.postgresql.CopyIn
    format: CSV
    table: "{{ render(vars.staging_table) }}"
    from: "{{ render(vars.file_uri) }}"
    header: true

```

### 🔹 Pattern B: Idempotency & Deduplication (Tính bất biến & Khử trùng)

**Nguyên tắc:** Pipeline phải có thể chạy lại N lần mà kết quả không thay đổi (không bị nhân đôi dữ liệu).

**Kỹ thuật:** Tạo "Fingerprint ID" (Dấu vân tay) cho từng dòng dữ liệu.

**Code ví dụ (Tạo ID bằng hàm băm MD5):**

```sql
-- Bước 1: Tạo ID duy nhất cho mỗi dòng trong bảng Staging
UPDATE {{ render(vars.staging_table) }}
SET unique_row_id = md5(
    COALESCE(vendor_id, '') || 
    COALESCE(pickup_datetime, '') || 
    COALESCE(trip_distance, '') 
    -- Nối tất cả các trường quan trọng lại rồi băm
);

-- Bước 2: Dùng MERGE (Upsert) để đưa vào bảng chính
MERGE INTO {{ render(vars.table) }} AS Main
USING {{ render(vars.staging_table) }} AS Stage
ON Main.unique_row_id = Stage.unique_row_id

-- Chỉ thêm mới nếu ID chưa tồn tại (Tránh trùng lặp)
WHEN NOT MATCHED THEN
  INSERT (unique_row_id, vendor_id, ...)
  VALUES (Stage.unique_row_id, Stage.vendor_id, ...);

```

---

## 4. Automation & Scheduling (Tự động hóa)

### 🔹 Cron & Backfill Pattern

Làm sao để một Flow vừa chạy tự động hàng ngày, vừa có thể chạy lại dữ liệu quá khứ (Backfill) mà không cần sửa code?

**Giải pháp:** Sử dụng biến `trigger.date`.

**Code ví dụ:**

```yaml
# 1. Định nghĩa lịch chạy (9h sáng ngày mùng 1 hàng tháng)
triggers:
  - id: monthly_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"

# 2. Sử dụng biến thời gian động trong Variables
variables:
  # Nếu chạy ngày 2024-02-01 -> Tải file "data_2024-02.csv"
  # Khi Backfill về năm 2020 -> Tự động đổi thành "data_2020-xx.csv"
  file_name: "data_{{ trigger.date | date('yyyy-MM') }}.csv"

```

### 🔹 Concurrency Control (Kiểm soát tài nguyên)

Ngăn chặn việc "DDOS" chính Database của mình khi Backfill chạy quá nhanh.

```yaml
concurrency:
  limit: 1  # Chỉ cho phép 1 luồng chạy cùng lúc. Xếp hàng lần lượt.

```

---

## 5. Resource Management (Quản lý tài nguyên)

Kestra lưu trữ file trung gian (CSV, JSON) trong bộ nhớ. Nếu không dọn dẹp, ổ cứng sẽ đầy.

**Code ví dụ (Task dọn rác):**

```yaml
  - id: cleanup
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: "Xóa toàn bộ file tạm sau khi Flow hoàn tất thành công"
    disabled: false # Đặt true nếu muốn debug (giữ file lại để kiểm tra)

```

---

## 💡 Summary

1. **Extract:** Dùng `wget/curl` hoặc Plugin HTTP. Lưu file vào Internal Storage.
2. **Transform (Light):** Dùng Python trong Docker để xử lý định dạng file (JSON -> CSV, Filter cột).
3. **Load (Staging):** Dùng `CopyIn` nạp vào bảng tạm Postgres.
4. **Transform (Heavy):** Dùng SQL (`MD5`, `MERGE`) trong Database để khử trùng và hợp nhất dữ liệu.
5. **Schedule:** Dùng `Cron` kết hợp biến `{{ trigger.date }}` để tự động hóa và hỗ trợ Backfill.

