variable "project_id" {
  type    = string
  default = "encuestas-490902"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "cloudsql_instance_name" {
  type    = string
  default = "campaign-service-dev-db"
}

variable "db_name" {
  type    = string
  default = "invitation_service"
}

variable "db_user" {
  type    = string
  default = "invitation_app"
}

variable "artifact_registry_repository" {
  type    = string
  default = "invitation-service"
}

variable "email_provider_api_key" {
  type      = string
  sensitive = true
}

variable "token_signing_secret" {
  type      = string
  sensitive = true
}

variable "container_image_tag" {
  type    = string
  default = "internal-v1"
}