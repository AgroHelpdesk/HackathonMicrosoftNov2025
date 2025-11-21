// ============================================================================
// Azure Communication Services Module
// ============================================================================
// Provisions Azure Communication Services for Chat and SMS

@description('Nome do projeto')
param projectName string

@description('Ambiente (dev, staging, prod)')
param environment string

@description('Localização dos recursos')
param location string = resourceGroup().location

@description('Tags para os recursos')
param tags object = {}

// Variables
var acsName = 'acs-${projectName}-${environment}'
var emailServiceName = 'email-${projectName}-${environment}'

// ============================================================================
// Azure Communication Services
// ============================================================================
resource communicationService 'Microsoft.Communication/communicationServices@2023-04-01' = {
  name: acsName
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'Brazil'
  }
}

// ============================================================================
// Email Service (for notifications)
// ============================================================================
resource emailService 'Microsoft.Communication/emailServices@2023-04-01' = {
  name: emailServiceName
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'Brazil'
  }
}

// Email Domain
resource emailDomain 'Microsoft.Communication/emailServices/domains@2023-04-01' = {
  parent: emailService
  name: 'AzureManagedDomain'
  location: 'global'
  properties: {
    domainManagement: 'AzureManaged'
    userEngagementTracking: 'Disabled'
  }
}

// Link Email Service to Communication Service
resource emailLink 'Microsoft.Communication/communicationServices/domains@2023-04-01' = {
  parent: communicationService
  name: emailDomain.name
  location: 'global'
  properties: {
    domainManagement: 'AzureManaged'
  }
}

// ============================================================================
// Event Grid System Topic (for ACS events)
// ============================================================================
resource eventGridSystemTopic 'Microsoft.EventGrid/systemTopics@2023-12-15-preview' = {
  name: 'acs-events-${projectName}-${environment}'
  location: location
  tags: tags
  properties: {
    source: communicationService.id
    topicType: 'Microsoft.Communication.CommunicationServices'
  }
}

// ============================================================================
// Outputs
// ============================================================================
output communicationServiceId string = communicationService.id
output communicationServiceName string = communicationService.name
@secure()
output communicationServiceConnectionString string = communicationService.listKeys().primaryConnectionString
@secure()
output communicationServiceKey string = communicationService.listKeys().primaryKey
output communicationServiceEndpoint string = 'https://${communicationService.name}.communication.azure.com'
output emailServiceId string = emailService.id
output emailDomainName string = emailDomain.properties.mailFromSenderDomain
output eventGridSystemTopicId string = eventGridSystemTopic.id
