terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
  
  tags = var.tags
}

# Storage Account for Functions and Data
resource "azurerm_storage_account" "main" {
  name                     = "st${var.project_name}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  blob_properties {
    cors_rule {
      allowed_headers    = ["*"]
      allowed_methods    = ["GET", "HEAD", "POST", "PUT"]
      allowed_origins    = ["*"]
      exposed_headers    = ["*"]
      max_age_in_seconds = 3600
    }
  }
  
  tags = var.tags
}

# Storage Container for Dataset
resource "azurerm_storage_container" "dataset" {
  name                  = "dataset"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Storage Container for Processed Data
resource "azurerm_storage_container" "processed" {
  name                  = "processed"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "appi-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  
  tags = var.tags
}

# App Service Plan for Functions
resource "azurerm_service_plan" "main" {
  name                = "asp-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.function_app_sku
  
  tags = var.tags
}

# Function App
resource "azurerm_linux_function_app" "main" {
  name                       = "func-${var.project_name}-${var.environment}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  service_plan_id            = azurerm_service_plan.main.id
  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key
  
  site_config {
    application_stack {
      python_version = "3.11"
    }
    
    cors {
      allowed_origins = var.cors_allowed_origins
    }
    
    application_insights_key               = azurerm_application_insights.main.instrumentation_key
    application_insights_connection_string = azurerm_application_insights.main.connection_string
  }
  
  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "COSMOS_DB_ENDPOINT"             = azurerm_cosmosdb_account.main.endpoint
    "COSMOS_DB_KEY"                  = azurerm_cosmosdb_account.main.primary_key
    "COSMOS_DB_DATABASE"             = azurerm_cosmosdb_sql_database.main.name
    "SEARCH_SERVICE_ENDPOINT"        = "https://${azurerm_search_service.main.name}.search.windows.net"
    "SEARCH_SERVICE_KEY"             = azurerm_search_service.main.primary_key
    "SEARCH_INDEX_NAME"              = "knowledge-base"
    "AZURE_OPENAI_ENDPOINT"          = var.azure_openai_endpoint
    "AZURE_OPENAI_KEY"               = var.azure_openai_key
    "AZURE_OPENAI_DEPLOYMENT_NAME"   = var.azure_openai_deployment_name
    "STORAGE_CONNECTION_STRING"      = azurerm_storage_account.main.primary_connection_string
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = var.tags
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  
  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
  
  capabilities {
    name = "EnableServerless"
  }
  
  tags = var.tags
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "agro-autoresolve"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Cosmos DB Containers
resource "azurerm_cosmosdb_sql_container" "tickets" {
  name                = "tickets"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_path  = "/id"
}

resource "azurerm_cosmosdb_sql_container" "agents" {
  name                = "agents"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_path  = "/id"
}

resource "azurerm_cosmosdb_sql_container" "metrics" {
  name                = "metrics"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_path  = "/date"
}

resource "azurerm_cosmosdb_sql_container" "chat_history" {
  name                = "chat-history"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_path  = "/ticketId"
}

# Azure Cognitive Search
resource "azurerm_search_service" "main" {
  name                = "search-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.search_service_sku
  
  tags = var.tags
}
