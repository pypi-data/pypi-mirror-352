import os


def deploy_container(config, image, username, password):
    os.system(
        f"""az container create   --resource-group {config['resource_group']}   --name {config['container_name']}   --image {image}   --cpu {config['cpu']} --memory {config['memory_gb']}   --registry-login-server {config['acr_name']}.azurecr.io   --registry-username {username}   --registry-password {password}   --restart-policy Never   --os-type {config['os_type']}""")
