output "resource_group_name" {
  description = "Nome do Resource Group"
  value       = azurerm_resource_group.main.name
}

output "function_app_name" {
  description = "Nome do Function App"
  value       = azurerm_linux_function_app.main.name
}

output "function_app_url" {
  description = "URL do Function App"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}"
}

output "function_app_identity" {
  description = "Managed Identity do Function App"
  value       = azurerm_linux_function_app.main.identity[0].principal_id
}

output "storage_account_name" {
  description = "Nome da Storage Account"
  value       = azurerm_storage_account.main.name
}

output "storage_connection_string" {
  description = "Connection string da Storage Account"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "cosmos_db_endpoint" {
  description = "Endpoint do Cosmos DB"
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "cosmos_db_key" {
  description = "Primary key do Cosmos DB"
  value       = azurerm_cosmosdb_account.main.primary_key
  sensitive   = true
}

output "cosmos_db_database_name" {
  description = "Nome do database do Cosmos DB"
  value       = azurerm_cosmosdb_sql_database.main.name
}

output "search_service_name" {
  description = "Nome do Azure Cognitive Search"
  value       = azurerm_search_service.main.name
}

output "search_service_endpoint" {
  description = "Endpoint do Azure Cognitive Search"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "search_service_key" {
  description = "Admin key do Azure Cognitive Search"
  value       = azurerm_search_service.main.primary_key
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "Instrumentation key do Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string do Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}
