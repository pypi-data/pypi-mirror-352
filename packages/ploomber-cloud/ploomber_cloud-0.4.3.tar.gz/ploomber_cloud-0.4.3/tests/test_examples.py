import json
import sys

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

from ploomber_cloud.cli import cli
from ploomber_cloud import examples


CMD_NAME = "ploomber-cloud"


@pytest.mark.parametrize(
    "location",
    [
        "",
        "examples",
        "examples/flask",
    ],
)
def test_examples(set_key, monkeypatch, capsys, location):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples"])
    monkeypatch.setattr(
        examples.click,
        "prompt",
        Mock(side_effect=["flask", "Basic app: A basic Flask app.", location]),
    )
    mock_requests_get = Mock()

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_get.side_effect = requests_get

    with pytest.raises(SystemExit):
        cli()

    if not location:
        location = "basic-app"

    assert Path(location).exists()
    assert Path(location, "app.py").exists()


def test_examples_name(set_key, monkeypatch):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "flask/basic-app"])
    monkeypatch.setattr(examples.click, "prompt", Mock(side_effect=[""]))
    mock_requests_get = Mock()

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_get.side_effect = requests_get

    with pytest.raises(SystemExit):
        cli()

    assert Path("basic-app").exists()
    assert Path("basic-app/app.py").exists()
    assert Path("basic-app/README.md").exists()
    assert Path("basic-app/requirements.txt").exists()


def test_examples_docker(set_key, monkeypatch):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "docker/jupyterlab"])
    monkeypatch.setattr(examples.click, "prompt", Mock(side_effect=[""]))
    mock_requests_get = Mock()

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_get.side_effect = requests_get

    with pytest.raises(SystemExit):
        cli()

    assert Path("jupyterlab").exists()
    assert Path("jupyterlab/requirements.txt").exists()
    assert Path("jupyterlab/jupyter_server_config.py").exists()
    assert Path("jupyterlab/Dockerfile").exists()


def test_examples_docker_error(set_key, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "docker/invalid"])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert "docker/invalid does not exist." in capsys.readouterr().err.strip()


NAME_ERROR_MSG = """Error: Invalid example choice. \
Either the framework or the project is missing.
Command should be in the format:

 $ ploomber-cloud examples framework/example-name

 or to select from a menu of examples:

 $ ploomber-cloud examples

To clear the cache:

 $ ploomber-cloud examples --clear-cache
 """


def test_examples_name_error(set_key, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "invalid"])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert NAME_ERROR_MSG.strip() == capsys.readouterr().err.strip()


@pytest.mark.parametrize(
    "example, msg",
    [
        ("framework/basic-app", "framework: framework"),
        ("streamlit/invalid", "project: invalid"),
    ],
)
def test_examples_framework_error(set_key, monkeypatch, capsys, example, msg):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", example])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert (
        f"Invalid example choice. Couldn't find {msg}."
        in capsys.readouterr().err.strip()
    )


def test_examples_file_exists_error(set_key, monkeypatch, capsys):
    Path("basic-app/").mkdir()
    Path("basic-app/app.py").touch()
    Path("basic-app/requirements.txt").touch()
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "flask/basic-app"])
    monkeypatch.setattr(examples.click, "prompt", Mock(side_effect=[""]))

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert (
        "Error: File already exists in this path. Choose a different location."
        in capsys.readouterr().err.strip()
    )


def test_examples_missing_api_key_message(set_key, monkeypatch, capsys):
    monkeypatch.setenv("PLOOMBER_CLOUD_KEY", "")
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "flask/basic-app"])
    monkeypatch.setattr(examples.click, "prompt", Mock(side_effect=[""]))

    with pytest.raises(SystemExit):
        cli()

    assert examples.MISSING_API_KEY_MSG in capsys.readouterr().out


def test_examples_metadata_not_updated(set_key, monkeypatch, tmp_empty, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "examples", "chainlit/basic-app"])
    monkeypatch.setattr(
        examples.click,
        "prompt",
        Mock(
            side_effect=[
                "chainlit",
                "Basic app: A basic Chainlit application to get started.",
                "",
            ]
        ),
    )

    monkeypatch.setattr(examples, "CLONED_REPO_PATH", Path(tmp_empty, "doc-repo"))
    monkeypatch.setattr(
        examples, "METADATA_PATH", Path(tmp_empty, ".ploomber-cloud-metadata")
    )

    timestamp = datetime.now().timestamp()
    examples_json = {
        "flask": {
            "basic-app": {
                "title": "Basic app",
                "description": "A basic Flask app.",
                "path": "/some_path/examples/flask/basic-app",
                "parsed": True,
            }
        }
    }
    metadata = json.dumps(dict(timestamp=timestamp, examples=examples_json), indent=4)
    Path(tmp_empty, ".ploomber-cloud-metadata").write_text(metadata)

    mock_requests_get = Mock()

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_get.side_effect = requests_get

    with pytest.raises(SystemExit):
        cli()

    updated_metadata = json.loads(
        Path(tmp_empty, ".ploomber-cloud-metadata").read_text()
    )["examples"]
    assert updated_metadata == examples_json
    assert (
        "Error: Invalid example choice. Couldn't find framework: chainlit."
        in capsys.readouterr().err
    )


def test_examples_clear_cache(set_key, monkeypatch, tmp_empty):
    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "examples", "chainlit/basic-app", "--clear-cache"]
    )
    monkeypatch.setattr(
        examples.click,
        "prompt",
        Mock(
            side_effect=[
                "chainlit",
                "Basic app: A basic Chainlit application to get started.",
                "",
            ]
        ),
    )

    monkeypatch.setattr(examples, "CLONED_REPO_PATH", Path(tmp_empty, "doc-repo"))
    monkeypatch.setattr(
        examples, "METADATA_PATH", Path(tmp_empty, ".ploomber-cloud-metadata")
    )

    timestamp = datetime.now().timestamp()
    examples_json = {
        "flask": {
            "basic-app": {
                "title": "Basic app",
                "description": "A basic Flask app.",
                "path": "/some_path/examples/flask/basic-app",
                "parsed": True,
            }
        }
    }
    metadata = json.dumps(dict(timestamp=timestamp, examples=examples_json), indent=4)
    Path(tmp_empty, ".ploomber-cloud-metadata").write_text(metadata)

    mock_requests_get = Mock()

    def requests_get(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_get.side_effect = requests_get

    with pytest.raises(SystemExit):
        cli()

    assert Path("", "chainlit").exists()
    assert Path("", "chainlit", "app.py").exists()
    updated_metadata = json.loads(
        Path(tmp_empty, ".ploomber-cloud-metadata").read_text()
    )["examples"]
    assert updated_metadata != examples_json
    assert updated_metadata["chainlit"]["basic-app"]["title"] == "Basic app"


def test_examples_clear_cache_error(set_key, monkeypatch, tmp_empty, capsys):
    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "examples", "flask/invalid", "--clear-cache"]
    )

    with pytest.raises(SystemExit):
        cli()

    assert "Couldn't find project: invalid." in capsys.readouterr().err
