variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "cloudsql_instance_name" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "email_provider_api_key" {
  type      = string
  sensitive = true
}

variable "token_signing_secret" {
  type      = string
  sensitive = true
}