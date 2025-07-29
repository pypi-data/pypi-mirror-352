
# ☁️ cloud_auto_deployor

[![PyPI version](https://badge.fury.io/py/cloud-auto-deployor.svg)](https://pypi.org/project/cloud-auto-deployor/)

**cloud_auto_deployor** is a Python package that simplifies end-to-end deployment of test automation projects to Azure using Docker and Azure Container Instances (ACI).  
Ideal for local developers, QA teams, and CI/CD use cases.

---

##  Features

* Auto-builds Docker image from your automation project
* Pushes the image to Azure Container Registry (ACR)
* Deploys the container to Azure Container Instance (ACI)
* Automatically runs your test suite (e.g. Pytest) in the container
* No manual Azure Portal steps required

---

##  Installation

```bash
pip install cloud-auto-deployor
```

> Make sure you have `Docker` and `Azure CLI` installed and logged in (`az login`).

---

##  Setup

Your test automation project should include:

```
demo_project/
├── Dockerfile
├── requirements.txt
├── tests/
│   └── test_example.py
├── run_tests.py           # Triggers pytest
└── config.json            # Azure details (see below)
```

###  Example `config.json`

```json
{
  "resource_group": "<your_resource_group>",
  "acr_name": "<your_acr_name>",
  "image_name": "<your_image_name>",
  "image_tag": "v1",
  "container_name": "<your_container_name>",
  "location": "<your_region>"
}
```

---

##  Usage

From your test project root (where `config.json` lives), run:

```bash
python -m cloud_auto_deployor.main
```

### What happens:

1. Reads `config.json`
2. Builds Docker image using your Dockerfile
3. Pushes to ACR (auto-creates if needed)
4. Deploys container instance (ACI)
5. Automatically triggers `run_tests.py` to run your tests
6. ✅ Results appear in Azure Portal Logs

---

##  Sample `run_tests.py`

```python
import pytest
import os
import sys

def run_tests():
    sys.path.insert(0, os.getcwd())
    exit_code = pytest.main(["-vv", "tests/"])
    return exit_code

if __name__ == "__main__":
    run_tests()
```

---

##  Uninstall / Clean Up

To remove the container:

```bash
az container delete \
  --name <your_container_name> \
  --resource-group <your_resource_group> \
  --yes
```

To remove the image from ACR:

```bash
az acr repository delete \
  --name <your_acr_name> \
  --image <your_image_name>:<your_image_tag> \
  --yes
```

---

## Delete Entire Resource Group

	az group delete --name <your_resource_group> --yes --no-wait
   
	Explanation:
	**•	--name: Name of your resource group (e.g., demo-deploy-group)
	•	--yes: Auto-confirms the deletion prompt
	•	--no-wait: Returns immediately without waiting for the deletion to complete (optional)**

##  Author

Developed by Raja Periyasamy – Automation Lead | Azure DevOps Follower  
📧 [cloudautodeployer@gmail.com](mailto:cloudautodeployer@gmail.com)

---



##  License

MIT License

---

##  Release Notes

**v1.0.6**
-- enable acr access
- Initial open-source release
- Supports end-to-end Docker → ACR → ACI automation
- Auto-triggers test execution from `run_tests.py`
- Removed tracked `config.json`, now properly gitignored
- Minor cleanup and security best practices applied
- read me file changes
- Azure resources delete expression syntax updated
