#!/usr/bin/env bash
set -e

if [ -f "slot-deploy.zip" ]; then
  echo "slot-deploy.zip already exists, reusing it."
else
  echo "Zipping source code for deployment to the 'broken' slot..."
  zip -r slot-deploy.zip . -x ".git/*" "slot-deploy.zip" > /dev/null
fi

# Correct variable names as per azd conventions
APP_NAME=$(azd env get-values --output json | jq -r '.AZURE_WEB_APP_NAME')
RESOURCE_GROUP=$(azd env get-values --output json | jq -r '.AZURE_RESOURCE_GROUP')
SLOT_NAME="broken"

echo "Deploying zip to slot '$SLOT_NAME' on app '$APP_NAME' in resource group '$RESOURCE_GROUP'..."

if [[ -z "$APP_NAME" || "$APP_NAME" == "null" ]]; then
  echo "ERROR: Could not determine App Service name! Check your azd env and .env file."
  exit 2
fi

az webapp deploy \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --slot "$SLOT_NAME" \
  --src-path slot-deploy.zip \
  --type zip

echo "Broken slot deployment complete."

if [ -f "slot-deploy.zip" ]; then
  echo "🧹 Removing old slot-deploy.zip..."
  rm slot-deploy.zip
fi