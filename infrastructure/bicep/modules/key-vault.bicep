// ============================================================================
// Azure Key Vault Module
// ============================================================================
// Provisions Azure Key Vault for secure secret management

@description('Nome do projeto')
param projectName string

@description('Ambiente (dev, staging, prod)')
param environment string

@description('Localização dos recursos')
param location string = resourceGroup().location

@description('Tags para os recursos')
param tags object = {}

@description('Object ID do Function App (Managed Identity)')
param functionAppPrincipalId string

@description('Object ID do usuário/service principal para acesso inicial')
param deploymentPrincipalId string = ''

// Variables
var keyVaultName = 'kv-${projectName}-${environment}'

// ============================================================================
// Key Vault
// ============================================================================
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// ============================================================================
// RBAC Assignments
// ============================================================================

// Function App - Key Vault Secrets User
resource functionAppSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionAppPrincipalId, 'SecretsUser')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Deployment Principal - Key Vault Administrator (if provided)
resource deploymentAdmin 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deploymentPrincipalId != '') {
  name: guid(keyVault.id, deploymentPrincipalId, 'Administrator')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00482a5a-887f-4fb3-b363-3b7fe8e74483') // Key Vault Administrator
    principalId: deploymentPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Outputs
// ============================================================================
output keyVaultId string = keyVault.id
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
