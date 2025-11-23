# GitHub Actions CI/CD Setup

This directory contains the GitHub Actions workflow for automated deployment to Azure.

## Workflow: `azure-deploy.yml`

Automatically deploys the application when code is pushed to the `main` branch.

### Jobs

1. **build-and-deploy-frontend**
   - Builds the React/Vite frontend
   - Deploys to Azure Static Web Apps

2. **build-and-deploy-backend**
   - Sets up Python environment
   - Installs Azure Functions dependencies
   - Deploys to Azure Functions

### Required Secrets

The workflow requires the following GitHub secrets to be configured:

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `AZURE_CREDENTIALS` | Service Principal credentials for Azure login | Run `setup-github-secrets.ps1` |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token for Static Web Apps | Run `setup-github-secrets.ps1` |
| `GITHUB_TOKEN` | Automatically provided by GitHub Actions | Auto-generated |

## Setup Instructions

### Prerequisites

1. Azure resources deployed (run `.\deploy.ps1`)
2. GitHub CLI installed (optional but recommended)
   ```bash
   winget install GitHub.cli
   ```
3. GitHub Personal Access Token with `repo` and `workflow` scopes
   - Generate at: https://github.com/settings/tokens

### Automated Setup

Run the setup script to configure all secrets automatically:

```powershell
.\setup-github-secrets.ps1 -GitHubRepo "owner/repo" -GitHubToken "ghp_xxxx"
```

Or run interactively (will prompt for inputs):

```powershell
.\setup-github-secrets.ps1
```

### Manual Setup

If the automated script fails, set secrets manually:

1. **Create Service Principal:**
   ```bash
   az ad sp create-for-rbac --name "sp-github-deploy" \
     --role Contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/rg-agro-autoresolve-dev \
     --sdk-auth
   ```
   Copy the JSON output and set as `AZURE_CREDENTIALS` secret.

2. **Get Static Web App Token:**
   ```bash
   az staticwebapp secrets list \
     --name swa-agro-autoresolve \
     --resource-group rg-agro-autoresolve-dev \
     --query "properties.apiKey" -o tsv
   ```
   Set as `AZURE_STATIC_WEB_APPS_API_TOKEN` secret.

3. **Set Secrets in GitHub:**
   - Go to: `https://github.com/{owner}/{repo}/settings/secrets/actions`
   - Click "New repository secret"
   - Add both secrets

## Testing the Workflow

### Trigger Manually

From the Actions tab in GitHub:
1. Go to Actions → "Deploy to Azure"
2. Click "Run workflow"
3. Select branch and run

### Trigger on Push

Simply push to `main` branch:
```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

## Monitoring

- **GitHub Actions**: https://github.com/{owner}/{repo}/actions
- **Azure Portal**: https://portal.azure.com
  - Static Web App: Deployment Center
  - Functions App: Deployment Center

## Troubleshooting

### Frontend Build Fails

**Issue**: Missing dependencies
```
Solution: npm ci
```

**Issue**: Build errors
```
Check: web-frontend/package.json scripts
Verify: All environment variables are set
```

### Backend Deployment Fails

**Issue**: Authentication error
```
Verify: AZURE_CREDENTIALS secret is correct
Check: Service Principal has Contributor role
```

**Issue**: Function app not found
```
Verify: func-agro-autoresolve exists in Azure
Check: Resource group name in workflow matches config
```

### Secrets Not Working

**Issue**: Secrets not accessible in workflow
```
Verify: Secrets are set at repository level (not environment)
Check: Secret names match exactly (case-sensitive)
Confirm: GitHub token has correct scopes
```

## Workflow Customization

### Deploy to Different Environments

Add environment-specific workflows:

```yaml
# .github/workflows/azure-deploy-staging.yml
on:
  push:
    branches:
      - develop
env:
  AZURE_FUNCTIONAPP_NAME: func-agro-autoresolve-staging
  RESOURCE_GROUP: rg-agro-autoresolve-staging
```

### Add Testing Before Deploy

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd web-frontend
          npm ci
          npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    # ... deploy steps
```

### Deploy Only on Tag

```yaml
on:
  push:
    tags:
      - 'v*'
```

## Security Best Practices

1. **Rotate Secrets Regularly**: Update Service Principal credentials every 90 days
2. **Least Privilege**: Service Principal has Contributor only on resource group
3. **Audit Logs**: Monitor deployment logs in Azure Portal
4. **Branch Protection**: Require PR reviews before merging to main
5. **Environment Secrets**: Use GitHub Environments for production secrets

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure Static Web Apps Deploy Action](https://github.com/Azure/static-web-apps-deploy)
- [Azure Functions Deploy Action](https://github.com/Azure/functions-action)
- [Azure Login Action](https://github.com/Azure/login)
