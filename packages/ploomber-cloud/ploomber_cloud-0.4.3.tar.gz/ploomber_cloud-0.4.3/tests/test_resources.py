import sys
from pathlib import Path
from unittest.mock import Mock
import json

import pytest

from ploomber_cloud.cli import cli
from ploomber_cloud import api, resources

CMD_NAME = "ploomber-cloud"


@pytest.mark.parametrize("account_type", ["community", "pro", "teams"])
def test_resources(monkeypatch, set_key, capsys, account_type):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources"])
    monkeypatch.setattr(
        resources.click,
        "prompt",
        Mock(side_effect=["0", "1", "2"]),
    )
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"_model": {"type": account_type}}))

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    with open("ploomber-cloud.json") as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "docker",
            "resources": {"cpu": 1.0, "ram": 2, "gpu": 0},
        }


@pytest.mark.parametrize("account_type", ["community", "pro", "teams"])
def test_resources_force(monkeypatch, set_key, capsys, account_type):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources", "--force"])
    monkeypatch.setattr(
        resources.click,
        "prompt",
        Mock(side_effect=["0", "1", "2"]),
    )
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"_model": {"type": account_type}}))

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    with open("ploomber-cloud.json") as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "docker",
            "resources": {"cpu": 1.0, "ram": 2, "gpu": 0},
        }


@pytest.mark.parametrize("account_type", ["pro", "teams"])
def test_resources_preselects_for_gpu(monkeypatch, set_key, capsys, account_type):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources", "--force"])
    monkeypatch.setattr(
        resources.click,
        "prompt",
        Mock(side_effect=["1"]),
    )
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"_model": {"type": account_type}}))

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    with open("ploomber-cloud.json") as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "docker",
            "resources": {"cpu": 4.0, "ram": 12, "gpu": 1},
        }
    assert (
        "CPU and RAM options are fixed when you select 1 or more GPUs."
    ) in capsys.readouterr().out


def test_resources_not_initialized_message(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources"])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert (
        "Project not initialized. "
        "Run 'ploomber-cloud init' to initialize your project."
    ) in capsys.readouterr().err


def test_resources_already_configured_message(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources"])
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text(
        '{"id": "someid", "type": "docker", \
"resources": {"cpu": 1.0, "ram": 1, "gpu": 1}}'
    )

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert (
        "Resources already configured: \n"
        "1.0 CPU, 1 RAM, 1 GPU\n"
        "Run 'ploomber-cloud resources --force' to re-configure them. "
    ) in capsys.readouterr().err


def test_resource_custom_config(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "resources", "--config", "custom.json"])
    monkeypatch.setattr(
        resources.click,
        "prompt",
        Mock(side_effect=["0", "1", "2"]),
    )
    Path("custom.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"_model": {"type": "community"}}))

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    with open("custom.json") as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "docker",
            "resources": {"cpu": 1.0, "ram": 2, "gpu": 0},
        }
