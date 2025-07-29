import os

def get_logs(resource_group, container_name):
    os.system(f"az container logs --name {container_name} --resource-group {resource_group}")
