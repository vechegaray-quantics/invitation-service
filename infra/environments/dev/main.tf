resource "google_project_service" "artifactregistry" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sqladmin" {
  project            = var.project_id
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  project            = var.project_id
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

resource "google_service_account" "invitation_service" {
  project      = var.project_id
  account_id   = "invitation-service-${var.environment}"
  display_name = "Invitation Service (${var.environment})"

  depends_on = [
    google_project_service.iam,
  ]
}

resource "google_project_iam_member" "invitation_service_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.invitation_service.email}"
}

resource "google_project_iam_member" "invitation_service_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.invitation_service.email}"
}

resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "_%@"
}

resource "google_sql_database" "invitation_service" {
  name     = var.db_name
  instance = var.cloudsql_instance_name

  depends_on = [
    google_project_service.sqladmin,
  ]
}

resource "google_sql_user" "invitation_app" {
  name     = var.db_user
  instance = var.cloudsql_instance_name
  password = random_password.db_password.result

  depends_on = [
    google_project_service.sqladmin,
  ]
}

resource "google_secret_manager_secret" "database_url" {
  project   = var.project_id
  secret_id = "invitation-service-database-url"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secretmanager,
  ]
}

resource "google_secret_manager_secret_version" "database_url_v1" {
  secret = google_secret_manager_secret.database_url.id
  secret_data = "postgresql+psycopg://${var.db_user}:${random_password.db_password.result}@/${var.db_name}?host=/cloudsql/${var.project_id}:${var.region}:${var.cloudsql_instance_name}"
}

resource "google_secret_manager_secret" "email_provider_api_key" {
  project   = var.project_id
  secret_id = "invitation-service-email-provider-api-key"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secretmanager,
  ]
}

resource "google_secret_manager_secret_version" "email_provider_api_key_v1" {
  secret      = google_secret_manager_secret.email_provider_api_key.id
  secret_data = var.email_provider_api_key
}

resource "google_secret_manager_secret" "token_signing_secret" {
  project   = var.project_id
  secret_id = "invitation-service-token-signing-secret"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secretmanager,
  ]
}

resource "google_secret_manager_secret_version" "token_signing_secret_v1" {
  secret      = google_secret_manager_secret.token_signing_secret.id
  secret_data = var.token_signing_secret
}

resource "google_artifact_registry_repository" "invitation_service" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Docker repository for invitation-service"
  format        = "DOCKER"

  depends_on = [
    google_project_service.artifactregistry,
  ]
}

resource "google_cloud_run_v2_service" "invitation_service" {
  name                 = "invitation-service"
  location             = var.region
  project              = var.project_id
  ingress              = "INGRESS_TRAFFIC_ALL"
  invoker_iam_disabled = true

  template {
    service_account = google_service_account.invitation_service.email

    containers {
	image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}/invitation-service:batches-v1"
      env {
        name  = "APP_ENV"
        value = var.environment
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      ports {
        container_port = 8080
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"

      cloud_sql_instance {
        instances = [
          "${var.project_id}:${var.region}:${var.cloudsql_instance_name}"
        ]
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }
  }

  depends_on = [
    google_project_service.run,
    google_project_iam_member.invitation_service_cloudsql_client,
    google_project_iam_member.invitation_service_secret_accessor,
    google_secret_manager_secret_version.database_url_v1,
    google_artifact_registry_repository.invitation_service,
  ]
}