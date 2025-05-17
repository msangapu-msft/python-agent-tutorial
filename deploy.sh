#!/usr/bin/env bash
set -e

# ─── Variables ───────────────────────────────────────────────────────────────
AZURE_ENV_NAME="my-sre-app-env"
AZURE_LOCATION="centralus"
RAND=$(openssl rand -hex 3)  # 6-character random hex string
AZURE_RESOURCE_GROUP="rg-my-sre-app-env-$RAND"

# ─── 1) Ensure resource group exists ────────────────────────────────────────
if ! az group show --name "$AZURE_RESOURCE_GROUP" &>/dev/null; then
  echo "Creating resource group '$AZURE_RESOURCE_GROUP' in '$AZURE_LOCATION'..."
  az group create \
    --name "$AZURE_RESOURCE_GROUP" \
    --location "$AZURE_LOCATION"
else
  echo "Resource group '$AZURE_RESOURCE_GROUP' already exists."
fi

# ─── 2) Initialize azd environment if needed ───────────────────────────────
if ! azd env list | grep -q "^$AZURE_ENV_NAME\s"; then
  echo "Initializing azd environment '$AZURE_ENV_NAME'..."
  azd init --environment "$AZURE_ENV_NAME" --no-prompt
fi

# ─── 3) Set location (and RG) in azd env ───────────────────────────────────
echo "Configuring azd environment values..."
azd env set AZURE_LOCATION "$AZURE_LOCATION" --environment "$AZURE_ENV_NAME"
azd env set AZURE_RESOURCE_GROUP "$AZURE_RESOURCE_GROUP" --environment "$AZURE_ENV_NAME"

# ─── 4) Ensure postprovision.sh is executable ───────────────────────────────
HOOK_SCRIPT=".azure/hooks/postprovision.sh"
if [[ -f "$HOOK_SCRIPT" && ! -x "$HOOK_SCRIPT" ]]; then
  echo "Making $HOOK_SCRIPT executable..."
  chmod +x "$HOOK_SCRIPT"
fi

# ─── 5) Provision infra + deploy app ────────────────────────────────────────
echo "Provisioning resources and deploying application..."
azd up --environment "$AZURE_ENV_NAME" --no-prompt
