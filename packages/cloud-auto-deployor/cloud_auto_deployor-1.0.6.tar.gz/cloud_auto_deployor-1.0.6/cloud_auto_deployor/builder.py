import os


def build_docker_image(image_name, tag, acr_name):
    full_tag = f"{acr_name}.azurecr.io/{image_name}:{tag}"

    print(f"🔨 Building Docker image for linux/amd64 platform...")
    os.system(f"docker buildx build --platform linux/amd64 -t {image_name}:{tag} . --load")

    print(f"🏷️ Tagging image as {full_tag}")
    os.system(f"docker tag {image_name}:{tag} {full_tag}")

    print(f"☁️ Pushing image to Azure Container Registry...")
    os.system(f"docker push {full_tag}")

    return full_tag
