from unittest.mock import patch
from cloud_auto_deployor.acr_handler import login_acr, enable_admin, get_credentials
import subprocess

@patch("subprocess.run")
def test_login_acr(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    login_acr("myacr")
    mock_run.assert_called_with(["az", "acr", "login", "--name", "myacr"], check=True)

@patch("subprocess.run")
def test_enable_admin(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    enable_admin("myacr")
    mock_run.assert_called_with([
        "az", "acr", "update",
        "--name", "myacr",
        "--admin-enabled", "true"
    ], check=True)

@patch("subprocess.run")
def test_get_credentials(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0,
        stdout=b'{"username": "fakeuser", "passwords": [{"value": "fakepass"}]}'
    )
    user, pwd = get_credentials("myacr")
    assert user == "fakeuser"
    assert pwd == "fakepass"