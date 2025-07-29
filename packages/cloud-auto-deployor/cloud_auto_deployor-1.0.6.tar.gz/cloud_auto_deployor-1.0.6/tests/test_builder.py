from unittest.mock import patch
from cloud_auto_deployor.builder import build_docker_image

@patch("subprocess.run")
def test_build_docker_image_success(mock_run):
    mock_run.return_value = None
    image_tag = build_docker_image("demo_app", "v2", "myacr")
    assert image_tag == "myacr.azurecr.io/demo_app:v2"