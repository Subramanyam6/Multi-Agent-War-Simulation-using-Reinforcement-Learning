# Azure Deployment Instructions

## Fixing the 409 Conflict Error

The updated workflow needs Azure credentials to stop/start the App Service and clear deployment locks. Follow these steps:

1. **Create Azure Service Principal**

   Run the following Azure CLI command to create a service principal:

   ```bash
   # Login to Azure CLI (if not already logged in)
   az login

   # Create a service principal with Contributor role
   az ad sp create-for-rbac --name "GitHubDeployPrincipal" \
                           --role contributor \
                           --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/rg-multi-agent-rl-war \
                           --sdk-auth
   ```

   This will output a JSON object with the credentials.

2. **Add Service Principal to GitHub**

   - Copy the entire JSON output from the previous command
   - Go to your GitHub repository > Settings > Secrets and variables > Actions
   - Create a new repository secret named `AZURE_CREDENTIALS` and paste the JSON as the value

3. **Ensure Publish Profile is Up to Date**

   - Go to the Azure Portal > App Service > Your app (multi-agent-rl-war)
   - Download a new publish profile
   - Update your GitHub repository secret named `AZURE_WEBAPP_PUBLISH_PROFILE` with the new content

4. **Manually Reset the App Service**

   Before running the updated workflow, perform these steps in the Azure Portal:

   - Go to App Service > Your app > Deployment Center
   - Click "Disconnect" to remove any existing deployment configuration
   - Go to App Service > Your app > Overview > Stop
   - Wait 30 seconds
   - Go to App Service > Your app > Overview > Start
   - Wait for the app to fully start

5. **Run the GitHub Workflow**

   - Go to the Actions tab in your GitHub repository
   - Select the "Build and deploy Python app to Azure Web App" workflow
   - Click "Run workflow" and select the main branch

The updated workflow will now:
1. Stop the App Service to release any locks
2. Restart the SCM site to clear lingering deployments
3. Deploy the application with a clean slate
4. Start the App Service after deployment

This should resolve the 409 Conflict error. 