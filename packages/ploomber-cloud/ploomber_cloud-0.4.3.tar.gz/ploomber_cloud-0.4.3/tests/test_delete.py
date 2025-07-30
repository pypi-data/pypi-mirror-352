import sys
import pytest
from pathlib import Path
from unittest.mock import Mock

from ploomber_cloud import api, delete
from ploomber_cloud.cli import cli


CMD_NAME = "ploomber-cloud"


def test_delete(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete"])
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_delete = Mock(name="requests.delete")

    def requests_delete(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"project_id": "someid"}))

    mock_requests_delete.side_effect = requests_delete

    monkeypatch.setattr(api.requests, "delete", mock_requests_delete)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert "Project someid has been successfully deleted" in capsys.readouterr().out
    mock_requests_delete.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/someid",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


def test_delete_error(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete"])
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_delete = Mock(name="requests.delete")

    def requests_delete(*args, **kwargs):
        return Mock(ok=False, json=Mock(return_value={"project_id": "someid"}))

    mock_requests_delete.side_effect = requests_delete

    monkeypatch.setattr(api.requests, "delete", mock_requests_delete)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert "Error deleting project someid" in capsys.readouterr().err.strip()


def test_delete_with_project_id(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete", "--project-id", "someid"])

    mock_requests_delete = Mock(name="requests.delete")

    def requests_delete(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"project_id": "someid"}))

    mock_requests_delete.side_effect = requests_delete

    monkeypatch.setattr(api.requests, "delete", mock_requests_delete)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert "Project someid has been successfully deleted" in capsys.readouterr().out
    mock_requests_delete.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/someid",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


def test_delete_with_project_id_error(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete", "--project-id", "someid"])

    mock_requests_delete = Mock(name="requests.delete")

    def requests_delete(*args, **kwargs):
        return Mock(ok=False, json=Mock(return_value={"project_id": "someid"}))

    mock_requests_delete.side_effect = requests_delete

    monkeypatch.setattr(api.requests, "delete", mock_requests_delete)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert "Error deleting project someid" in capsys.readouterr().err.strip()


def test_delete_all_with_confirm(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete", "--all"])
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(return_value={"projects": [{"id": "someid", "name": None}]}),
        )

    mock_requests_get.side_effect = requests_get

    mock_requests_delete = Mock(name="requests.delete")

    def requests_delete(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"project_id": "someid"}))

    mock_requests_delete.side_effect = requests_delete

    monkeypatch.setattr(api.requests, "get", mock_requests_get)
    monkeypatch.setattr(api.requests, "delete", mock_requests_delete)
    monkeypatch.setattr(delete.click, "prompt", Mock(side_effect=["delete all"]))

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert "All projects have been successfully deleted" in capsys.readouterr().out
    mock_requests_delete.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


@pytest.mark.parametrize("input", ["N", "n"])
def test_delete_all_with_confirm_cancelled(monkeypatch, set_key, capsys, input):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "delete", "--all"])
    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    monkeypatch.setattr(delete.click, "prompt", Mock(side_effect=[input]))

    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(return_value={"projects": [{"id": "someid", "name": None}]}),
        )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert "cancelled" in capsys.readouterr().out
