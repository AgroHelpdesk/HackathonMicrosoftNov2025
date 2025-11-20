variable "project_name" {
  description = "Nome do projeto (usado para nomenclatura de recursos)"
  type        = string
  default     = "agroautoresolve"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Região do Azure"
  type        = string
  default     = "brazilsouth"
}

variable "function_app_sku" {
  description = "SKU do App Service Plan para Functions"
  type        = string
  default     = "B1" # Basic tier para desenvolvimento
  # Para produção, considere: "P1v2" ou "P2v2"
}

variable "search_service_sku" {
  description = "SKU do Azure Cognitive Search"
  type        = string
  default     = "basic"
  # Opções: free (limitado), basic, standard, standard2, standard3
}

variable "cors_allowed_origins" {
  description = "Origens permitidas para CORS"
  type        = list(string)
  default     = [
    "http://localhost:5173",
    "http://localhost:3000"
  ]
}

variable "azure_openai_endpoint" {
  description = "Endpoint do Azure OpenAI"
  type        = string
  sensitive   = true
  default     = ""
}

variable "azure_openai_key" {
  description = "Chave de API do Azure OpenAI"
  type        = string
  sensitive   = true
  default     = ""
}

variable "azure_openai_deployment_name" {
  description = "Nome do deployment do modelo no Azure OpenAI"
  type        = string
  default     = "gpt-4"
}

variable "tags" {
  description = "Tags para recursos Azure"
  type        = map(string)
  default = {
    Project     = "Agro Auto-Resolve"
    Environment = "Development"
    ManagedBy   = "Terraform"
    Hackathon   = "Microsoft Nov 2025"
  }
}
