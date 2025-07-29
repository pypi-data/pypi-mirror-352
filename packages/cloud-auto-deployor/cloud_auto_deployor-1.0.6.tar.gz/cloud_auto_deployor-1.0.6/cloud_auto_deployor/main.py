import json
import os
import subprocess
import time

from cloud_auto_deployor.builder import build_docker_image
from cloud_auto_deployor.acr_handler import login_acr, enable_admin, get_credentials
from cloud_auto_deployor.aci_deployer import deploy_container
from cloud_auto_deployor.logger import get_logs

def main(config_path="config.json"):
    CONFIG_PATH = os.path.abspath(config_path)

    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)

        # Step 0: Ensure infrastructure exists
        ensure_resource_group_exists(config['resource_group'], config['location'])
        ensure_acr_exists(config['acr_name'], config['resource_group'], config['location'])

        # 🔐 Enable Admin Access for ACR
        enable_admin(config['acr_name'])

        # Step 1–2: Build and push Docker image
        full_tag = build_docker_image(
            config['image_name'],
            config['image_tag'],
            config['acr_name']
        )

        # Step 3: Login to ACR
        login_acr(config['acr_name'])

        # Step 4: Deploy to Azure Container Instance
        username, password = get_credentials(config['acr_name'])
        deploy_container(config, full_tag, username, password)

        # Step 5: Fetch container logs (optional)
        get_logs(config['resource_group'], config['container_name'])

        # Step 6: Hold the container briefly to allow Azure to collect logs
        print("✅ Deployment finished. Waiting for 30 seconds for Azure logs to appear...")
        time.sleep(30)

        return True  # success

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False  # failure


# Utilities for infra checks

def ensure_acr_exists(acr_name, resource_group, location):
    result = subprocess.run(
        ["az", "acr", "show", "--name", acr_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(f"⚠️ ACR '{acr_name}' not found. Creating it...")
        subprocess.run(
            ["az", "acr", "create",
             "--resource-group", resource_group,
             "--name", acr_name,
             "--sku", "Basic",
             "--location", location],
            check=True
        )
        print("⏳ Waiting 60 seconds for ACR to fully initialize...")
        time.sleep(60)

def ensure_resource_group_exists(resource_group, location):
    result = subprocess.run(
        ["az", "group", "show", "--name", resource_group],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(f"⚠️ Resource group '{resource_group}' not found. Creating it...")
        subprocess.run(
            ["az", "group", "create",
             "--name", resource_group,
             "--location", location],
            check=True
        )

if __name__ == "__main__":
    main()
    print("✅ Deployment complete. Waiting 30 seconds for Azure logs to become available...")
    time.sleep(30)  # Let container stay alive before it exits