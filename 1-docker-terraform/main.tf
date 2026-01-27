terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  # Thay vì điền cứng ID, ta dùng biến
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "demo-bucket" {
  # Sử dụng biến project để tên bucket là duy nhất
  name          = "${var.project}-terra-bucket"
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = var.location
}