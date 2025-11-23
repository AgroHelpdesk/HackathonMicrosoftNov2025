# Infrastructure as Code

This directory contains scripts to provision the Azure resources required for the Agro Auto-Resolve application.

## Files

*   `config.json`: Configuration file defining resource names, location, and tags. **Edit this file before running the script** to ensure unique resource names.
*   `deploy_resources.ps1`: PowerShell script that uses the Azure CLI (`az`) to create the resources defined in `config.json`.

## Prerequisites

1.  **Azure CLI**: Ensure `az` is installed and logged in (`az login`).
2.  **PowerShell**: Required to run the deployment script.
3.  **Python 3.10+**: Required for data upload scripts.
4.  **Python Packages**: Install dependencies with `pip install -r requirements.txt`

## Usage

1.  Open `config.json` and update the `resourceGroupName` or resource names if needed (Azure resource names must be globally unique).
2.  Open a PowerShell terminal in this directory.
3.  Run the script:
    ```powershell
    ./deploy_resources.ps1
    ```

## Uploading Dataset to Blob Storage

After deploying the infrastructure, upload the dataset files:

1.  Install Python dependencies:
    ```powershell
    pip install -r requirements.txt
    ```
2.  Run the upload script:
    ```powershell
    python upload_dataset.py
    ```
3.  Verify the upload:
    ```powershell
    az storage blob list --account-name stagroautoresolve001 --container-name knowledge-base --output table --auth-mode login
    ```

## Resources Created

*   **Resource Group**: Container for all resources.
*   **Storage Account**: For Azure Functions and Blob Storage (Dataset).
*   **Cosmos DB**: Serverless SQL API for application data.
*   **Azure OpenAI**: For AI Agents.
*   **Azure AI Search**: For RAG (Vector Search).
*   **Function App**: Python runtime for the backend API.
*   **Static Web App**: For hosting the React Frontend.
