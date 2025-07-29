import os

def login_acr(acr_name):
    os.system(f"az acr login --name {acr_name}")

def enable_admin(acr_name):
    os.system(f"az acr update --name {acr_name} --admin-enabled true")

def get_credentials(acr_name):
    username = os.popen(f"az acr credential show --name {acr_name} --query username -o tsv").read().strip()
    password = os.popen(f"az acr credential show --name {acr_name} --query \"passwords[0].value\" -o tsv").read().strip()
    return username, password

def tag_and_push_image(image_name, tag, acr_name):
    full_tag = f"{acr_name}.azurecr.io/{image_name}:{tag}"
    os.system(f"docker tag {image_name}:{tag} {full_tag}")
    os.system(f"docker push {full_tag}")
    return full_tag
