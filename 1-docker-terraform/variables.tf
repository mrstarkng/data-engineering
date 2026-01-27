variable "project" {
  description = "genuine-flight-485514-h8"
  type        = string
}

variable "region" {
  description = "Region cho GCP resources"
  default     = "us-central1"
}

variable "location" {
  description = "Location cho Bucket và BigQuery"
  default     = "US"
}