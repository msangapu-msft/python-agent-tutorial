---
page_type: sample
languages:
- python
products:
- app-service
description: "App Service Tutorial to be used with ttp://docs.microsoft.com/azure/app-service/tutorial-sre-agent."
urlFragment: "appsvc-troubleshoot-azure-monitor"
---

# App-Service-Agent-Tutorial
Agent Tutorial for App Service


<!-- 
Guidelines on README format: https://review.docs.microsoft.com/help/onboard/admin/samples/concepts/readme-template?branch=master

Guidance on onboarding samples to docs.microsoft.com/samples: https://review.docs.microsoft.com/help/onboard/admin/samples/process/onboarding?branch=master

Taxonomies for products and languages: https://review.docs.microsoft.com/new-hope/information-architecture/metadata/taxonomies?branch=master
-->

This is a sample image app to be used with http://docs.microsoft.com/azure/app-service/tutorial-sre-agent. The app converts JPG images to PNG. A "code bug" has been introduced for the troubleshooting scenario.

# Azure App Service SRE Memory Demo – Flask Image Converter

This sample Flask web app is designed for Azure App Service SRE troubleshooting demos. The app allows you to upload, view, and convert JPG images to PNG, and can intentionally trigger memory exhaustion in a deployment slot for root cause analysis.

---

## Features

- Upload, list, and convert JPG images to PNG.
- Deployment slot (e.g., "broken") can simulate an out-of-memory condition.
- Toggle the memory bug on/off using the `MEMORY_BUG` app setting.
- Built-in memory usage logging.

---

## Project Structure

- `app.py` – Main Flask application.
- `startup.sh` – Standard startup script.
- `startup_broken.sh` – Startup script for the broken slot (optional).
- `requirements.txt` – Python dependencies.
- `main.bicep` – Azure Bicep template to provision the app and slot.
- `static/` – Static files (including uploaded images and thumbnails).
- `converted/` – Folder for converted PNG images.

---

## How It Works

### 1. Production Slot

- Normal app behavior.
- No memory errors triggered.

### 2. Broken Slot

- Add the Azure App Setting: `MEMORY_BUG=1` (or `true` or `yes`).
- When converting images, the app tries to allocate a huge list, simulating a **MemoryError**.
- Demonstrates memory issues for SRE root cause analysis.

---

## Deploying to Azure

You can deploy using **Azure Developer CLI (azd)**, **Bicep**, or through the **Azure Portal**.

### Prerequisites

- Azure Subscription
- Python 3.13
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

### Quick Steps

1. **Provision Resources**

   ```sh
   azd up
   # OR
   az deployment group create -f main.bicep -g <your-resource-group>


2. **Deploy Code**
    - Use Azure Portal, VS Code, or CLI to deploy your code to the App Service.

3. **Set Up the Broken Slot**
    - In Azure Portal, navigate to your App Service.
    - Create a deployment slot (e.g., named broken).
    - In the slot, add an app setting:
        Name:  MEMORY_BUG
        Value: 1
    - Restart the slot if needed.

## Testing

### Production slot
- Visit `https://<your-app-name>.azurewebsites.net`
- Upload and convert images — should work normally.

### Broken slot
- Visit `https://<your-app-name>-broken.azurewebsites.net`
- Try to convert images — you should see memory errors when `MEMORY_BUG` is set.

---

## Troubleshooting

- Application logs are available in the `/home/LogFiles/` directory (access via Kudu/Advanced Tools or Azure Portal).
- If you hit a `MemoryError`, verify your app setting and check the logs.
- If conversions work normally in the main slot but fail in the slot with `MEMORY_BUG`, your setup is correct.

---

## Authors

Created by **Mangesh Sangapu**  
Sample app for SRE and Azure App Service troubleshooting tutorials.


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
