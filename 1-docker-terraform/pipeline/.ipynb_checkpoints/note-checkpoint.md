
**Chủ đề:** ETL Pipeline (CSV to Postgres)
**Ngày:** 28/01/2026

---

## 1. Cột Gợi nhớ (Cues) | 2. Nội dung chi tiết (Notes)

### ❓ Big Concept:

**ETL là gì?**
*(Giải thích kiểu Feynman)*

> **ETL = Extract - Transform - Load**
> Hãy tưởng tượng bạn chuyển nhà:
> 1. **Extract (Lấy đồ):** Lấy đồ đạc từ nhà cũ (File CSV trên mạng).
> 2. **Transform (Sắp xếp):** Phân loại đồ dễ vỡ, ghi tên thùng, vứt rác (Sửa kiểu dữ liệu, fix datetime).
> 3. **Load (Xếp kho):** Chất đồ vào nhà kho mới (Postgres Database).
> 
> 

---

### 🛠️ Tech Stack

**(Công cụ cần nhớ)**

* **Jupyter Notebook:** Quyển nháp điện tử. Code dòng nào chạy dòng đó, sai sửa luôn. Dùng để test logic.
* **Pandas:** "Excel bằng code". Dùng để đọc và xử lý dữ liệu dạng bảng.
* **SQLAlchemy:** Người phiên dịch. Giúp Python nói chuyện được với Database.
* **Docker:** Cái hộp ảo chứa Database.

---

### ⚠️ Critical Fixes

**(Những lỗi đã gặp)**

**1. Lỗi Driver SQLAlchemy**

* **Vấn đề:** SQLAlchemy mặc định tìm `psycopg2` (cũ), nhưng mình cài `psycopg` (mới).
* **Giải pháp:** Sửa connection string.
* ❌ `postgresql://...`
* ✅ `postgresql+psycopg://...`



**2. Lỗi mất dữ liệu (Docker)**

* **Vấn đề:** Tắt máy -> Tắt Container -> Mất dữ liệu?
* **Giải pháp:** **Volumes**. Dữ liệu không nằm trong Container, nó nằm ở "ổ cứng rời" (Volume).
* **Cú pháp:** `-v host_path:container_path`

**3. Lỗi "Relation does not exist"**

* **Vấn đề:** Mount volume sai chỗ.
* ❌ `/var/lib/postgresql` (Thư mục cha)
* ✅ `/var/lib/postgresql/data` (Thư mục chính xác chứa data của Postgres)


* **Bài học:** Sai một ly, đi một dặm. Postgres không tìm thấy data cũ -> Nó tạo DB mới tinh -> Bảng biến mất.

---

### 🚀 Performance

**(Tối ưu hóa)**

**Tại sao phải "Chunking"?**
*(Iterators)*

> **Vấn đề:** RAM máy tính có hạn (ví dụ 8GB). Nếu file CSV nặng 10GB -> Máy treo (Out of Memory).
> **Giải pháp:** Chia nhỏ để trị.
> * Dùng `iterator=True` và `chunksize=100000`.
> * Giống như uống bia: Không ai uống hết két bia 1 hơi. Phải uống từng cốc một.
> 
> 

**Quy trình Ingestion Loop:**

1. **Chunk 1:** `head(0)` để tạo khung bảng (`replace`). Sau đó nạp dữ liệu.
2. **Chunk 2...n:** `append` (nối đuôi) vào bảng cũ.
3. **Kết quả:** 1 triệu dòng được nạp mượt mà, RAM không bị quá tải.

---

### 💻 Code Snippets

**(Copy-paste cheatsheet)**

**1. Connect DB:**

```python
engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')
engine.connect()

```

**2. Chunking Iterator:**

```python
df_iter = pd.read_csv(url, iterator=True, chunksize=100000)

```

**3. The Loop:**

```python
for chunk in df_iter:
    chunk.to_sql(name='table_name', con=engine, if_exists='append')

```

**4. Fix Docker Volume:**

```bash
docker run ... -v ny_taxi_postgres_data:/var/lib/postgresql/data ...

```

---

## 3. Tổng kết (Summary)

Hôm nay mình đã học cách xây dựng một **Data Pipeline đơn giản**:

1. Không tải file CSV về máy local, mà stream trực tiếp từ mạng vào RAM.
2. Dùng **Pandas Chunking** để xử lý dữ liệu lớn hơn dung lượng RAM cho phép.
3. Hiểu sâu về **Docker Volumes**: Container là tạm thời (ephemeral), Volume là vĩnh cửu (persistent). Nếu mất dữ liệu, kiểm tra lại đường dẫn mount (`/data`).
4. Debug thành công các lỗi kết nối phổ biến giữa Python và Postgres.

