# Google Cloud Provider Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.84"
    }
  }
}

# Variables
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "google_maps_api_key" {
  description = "Google Maps API Key"
  type        = string
  sensitive   = true
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable Required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "firestore.googleapis.com",
    "pubsub.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com",
    "maps-backend.googleapis.com",
    "aiplatform.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Firestore Database
resource "google_firestore_database" "main" {
  depends_on  = [google_project_service.required_apis]
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  concurrency_mode                = "OPTIMISTIC"
  app_engine_integration_mode     = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state         = "DELETE_PROTECTION_ENABLED"

  depends_on = [google_project_service.required_apis]
}

# Service Accounts
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-service"
  display_name = "Cloud Run Service Account"
  description  = "Service account for Cloud Run services"
}

resource "google_service_account" "agents_sa" {
  account_id   = "a2a-agents-service"
  display_name = "A2A Agents Service Account"
  description  = "Service account for A2A agents"
}

# IAM Roles for Service Accounts
resource "google_project_iam_member" "cloud_run_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.editor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "agents_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agents_sa.email}"
}

# Pub/Sub Topics and Subscriptions
resource "google_pubsub_topic" "donation_created" {
  name = "donation-created"

  message_retention_duration = "604800s" # 7 days
  
  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "agent_processing" {
  name = "agent-processing"

  message_retention_duration = "604800s"
  
  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "achievement_unlocked" {
  name = "achievement-unlocked"

  message_retention_duration = "86400s" # 1 day
  
  depends_on = [google_project_service.required_apis]
}

# Subscriptions
resource "google_pubsub_subscription" "donation_processing" {
  name  = "donation-processing-sub"
  topic = google_pubsub_topic.donation_created.name

  ack_deadline_seconds       = 20
  message_retention_duration = "600s"
  retain_acked_messages      = false

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "86400s" # 1 day
  }
}

resource "google_pubsub_subscription" "agent_coordination" {
  name  = "agent-coordination-sub"
  topic = google_pubsub_topic.agent_processing.name

  ack_deadline_seconds = 30
  message_retention_duration = "1200s"
}

# Secret Manager for API Keys
resource "google_secret_manager_secret" "google_maps_api_key" {
  secret_id = "google-maps-api-key"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "google_maps_api_key" {
  secret      = google_secret_manager_secret.google_maps_api_key.id
  secret_data = var.google_maps_api_key
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = "your-super-secret-jwt-key-change-in-production"
}

# Cloud Run Services

# Donation Service
resource "google_cloud_run_service" "donation_service" {
  name     = "donation-service"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/donation-service:latest"
        
        ports {
          container_port = 8000
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "FIRESTORE_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name = "JWT_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run_sa.email

      timeout_seconds = 300
      container_concurrency = 80
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "100"
        "autoscaling.knative.dev/minScale"        = "1"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/cpu-throttling"       = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

# Points Service
resource "google_cloud_run_service" "points_service" {
  name     = "points-service"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/points-service:latest"
        
        ports {
          container_port = 8001
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
          requests = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run_sa.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "50"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Donor Engagement Agent
resource "google_cloud_run_service" "donor_agent" {
  name     = "donor-engagement-agent"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/donor-engagement-agent:latest"
        
        ports {
          container_port = 8080
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "A2A_PROTOCOL_VERSION"
          value = "0.3.0"
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }

      service_account_name = google_service_account.agents_sa.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "50"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Charity Optimization Agent
resource "google_cloud_run_service" "charity_agent" {
  name     = "charity-optimization-agent"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/charity-optimization-agent:latest"
        
        ports {
          container_port = 8081
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }
      }

      service_account_name = google_service_account.agents_sa.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "50"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM for Cloud Run Services (Allow unauthenticated access)
resource "google_cloud_run_service_iam_member" "donation_service_invoker" {
  service  = google_cloud_run_service.donation_service.name
  location = google_cloud_run_service.donation_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "points_service_invoker" {
  service  = google_cloud_run_service.points_service.name
  location = google_cloud_run_service.points_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "donor_agent_invoker" {
  service  = google_cloud_run_service.donor_agent.name
  location = google_cloud_run_service.donor_agent.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "charity_agent_invoker" {
  service  = google_cloud_run_service.charity_agent.name
  location = google_cloud_run_service.charity_agent.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# API Gateway
resource "google_api_gateway_api" "donation_api" {
  provider = google-beta
  api_id   = "donation-platform-api"
  project  = var.project_id

  depends_on = [google_project_service.required_apis]
}

resource "google_api_gateway_api_config" "donation_api_config" {
  provider      = google-beta
  api           = google_api_gateway_api.donation_api.api_id
  api_config_id = "config-${formatdate("YYYYMMDD-hhmm", timestamp())}"
  project       = var.project_id

  openapi_documents {
    document {
      path = "openapi.yaml"
      contents = base64encode(templatefile("${path.module}/openapi.yaml", {
        donation_service_url = google_cloud_run_service.donation_service.status[0].url
        points_service_url   = google_cloud_run_service.points_service.status[0].url
        donor_agent_url      = google_cloud_run_service.donor_agent.status[0].url
        charity_agent_url    = google_cloud_run_service.charity_agent.status[0].url
      }))
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_api_gateway_gateway" "donation_gateway" {
  provider   = google-beta
  api_config = google_api_gateway_api_config.donation_api_config.id
  gateway_id = "donation-platform-gateway"
  project    = var.project_id
  region     = var.region

  depends_on = [google_api_gateway_api_config.donation_api_config]
}

# Monitoring and Logging

# Log Sink for Errors
resource "google_logging_project_sink" "error_sink" {
  name        = "error-log-sink"
  destination = "pubsub.googleapis.com/projects/${var.project_id}/topics/${google_pubsub_topic.donation_created.name}"
  
  filter = "severity >= ERROR"

  unique_writer_identity = true
}

# Monitoring Dashboard
resource "google_monitoring_dashboard" "platform_dashboard" {
  dashboard_json = jsonencode({
    displayName = "Donation Platform Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "API Request Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"donation-service\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
              }]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Requests/second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND severity=\"ERROR\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

# Alerting Policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "High error rate for donation service"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"donation-service\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.1 # 10% error rate
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = []
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Storage Buckets for Static Assets
resource "google_storage_bucket" "static_assets" {
  name          = "${var.project_id}-static-assets"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30
    }
  }
}

# Make bucket publicly readable
resource "google_storage_bucket_iam_member" "static_assets_public" {
  bucket = google_storage_bucket.static_assets.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Outputs
output "donation_service_url" {
  description = "URL of the donation service"
  value       = google_cloud_run_service.donation_service.status[0].url
}

output "points_service_url" {
  description = "URL of the points service"
  value       = google_cloud_run_service.points_service.status[0].url
}

output "donor_agent_url" {
  description = "URL of the donor engagement agent"
  value       = google_cloud_run_service.donor_agent.status[0].url
}

output "charity_agent_url" {
  description = "URL of the charity optimization agent"
  value       = google_cloud_run_service.charity_agent.status[0].url
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = google_api_gateway_gateway.donation_gateway.default_hostname
}

output "firestore_database" {
  description = "Firestore database name"
  value       = google_firestore_database.main.name
}

output "static_assets_bucket" {
  description = "Static assets bucket name"
  value       = google_storage_bucket.static_assets.name
}