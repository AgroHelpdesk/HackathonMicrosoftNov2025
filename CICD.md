# CI/CD Documentation - Agro Auto-Resolve

Este documento descreve a configuração e uso do pipeline CI/CD implementado com GitHub Actions e Azure Bicep.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configuração Inicial](#configuração-inicial)
- [Workflows](#workflows)
- [Ambientes](#ambientes)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O projeto utiliza GitHub Actions para CI/CD com os seguintes componentes:

- **Backend**: FastAPI (Python 3.11) → Azure Functions
- **Frontend**: React + Vite → Azure Static Web Apps
- **Infraestrutura**: Bicep → Azure Resource Manager

### Arquitetura do Pipeline

```mermaid
graph LR
    A[Push/PR] --> B{Qual componente?}
    B -->|Backend| C[Backend CI/CD]
    B -->|Frontend| D[Frontend CI/CD]
    B -->|Infra| E[Infrastructure CI/CD]
    B -->|PR| F[PR Validation]
    
    C --> G[Lint & Test]
    C --> H[Build]
    C --> I[Deploy to Azure Functions]
    
    D --> J[Lint & Build]
    D --> K[Deploy to Static Web Apps]
    
    E --> L[Validate Bicep]
    E --> M[What-If Analysis]
    E --> N[Deploy Infrastructure]
    
    F --> O[Validate All Components]
</mermaid>

## 🔧 Pré-requisitos

### 1. Azure CLI

```bash
# Instalar Azure CLI
# Windows (PowerShell):
winget install Microsoft.AzureCLI

# Verificar instalação
az --version
az bicep version
```

### 2. Conta Azure

- Subscription ativa do Azure
- Permissões para criar Service Principal
- Acesso ao Azure Portal

### 3. Repositório GitHub

- Repositório com acesso de administrador
- Permissão para configurar Secrets

## ⚙️ Configuração Inicial

### Passo 1: Criar Service Principal

O Service Principal permite que o GitHub Actions se autentique no Azure.

```bash
# Login no Azure
az login

# Definir subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Criar Service Principal
az ad sp create-for-rbac \
  --name "github-actions-agro-autoresolve" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

**Importante**: Salve o JSON retornado! Você precisará dele para configurar os secrets.

Exemplo de output:
```json
{
  "clientId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "clientSecret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "subscriptionId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "tenantId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### Passo 2: Configurar GitHub Secrets

Vá para: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Configure os seguintes secrets:

| Secret Name | Descrição | Valor |
|-------------|-----------|-------|
| `AZURE_CREDENTIALS` | JSON completo do Service Principal | Todo o JSON do passo anterior |
| `AZURE_SUBSCRIPTION_ID` | ID da subscription Azure | Valor de `subscriptionId` |
| `AZURE_TENANT_ID` | ID do tenant Azure | Valor de `tenantId` |
| `AZURE_CLIENT_ID` | ID do cliente | Valor de `clientId` |
| `AZURE_CLIENT_SECRET` | Secret do cliente | Valor de `clientSecret` |

### Passo 3: Configurar Azure Static Web Apps (Frontend)

```bash
# Criar Static Web App
az staticwebapp create \
  --name agro-autoresolve-frontend \
  --resource-group rg-agroautoresolve-dev \
  --location brazilsouth \
  --sku Free

# Obter deployment token
az staticwebapp secrets list \
  --name agro-autoresolve-frontend \
  --resource-group rg-agroautoresolve-dev \
  --query "properties.apiKey" -o tsv
```

Adicione o token como secret:

| Secret Name | Valor |
|-------------|-------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token obtido acima (dev) |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROD` | Token para produção |

### Passo 4: Criar Resource Group

```bash
# Criar Resource Group para desenvolvimento
az group create \
  --name rg-agroautoresolve-dev \
  --location brazilsouth

# Criar Resource Group para produção (opcional)
az group create \
  --name rg-agroautoresolve-prod \
  --location brazilsouth
```

## 🔄 Workflows

### 1. Infrastructure CI/CD

**Arquivo**: `.github/workflows/infrastructure-ci-cd.yml`

**Triggers**:
- Push para `main` (arquivos em `infrastructure/bicep/**`)
- Pull Request
- Manual (workflow_dispatch)

**Jobs**:
1. **Validate**: Valida sintaxe e configuração do Bicep
2. **Preview**: Gera análise What-If (apenas em PRs)
3. **Deploy-Dev**: Deploy automático para desenvolvimento
4. **Deploy-Prod**: Deploy manual para produção

**Uso Manual**:
```bash
# Via GitHub UI:
Actions → Infrastructure CI/CD → Run workflow → Selecionar environment
```

### 2. Backend CI/CD

**Arquivo**: `.github/workflows/backend-ci-cd.yml`

**Triggers**:
- Push para `main` (arquivos em `backend/**`)
- Pull Request

**Jobs**:
1. **Lint-and-Test**: Flake8, Black, Pytest
2. **Build**: Cria pacote de deployment
3. **Deploy-Dev**: Deploy para Azure Functions (dev)
4. **Deploy-Prod**: Deploy para Azure Functions (prod)

**Testes Locais**:
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
black --check .
flake8 .
```

### 3. Frontend CI/CD

**Arquivo**: `.github/workflows/frontend-ci-cd.yml`

**Triggers**:
- Push para `main` (arquivos em `web-frontend/**`)
- Pull Request

**Jobs**:
1. **Lint-and-Build**: Lint e build do React app
2. **Deploy-Dev**: Deploy para Static Web Apps (dev)
3. **Deploy-Prod**: Deploy para Static Web Apps (prod)

**Testes Locais**:
```bash
cd web-frontend
npm install
npm run build
npm run dev
```

### 4. PR Validation

**Arquivo**: `.github/workflows/pr-validation.yml`

**Triggers**:
- Qualquer Pull Request para `main`

**Jobs**:
1. **Validate-Backend**: Lint e testes do backend
2. **Validate-Frontend**: Build do frontend
3. **Validate-Bicep**: Validação do Bicep
4. **PR-Summary**: Resumo dos resultados

## 🌍 Ambientes

### Development (dev)

- **Trigger**: Push automático para `main`
- **Resource Group**: `rg-agroautoresolve-dev`
- **Function App**: `func-agroautoresolve-dev`
- **SKUs**: Econômicos (B1, Basic)

### Production (prod)

- **Trigger**: Manual (workflow_dispatch)
- **Resource Group**: `rg-agroautoresolve-prod`
- **Function App**: `func-agroautoresolve-prod`
- **SKUs**: Produção (P1v2, Standard)
- **Approval**: Requer aprovação manual

## 🐛 Troubleshooting

### Erro: "Azure credentials not found"

**Solução**: Verifique se o secret `AZURE_CREDENTIALS` está configurado corretamente.

```bash
# Recriar Service Principal
az ad sp create-for-rbac \
  --name "github-actions-agro-autoresolve" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

### Erro: "Resource group not found"

**Solução**: Crie o Resource Group manualmente:

```bash
az group create \
  --name rg-agroautoresolve-dev \
  --location brazilsouth
```

### Erro: "Bicep validation failed"

**Solução**: Valide localmente:

```bash
cd infrastructure/bicep
az bicep build --file main.bicep
az deployment group validate \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

### Erro: "Function App deployment failed"

**Solução**: Verifique se a Function App existe:

```bash
az functionapp list \
  --resource-group rg-agroautoresolve-dev \
  --output table
```

Se não existir, execute o workflow de infraestrutura primeiro.

### Erro: "Static Web App token invalid"

**Solução**: Regenere o token:

```bash
az staticwebapp secrets list \
  --name agro-autoresolve-frontend \
  --resource-group rg-agroautoresolve-dev \
  --query "properties.apiKey" -o tsv
```

Atualize o secret no GitHub.

## 📊 Monitoramento

### Ver Logs de Deployment

```bash
# Listar deployments
az deployment group list \
  --resource-group rg-agroautoresolve-dev \
  --output table

# Ver detalhes de um deployment
az deployment group show \
  --resource-group rg-agroautoresolve-dev \
  --name DEPLOYMENT_NAME
```

### Application Insights

Acesse o Application Insights no Azure Portal para:
- Logs de aplicação
- Métricas de performance
- Rastreamento de erros
- Análise de uso

## 🔐 Segurança

### Boas Práticas

1. **Nunca commite secrets** no código
2. **Use GitHub Secrets** para credenciais
3. **Rotacione Service Principals** periodicamente
4. **Limite permissões** do Service Principal
5. **Use ambientes protegidos** para produção

### Rotação de Credentials

```bash
# Deletar Service Principal antigo
az ad sp delete --id CLIENT_ID

# Criar novo
az ad sp create-for-rbac \
  --name "github-actions-agro-autoresolve" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth

# Atualizar secrets no GitHub
```

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Functions CI/CD](https://learn.microsoft.com/azure/azure-functions/functions-how-to-github-actions)
- [Azure Static Web Apps CI/CD](https://learn.microsoft.com/azure/static-web-apps/github-actions-workflow)

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs no GitHub Actions
2. Consulte a documentação do Azure
3. Revise este documento de troubleshooting
4. Abra uma issue no repositório
