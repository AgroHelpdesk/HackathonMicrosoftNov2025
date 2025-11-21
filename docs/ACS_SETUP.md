# Azure Communication Services Setup Guide

This guide walks you through setting up Azure Communication Services (ACS) for the Agro Auto-Resolve system.

## Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Permissions to create resources in your subscription

## 1. Create ACS Resource

### Using Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Communication Services"
4. Click "Create"
5. Fill in the details:
   - **Subscription**: Select your subscription
   - **Resource Group**: `rg-agro-dev` (or your preferred name)
   - **Resource Name**: `acs-agro-dev`
   - **Data Location**: Choose your region (e.g., Brazil South)
6. Click "Review + Create" then "Create"

### Using Azure CLI

```bash
# Create resource group
az group create \
  --name rg-agro-dev \
  --location brazilsouth

# Create ACS resource
az communication create \
  --name acs-agro-dev \
  --location global \
  --data-location BrazilSouth \
  --resource-group rg-agro-dev
```

## 2. Get Connection String

### Using Azure Portal

1. Navigate to your ACS resource
2. Go to "Keys" under "Settings"
3. Copy the "Primary connection string"
4. Store it securely (we'll add it to Key Vault later)

### Using Azure CLI

```bash
az communication list-key \
  --name acs-agro-dev \
  --resource-group rg-agro-dev \
  --query primaryConnectionString \
  --output tsv
```

## 3. Configure Chat

### Enable Chat Feature

Chat is enabled by default in ACS. No additional configuration needed.

### Create Chat Thread (Programmatically)

The backend will create chat threads automatically when needed. Here's how it works:

```python
from azure.communication.chat import ChatClient
from azure.communication.identity import CommunicationIdentityClient

# Create identity client
identity_client = CommunicationIdentityClient.from_connection_string(connection_string)

# Create user
user = identity_client.create_user()

# Create chat client
chat_client = ChatClient(endpoint, CommunicationTokenCredential(user_token))

# Create chat thread
create_chat_thread_result = chat_client.create_chat_thread(
    topic="Support Ticket #123"
)
thread_id = create_chat_thread_result.chat_thread.id
```

## 4. Configure SMS

### Get Phone Number

1. Navigate to your ACS resource in Azure Portal
2. Go to "Phone numbers" under "Channels"
3. Click "Get" to acquire a phone number
4. Select:
   - **Country**: Brazil (+55)
   - **Number type**: Toll-free or Geographic
   - **Capabilities**: Check "Send SMS" and "Receive SMS"
5. Complete the purchase

### Using Azure CLI

```bash
# List available phone numbers
az communication phonenumber list-available \
  --resource-group rg-agro-dev \
  --communication-service-name acs-agro-dev \
  --phone-number-type tollFree \
  --assignment-type application \
  --capabilities sms \
  --area-code 0800

# Purchase phone number
az communication phonenumber purchase \
  --resource-group rg-agro-dev \
  --communication-service-name acs-agro-dev \
  --phone-number "+5508001234567"
```

## 5. Configure Event Grid for Webhooks

### Create Event Grid System Topic

```bash
# Create Event Grid system topic for ACS
az eventgrid system-topic create \
  --name acs-events-agro-dev \
  --resource-group rg-agro-dev \
  --source /subscriptions/YOUR_SUB_ID/resourceGroups/rg-agro-dev/providers/Microsoft.Communication/CommunicationServices/acs-agro-dev \
  --topic-type Microsoft.Communication.CommunicationServices \
  --location global
```

### Create Event Subscriptions

#### For Chat Messages

```bash
az eventgrid system-topic event-subscription create \
  --name chat-message-received \
  --resource-group rg-agro-dev \
  --system-topic-name acs-events-agro-dev \
  --endpoint https://YOUR_FUNCTION_APP.azurewebsites.net/api/acs/chat/webhook \
  --endpoint-type webhook \
  --included-event-types Microsoft.Communication.ChatMessageReceived
```

#### For SMS Messages

```bash
az eventgrid system-topic event-subscription create \
  --name sms-received \
  --resource-group rg-agro-dev \
  --system-topic-name acs-events-agro-dev \
  --endpoint https://YOUR_FUNCTION_APP.azurewebsites.net/api/acs/sms/webhook \
  --endpoint-type webhook \
  --included-event-types Microsoft.Communication.SMSReceived
```

## 6. Store Secrets in Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name kv-agro-dev \
  --resource-group rg-agro-dev \
  --location brazilsouth

# Store ACS connection string
az keyvault secret set \
  --vault-name kv-agro-dev \
  --name ACS-CONNECTION-STRING \
  --value "YOUR_CONNECTION_STRING"

# Store ACS endpoint
az keyvault secret set \
  --vault-name kv-agro-dev \
  --name ACS-ENDPOINT \
  --value "https://acs-agro-dev.communication.azure.com"

# Store phone number
az keyvault secret set \
  --vault-name kv-agro-dev \
  --name ACS-PHONE-NUMBER \
  --value "+5508001234567"
```

## 7. Configure Function App

### Grant Function App Access to Key Vault

```bash
# Enable system-assigned managed identity
az functionapp identity assign \
  --name func-agro-dev \
  --resource-group rg-agro-dev

# Get the principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name func-agro-dev \
  --resource-group rg-agro-dev \
  --query principalId \
  --output tsv)

# Grant access to Key Vault
az keyvault set-policy \
  --name kv-agro-dev \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### Configure App Settings

```bash
az functionapp config appsettings set \
  --name func-agro-dev \
  --resource-group rg-agro-dev \
  --settings \
    "ACS_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=https://kv-agro-dev.vault.azure.net/secrets/ACS-CONNECTION-STRING/)" \
    "ACS_ENDPOINT=@Microsoft.KeyVault(SecretUri=https://kv-agro-dev.vault.azure.net/secrets/ACS-ENDPOINT/)" \
    "ACS_PHONE_NUMBER=@Microsoft.KeyVault(SecretUri=https://kv-agro-dev.vault.azure.net/secrets/ACS-PHONE-NUMBER/)"
```

## 8. Test the Setup

### Test Chat

```python
# Run this in your local environment
from azure.communication.chat import ChatClient
from azure.communication.identity import CommunicationIdentityClient
from azure.core.credentials import AzureKeyCredential

connection_string = "YOUR_CONNECTION_STRING"
endpoint = "https://acs-agro-dev.communication.azure.com"

# Create identity client
identity_client = CommunicationIdentityClient.from_connection_string(connection_string)

# Create user and get token
user = identity_client.create_user()
token_response = identity_client.get_token(user, scopes=["chat"])

print(f"User ID: {user.properties['id']}")
print(f"Token: {token_response.token}")

# Test creating a chat thread
from azure.communication.chat import ChatClient, CommunicationTokenCredential

chat_client = ChatClient(endpoint, CommunicationTokenCredential(token_response.token))

create_chat_thread_result = chat_client.create_chat_thread(
    topic="Test Support Ticket"
)

print(f"Thread ID: {create_chat_thread_result.chat_thread.id}")
```

### Test SMS

```python
from azure.communication.sms import SmsClient

connection_string = "YOUR_CONNECTION_STRING"
sms_client = SmsClient.from_connection_string(connection_string)

# Send test SMS
sms_responses = sms_client.send(
    from_="+5508001234567",  # Your ACS phone number
    to=["+5511999999999"],    # Test phone number
    message="Test message from Agro Auto-Resolve"
)

for sms_response in sms_responses:
    print(f"Message ID: {sms_response.message_id}")
    print(f"HTTP Status Code: {sms_response.http_status_code}")
    print(f"Successful: {sms_response.successful}")
```

## 9. Monitor Events

### View Event Grid Metrics

```bash
az monitor metrics list \
  --resource /subscriptions/YOUR_SUB_ID/resourceGroups/rg-agro-dev/providers/Microsoft.EventGrid/systemTopics/acs-events-agro-dev \
  --metric PublishSuccessCount,PublishFailCount \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z
```

### View Function App Logs

```bash
az functionapp log tail \
  --name func-agro-dev \
  --resource-group rg-agro-dev
```

## 10. Troubleshooting

### Common Issues

#### Chat Messages Not Received

1. Check Event Grid subscription is active:
   ```bash
   az eventgrid system-topic event-subscription show \
     --name chat-message-received \
     --resource-group rg-agro-dev \
     --system-topic-name acs-events-agro-dev
   ```

2. Verify webhook endpoint is accessible
3. Check Function App logs for errors

#### SMS Not Sending

1. Verify phone number is active and has SMS capability
2. Check ACS connection string is correct
3. Verify recipient phone number format (+55XXXXXXXXXXX)

#### Authentication Errors

1. Verify Key Vault access policy is set correctly
2. Check managed identity is enabled on Function App
3. Verify secret URIs in app settings are correct

### Enable Diagnostic Logging

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group rg-agro-dev \
  --workspace-name law-agro-dev

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group rg-agro-dev \
  --workspace-name law-agro-dev \
  --query id \
  --output tsv)

# Enable diagnostic settings for ACS
az monitor diagnostic-settings create \
  --name acs-diagnostics \
  --resource /subscriptions/YOUR_SUB_ID/resourceGroups/rg-agro-dev/providers/Microsoft.Communication/CommunicationServices/acs-agro-dev \
  --workspace $WORKSPACE_ID \
  --logs '[{"category": "ChatOperational", "enabled": true}, {"category": "SMSOperational", "enabled": true}]'
```

## Resources

- [ACS Documentation](https://docs.microsoft.com/azure/communication-services/)
- [ACS Chat Quickstart](https://docs.microsoft.com/azure/communication-services/quickstarts/chat/get-started)
- [ACS SMS Quickstart](https://docs.microsoft.com/azure/communication-services/quickstarts/sms/send)
- [Event Grid Documentation](https://docs.microsoft.com/azure/event-grid/)
- [Key Vault Documentation](https://docs.microsoft.com/azure/key-vault/)

## Next Steps

- Configure [Azure Content Safety](https://docs.microsoft.com/azure/cognitive-services/content-safety/) for message moderation
- Set up [Azure Monitor Alerts](https://docs.microsoft.com/azure/azure-monitor/alerts/alerts-overview) for critical events
- Implement [rate limiting](https://docs.microsoft.com/azure/communication-services/concepts/service-limits) for SMS
- Configure [email notifications](https://docs.microsoft.com/azure/communication-services/quickstarts/email/send-email) via ACS
