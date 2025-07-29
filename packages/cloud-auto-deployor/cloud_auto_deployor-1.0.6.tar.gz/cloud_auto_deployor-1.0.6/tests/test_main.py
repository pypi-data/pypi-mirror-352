import subprocess
from unittest.mock import patch
from cloud_auto_deployor.main import ensure_acr_exists, ensure_resource_group_exists


@patch("subprocess.run")
def test_acr_already_exists(mock_run):
    # Simulate: ACR exists
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    ensure_acr_exists("myacr", "demo-rg", "eastus")
    assert mock_run.call_count == 1
    mock_run.assert_called_with(["az", "acr", "show", "--name", "myacr"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@patch("subprocess.run")
def test_acr_not_exists_and_created(mock_run):
    # Simulate: ACR does not exist, then gets created
    mock_run.side_effect = [
        subprocess.CompletedProcess(args=[], returncode=1),  # Not found
        subprocess.CompletedProcess(args=[], returncode=0)   # Created
    ]
    ensure_acr_exists("myacr", "demo-rg", "eastus")
    assert mock_run.call_count == 2


@patch("subprocess.run")
def test_acr_create_failure_raises_error(mock_run):
    # Simulate: creation command fails
    mock_run.side_effect = [
        subprocess.CompletedProcess(args=[], returncode=1),  # Not found
        subprocess.CalledProcessError(returncode=1, cmd="az acr create")
    ]
    try:
        ensure_acr_exists("myacr", "demo-rg", "eastus")
        assert False, "Expected CalledProcessError"
    except subprocess.CalledProcessError:
        assert True


@patch("subprocess.run")
def test_resource_group_already_exists(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    ensure_resource_group_exists("demo-rg", "eastus")
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_resource_group_not_exists_and_created(mock_run):
    mock_run.side_effect = [
        subprocess.CompletedProcess(args=[], returncode=1),  # Not found
        subprocess.CompletedProcess(args=[], returncode=0)   # Created
    ]
    ensure_resource_group_exists("demo-rg", "eastus")
    assert mock_run.call_count == 2