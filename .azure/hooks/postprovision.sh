#!/usr/bin/env bash
set -e

echo "Zipping source code for deployment to the 'broken' slot..."

# Create zip of the current app contents
zip -r slot-deploy.zip . -x ".git/*" "slot-deploy.zip" > /dev/null

# Get values from azd environment
APP_NAME=$(azd env get-values --output json | jq -r '.APP_NAME')
RESOURCE_GROUP=$(azd env get-values --output json | jq -r '.AZURE_RESOURCE_GROUP')
SLOT_NAME="broken"

echo "Deploying zip to slot '$SLOT_NAME' on app '$APP_NAME' in resource group '$RESOURCE_GROUP'..."

az webapp deploy \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --slot "$SLOT_NAME" \
  --src-path slot-deploy.zip \
  --type zip

echo "Broken slot deployment complete."
