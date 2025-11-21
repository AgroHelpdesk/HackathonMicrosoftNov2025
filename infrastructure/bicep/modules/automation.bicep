// ============================================================================
// Azure Automation and Logic Apps Module
// ============================================================================
// Provisions Azure Automation Account and Logic Apps for runbooks

@description('Nome do projeto')
param projectName string

@description('Ambiente (dev, staging, prod)')
param environment string

@description('Localização dos recursos')
param location string = resourceGroup().location

@description('Tags para os recursos')
param tags object = {}

// Variables
var automationAccountName = 'aa-${projectName}-${environment}'

// ============================================================================
// Azure Automation Account
// ============================================================================
resource automationAccount 'Microsoft.Automation/automationAccounts@2023-11-01' = {
  name: automationAccountName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    sku: {
      name: 'Basic'
    }
    encryption: {
      keySource: 'Microsoft.Automation'
    }
    publicNetworkAccess: true
  }
}

// ============================================================================
// Python 3 Runtime for Runbooks
// ============================================================================
resource pythonPackage 'Microsoft.Automation/automationAccounts/python3Packages@2023-11-01' = {
  parent: automationAccount
  name: 'requests'
  properties: {
    contentLink: {
      uri: 'https://files.pythonhosted.org/packages/requests/requests-2.31.0-py3-none-any.whl'
    }
  }
}

// ============================================================================
// Sample Runbooks
// ============================================================================

// Runbook para reset de telemetria
resource resetTelemetryRunbook 'Microsoft.Automation/automationAccounts/runbooks@2023-11-01' = {
  parent: automationAccount
  name: 'Reset-Telemetry'
  location: location
  tags: tags
  properties: {
    runbookType: 'Python3'
    logProgress: true
    logVerbose: true
    description: 'Runbook para reset de telemetria de equipamentos'
    publishContentLink: {
      uri: 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/quickstarts/microsoft.automation/101-automation/scripts/AzureAutomationTutorialPython3.py'
      version: '1.0.0.0'
    }
  }
}

// Runbook para verificação de estoque
resource inventoryCheckRunbook 'Microsoft.Automation/automationAccounts/runbooks@2023-11-01' = {
  parent: automationAccount
  name: 'Check-Inventory'
  location: location
  tags: tags
  properties: {
    runbookType: 'Python3'
    logProgress: true
    logVerbose: true
    description: 'Runbook para verificação de estoque de insumos agrícolas'
    publishContentLink: {
      uri: 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/quickstarts/microsoft.automation/101-automation/scripts/AzureAutomationTutorialPython3.py'
      version: '1.0.0.0'
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
output automationAccountId string = automationAccount.id
output automationAccountName string = automationAccount.name
output automationAccountIdentity string = automationAccount.identity.principalId
