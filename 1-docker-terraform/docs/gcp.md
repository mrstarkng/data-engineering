# ☁️ GCP & Terraform Setup Log

**Dự án:** Data Engineering Zoomcamp & SentinAI Thesis
**Ngày cập nhật:** 05/02/2026
**Thiết bị:** MacBook Pro M1 (ARM64)

## 1. Trạng thái Tài khoản & Tài chính (Billing)

* **Loại tài khoản:** Paid Account (Tài khoản trả phí).
* **Tín dụng miễn phí (Free Credit):** ~$300 (hiển thị là `₫7,885,501`).
* *Cơ chế:* Hệ thống trừ tiền vào Credit trước. Khi Credit = 0, mới trừ vào thẻ VISA.


* **Cảnh báo ngân sách (Budget Alert):** Đã thiết lập ngưỡng cảnh báo tại **7.000.000 VNĐ**.
* *Mục đích:* Nhận email thông báo ngay khi chi phí chạm ngưỡng, tránh việc tài nguyên chạy ngầm làm "cháy" thẻ.



## 2. Cấu hình Môi trường Local (MacBook M1)

### Các công cụ đã cài đặt

| Công cụ | Phiên bản | Đường dẫn cài đặt | Ghi chú |
| --- | --- | --- | --- |
| **Google Cloud SDK** | 553.0.0 | `/opt/homebrew/bin/gcloud` | Cài qua Homebrew, fix lỗi Python 3.13 |
| **Terraform** | 1.14.3 | `/opt/homebrew/bin/terraform` | Phiên bản native cho chip Apple Silicon |
| **Python** | 3.13 | `/opt/homebrew/opt/python@3.13` | Môi trường nền cho gcloud |

### Xác thực & Biến môi trường

* **Service Account Key:** File JSON chứa khóa bí mật.
* *Vị trí (Ví dụ):* `~/.google/credentials/gcp-key.json` (hoặc đường dẫn thực tế bạn lưu).


* **Biến môi trường (.zshrc):**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="<đường-dẫn-đến-file-json-của-bạn>"

```


* **Quyền hạn (Authentication):**
1. **Cho code/Terraform:** Đã chạy `gcloud auth application-default login` (Sử dụng biến môi trường trên).
2. **Cho CLI Admin:** Đã chạy `gcloud auth login` (Đăng nhập trình duyệt quyền Admin).



## 3. Cấu trúc Dự án trên Cloud (GCP)

* **Project Name:** `DTC DE Course`
* **Project ID:** `genuine-flight-485514-h8` (ID dùng định danh duy nhất trong lệnh code).
* **Service Account:** `dtc-de-user`
* **Các quyền (IAM Roles) đã cấp cho Service Account:**
* `Viewer`: Xem tài nguyên cơ bản.
* `Storage Admin`: Toàn quyền tạo/xóa Bucket.
* `Storage Object Admin`: Toàn quyền đọc/ghi file trong Bucket.
* `BigQuery Admin`: Toàn quyền tạo/xóa Dataset, Table.


* **APIs đã bật:**
* `iam.googleapis.com`
* `iamcredentials.googleapis.com`



## 4. Hạ tầng đã triển khai (Infrastructure as Code)

**Thư mục làm việc:** `~/Projects/de-zoomcamp/terraform`

### Các file cấu hình

1. **`main.tf`**: File chính khai báo tài nguyên (Provider, Resource).
2. **`variables.tf`**: Chứa các biến (Project ID, Region) để code gọn gàng, tái sử dụng được.
3. **`.gitignore`**: **QUAN TRỌNG**. Đã cấu hình để chặn upload file `*.json`, `*.tfstate`, `.terraform/` lên Github.

### Tài nguyên hiện có (Created Resources)

| Loại Resource | Tên trong Code | Tên trên GCP | Mục đích |
| --- | --- | --- | --- |
| **GCS Bucket** | `demo-bucket` | `genuine-flight-485514-h8-terra-bucket` | **Data Lake**: Nơi chứa dữ liệu thô (Raw Data) |
| **BigQuery Dataset** | `demo_dataset` | `demo_dataset` | **Data Warehouse**: Nơi chứa bảng dữ liệu để phân tích |

## 5. Cheat Sheet: Các lệnh thường dùng

### Google Cloud CLI (`gcloud`)

* `gcloud projects list`: Xem danh sách dự án.
* `gcloud config set project <PROJECT_ID>`: Chọn dự án mặc định để làm việc.
* `gcloud storage ls`: Liệt kê các bucket đang có.

### Terraform Workflow

Quy trình chuẩn mỗi khi muốn sửa đổi hạ tầng:

1. **Sửa code** trong `main.tf` hoặc `variables.tf`.
2. **`terraform plan -var="project=genuine-flight-485514-h8"`**: Xem trước thay đổi (Review).
3. **`terraform apply -var="project=genuine-flight-485514-h8"`**: Áp dụng thay đổi (Deploy).
4. **`terraform destroy`**: Xóa sạch mọi thứ (Dùng khi học xong bài để tiết kiệm tiền).

## 6. Bài học kinh nghiệm (Key Learnings)

* **Về Billing:** Khi nâng cấp lên Paid Account, giao diện $300 Credit có thể bị ẩn đi hoặc báo "Expired" ở gói cũ, nhưng thực chất tiền vẫn còn ở gói mới (Available).
* **Về Terraform vs GCP:**
* **GCP** là "đất đai & vật liệu" (Cloud Provider).
* **Terraform** là "bản vẽ & robot xây dựng" (IaC Tool).
* Dùng Terraform giúp dự án Khóa luận có tính **Reproducibility** (Xóa đi dựng lại dễ dàng) và **Scalability** (Dễ mở rộng), điểm cộng lớn về tư duy Software Engineering.


