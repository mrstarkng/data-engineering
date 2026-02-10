
**Chủ đề:** ETL Pipeline (CSV to Postgres)
**Ngày:** 28/01/2026

---

## 1. Cột Gợi nhớ (Cues) | 2. Nội dung chi tiết (Notes)

### ❓ Big Concept:

**ETL là gì?**

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


Tuyệt vời! Đây là bản tổng hợp kiến thức (Lecture Notes) cho các bài học gần đây nhất (từ lúc tạo Script đến setup pgAdmin), được trình bày theo phong cách **Cornell Notes** dành cho sinh viên Khoa học Máy tính (CS).

Bạn có thể copy cái này vào Notion/Obsidian.

---

**Chủ đề:** Automation (Scripting) & Docker Networking
**Trạng thái:** Đã hoàn thành (Hands-on)

---

## 1. Automation: Từ Notebook đến Script (`.py`)

### 💡 Core Concept (Tư duy)

* **Notebook (`.ipynb`)**: Dùng cho *Exploration* (Khám phá), *Prototyping* (Thử nghiệm). Chạy tương tác (Interactive).
* **Script (`.py`)**: Dùng cho *Production* (Vận hành), *Automation* (Tự động hóa). Chạy batch/cronjob.
* **Mục tiêu**: Biến quy trình nạp dữ liệu thủ công thành một công cụ dòng lệnh (CLI Tool) có thể tái sử dụng.

### 🛠️ Kỹ thuật (Technical Implementation)

* **`argparse` / `click**`: Thư viện để parse tham số dòng lệnh. Giúp script không bị "hard-code".
* *Ví dụ:* Thay vì sửa code để đổi ngày, ta chạy: `python ingest.py --date=2021-01`


* **`if __name__ == '__main__':`**: Điểm bắt đầu (Entry point) của chương trình Python. Đảm bảo code chỉ chạy khi được gọi trực tiếp, không chạy khi bị import như module.

### 📝 Code Snippet (Skeleton)

```python
import click

@click.command()
@click.option('--user', help='Postgres User')
@click.option('--url', help='CSV URL')
def main(user, url):
    # Logic: Download -> Pandas Chunking -> Postgres
    print(f"Ingesting data for user {user} from {url}")

if __name__ == '__main__':
    main()

```

---

## 2. Docker Networking (Kiến thức quan trọng ⭐️)

### ❓ Vấn đề (The Problem)

* Mỗi Container là một môi trường cách ly (isolated environment).
* Container A (Postgres) và Container B (pgAdmin) mặc định **không nhìn thấy nhau**.
* **Lầm tưởng phổ biến:** Từ Container B gọi `localhost` để tìm A.
* ❌ **Sai:** `localhost` trong Container B chính là Container B.
* ✅ **Đúng:** Phải dùng **Service Name** (Tên Container).



### 💡 Giải pháp: User-defined Bridge Network

Docker cho phép tạo một mạng ảo (Virtual Network) để các container kết nối với nhau.

1. **Tạo mạng:**
```bash
docker network create pg-network

```


2. **Gắn Container vào mạng:** Thêm flag `--network=pg-network` khi `docker run`.
3. **DNS Resolution (Ma thuật):** Docker tự động phân giải tên Container thành địa chỉ IP nội bộ.
* Khi pgAdmin hỏi: "Ai là `pgdatabase`?"
* Docker trả lời: "Nó là IP `172.18.0.2`" (Ví dụ).



### 📐 Sơ đồ kiến trúc (Mental Model)

```text
[ Docker Host (Máy tính của bạn) ]
      |
      |-- [ Network: pg-network ] ---------------------------|
            |                                                |
      [ Container: pgdatabase ]                       [ Container: pgadmin ]
      (Postgres DB)                                   (Web Interface)
      Port: 5432                                      Port: 80
      Name: "pgdatabase"                              Name: "pgadmin"

```

---

## 3. Quản lý DB bằng pgAdmin

### 🛠️ Setup

* Image: `dpage/pgadmin4`
* Cần ánh xạ cổng (Port mapping) để truy cập từ trình duyệt máy host: `-p 8085:80`.
* Cần Volume để lưu cấu hình (đỡ phải add lại server mỗi lần restart): `-v pgadmin_data:/var/lib/pgadmin`.

### 🔌 Kết nối (Connection Config)

Khi cấu hình server trong giao diện pgAdmin:

* **Host name/address:** `pgdatabase` (Tên container Postgres). **KHÔNG DÙNG** `localhost`.
* **Port:** `5432` (Cổng nội bộ của container Postgres).
* **Username/Password:** `root` / `root`.

---

## 4. Troubleshooting (Gỡ lỗi thường gặp)

| Lỗi (Error) | Nguyên nhân (Root Cause) | Cách fix (Solution) |
| --- | --- | --- |
| **Connection Refused** | Container chưa bật hoặc sai port. | Check `docker ps`. Restart container. |
| **Conflict. Name already in use** | Tên container bị trùng với cái cũ đã tắt. | `docker rm -f <tên_container>` |
| **Relation does not exist** | DB trống rỗng do mount sai volume path. | Fix path: `-v vol_name:/var/lib/postgresql/data` |
| **pgAdmin không kết nối được DB** | Khác mạng Docker hoặc sai Host name. | Cho 2 container cùng `--network`. Hostname = Container Name. |

---

## 5. Tổng kết 

> "Để làm Data Engineer chuyên nghiệp, chúng ta không chạy code thủ công (Notebook) mà gói nó thành Script. Để các công cụ (như Database và trang quản lý pgAdmin) nói chuyện được với nhau, chúng ta không dùng dây cáp thật mà cắm chúng vào chung một cái ổ cắm ảo gọi là **Docker Network**. Khi đã cắm chung ổ, chúng gọi nhau bằng tên (Name) chứ không gọi là 'localhost'."

---

### 👉 Next Step (Bước kế tiếp)

Bạn đã có Script (`ingest_data.py`) và Database. Bước tiếp theo là **Dockerize the Script**: Đóng gói chính cái script Python của bạn vào trong một Docker Image để nó trở thành một "Container xử lý dữ liệu" độc lập, không phụ thuộc vào môi trường máy tính của bạn nữa.

Tuyệt vời! Đây là bản tổng hợp kiến thức chuyên sâu của các bài học gần đây (từ lúc đóng gói Script đến khi chạy xong Pipeline hoàn chỉnh), được trình bày theo phương pháp **Cornell Notes** kết hợp với tư duy giải thích đơn giản hóa của **Feynman**.

Đây là tài liệu để bạn ôn tập ("Review") trước khi bước vào các hệ thống phức tạp hơn.

---

# 🎓 NOTES: Containerization & Orchestration

**Module:** Docker & Ingestion Pipeline
**Ngày:** 03/02/2026

---

## 1. CỘT TỪ KHÓA (Cues) | 2. NỘI DUNG CHI TIẾT (Notes)

### 📦 The Concept: Dockerizing Scripts

*(Tại sao phải làm thế?)*

* **Vấn đề "It works on my machine":** Code chạy ngon trên máy mình nhưng sang máy khác (hoặc lên Cloud) thì chết vì thiếu thư viện, lệch phiên bản OS.
* **Giải pháp (Feynman Analogy):**
> Đừng chỉ gửi mỗi món hàng (Code). Hãy gửi **cả cái thùng container** chứa món hàng đó (Image). Trong thùng đã có sẵn môi trường, công cụ, hệ điều hành y hệt lúc mình làm.


* **Quy trình:**
1. **Dockerfile:** Bản thiết kế (Recipe).
2. **Build:** Đóng gói -> Tạo ra `Image` (Tĩnh).
3. **Run:** Chạy -> Tạo ra `Container` (Động).


* **⚠️ Bài học xương máu (Slim Images):**
* Image `python:slim` rất nhẹ nhưng bị cắt giảm quá tay (thiếu `curl`, `gcc`...).
* **Fix:** Phải tự cài lại bằng `RUN apt-get install -y curl` trong Dockerfile.



---

### 🌐 Docker Networking

*(Làm sao các Container nói chuyện?)*

* **Isolation (Mặc định):** Mỗi container là một hòn đảo cô lập.
* **Bridge Network (Cầu nối):** Để kết nối, ta phải "xây cầu" (tạo network) hoặc "nối dây mạng ảo".
* **DNS Resolution (Ma thuật):**
* Trong mạng Docker, các container gọi nhau bằng **TÊN (Service Name)**, không dùng IP (vì IP đổi liên tục).
* **Quy tắc vàng:**
* Từ máy Host gọi vào Container: Dùng `localhost:Port_Map`.
* Từ Container gọi Container khác: Dùng `Service_Name:Internal_Port` (Ví dụ: `pgdatabase:5432`).





---

### 🎼 Orchestration: Docker Compose

*(Nhạc trưởng điều phối)*

* **Vấn đề:** Chạy 5-6 container bằng lệnh `docker run` thủ công rất mệt, dễ quên tham số (`-v`, `-e`, `--network`...).
* **Giải pháp:** **Infrastructure as Code (IaC)**.
* Viết tất cả cấu hình vào 1 file `docker-compose.yaml`.
* Dùng 1 lệnh `docker-compose up -d` để dựng cả hệ thống.


* **Cơ chế:**
* Tự động tạo Network chung (ví dụ: `pipeline_default`).
* Tự động gán DNS cho các services (`pgdatabase`, `pgadmin`).
* Quản lý vòng đời (Lifecycle): Khởi tạo -> Chạy -> Dừng -> Xóa.



---

### 💾 Data Persistence

*(Cái xác và cái hồn)*

* **Container (Cái xác):** Là vô thường (Ephemeral). Có thể xóa đi tạo lại thoải mái.
* **Volume (Cái hồn):** Là vĩnh cửu (Persistent).
* Dù container bị `rm`, `down`, thì dữ liệu trong Volume vẫn còn (miễn là không xóa Volume).
* Nếu mất dữ liệu -> Kiểm tra lại đường dẫn mount (`/var/lib/postgresql/data`).



---

### 🏭 Real-world Mapping

*(Áp dụng thực tế)*

| Local (Học tập) | Production (Đi làm) |
| --- | --- |
| `docker build` | **CI/CD Pipeline** (Jenkins/GitHub Actions) tự động build khi push code. |
| `docker run` | **Job Scheduling** (Airflow/Prefect) tự động kích hoạt container chạy định kỳ. |
| `docker-compose` | **Kubernetes (K8s)** quản lý hàng nghìn container phức tạp. |
| `--rm` (Tự xóa) | **Ephemeral Pods/Jobs** chạy xong tự hủy để tiết kiệm tiền Cloud. |

---

## 3. SUMMARY 

> **Tóm lại:**
> Thay vì chạy code thủ công như một thợ thủ công (Artisan), chúng ta đã chuyển sang dây chuyền công nghiệp:
> 1. Đóng gói code vào "chiếc hộp thần kỳ" (**Docker Image**) để vứt đâu cũng chạy được.
> 2. Dùng một "bản vẽ kiến trúc" (**Docker Compose**) để dựng lên cả một toà nhà (Database + Admin) chỉ trong 1 giây.
> 3. Kết nối các phòng trong toà nhà bằng "đường dây nội bộ" (**Network**) để chúng gọi nhau bằng tên.
> 4. Khi cần chạy việc (Ingestion), ta thuê một nhân viên thời vụ (**Container --rm**), làm xong việc thì nhân viên đó tự biến mất, nhưng kết quả công việc (**Data**) thì được lưu lại mãi mãi trong kho (**Volume**).
> 
> 

---

### 📝 Next Action Items

1. **Ôn tập SQL:** Dữ liệu đã có, giờ cần học cách truy vấn (Query) để lấy Insight.
2. **Git:** Lưu trữ code (`ingest_data.py`, `Dockerfile`, `docker-compose.yaml`) lên GitHub để quản lý phiên bản.