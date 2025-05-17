---
page_type: sample
languages:
- php
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

## Contents

Outline the file contents of the repository. It helps users navigate the codebase, build configuration and any related assets.

| File/folder       | Description                                |
|-------------------|--------------------------------------------|
| `/images`             | Sample images.                        |
| `/thumbs`      | Sample image thumbnails.      |
| `50x.html`    | HTTP500 page for NGINX            |
| `delete.php`    | Deletes converted images.             |
| `index.html`    | Main page for app.             |
| `listImages.php`        | List all images contained in images folder.             |
| `process.php`           | Convert JPGs to PNGs.             |
| `process.php_broken`    | Sample of broken file.             |
| `process.php_working`   | Sample of fixed file.             |
| `starter-template.css`  | CSS template             |
| `startup.sh`  | Startup script that copies the 50x.html file         |
| `CONTRIBUTING.md` | Guidelines for contributing to the sample. |
| `README.md`       | This README file.                          |
| `LICENSE`         | The license for the sample.                |

## Prerequisites / Steup / Running the sample / Key concepts

See http://docs.microsoft.com/azure/app-service/tutorial-sre-agent. 

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
