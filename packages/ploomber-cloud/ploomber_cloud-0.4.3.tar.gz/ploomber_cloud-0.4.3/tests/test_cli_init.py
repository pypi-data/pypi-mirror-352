import io
import sys
from pathlib import Path
from unittest.mock import Mock, call
import json
import zipfile

import pytest

from ploomber_core.exceptions import COMMUNITY

from ploomber_cloud.cli import cli
from ploomber_cloud import init, api, github
from ploomber_cloud.github import GITHUB_DOCS_URL
from ploomber_cloud.constants import CONFIGURE_RESOURCES_MESSAGE
from ploomber_cloud.exceptions import BasePloomberCloudException

CMD_NAME = "ploomber-cloud"

COMMUNITY = COMMUNITY.strip()


def test_set_key(monkeypatch, fake_ploomber_dir):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "key", "somekey"])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert (
        "cloud_key: somekey"
        in (fake_ploomber_dir / "stats" / "config.yaml").read_text()
    )


ALREADY_INITIALIZED_MESSAGE = f"""Error: Project already initialized with id: someid. \
Run \'ploomber-cloud deploy\' to deploy your \
project. To track its progress, add the --watch flag.
{COMMUNITY}"""


@pytest.mark.parametrize(
    "args", [[CMD_NAME, "init"], [CMD_NAME, "init", "--from-existing"]]
)
def test_init(monkeypatch, fake_ploomber_dir, capsys, args):
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    monkeypatch.setattr(sys, "argv", args)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert ALREADY_INITIALIZED_MESSAGE == capsys.readouterr().err.strip()


def test_init_invalid_env(monkeypatch, set_key):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    monkeypatch.setenv("_PLOOMBER_CLOUD_ENV", "invalid")

    with pytest.raises(BasePloomberCloudException) as excinfo:
        monkeypatch.setattr(api.endpoints, api.PloomberCloudEndpoints())

    assert (
        "Unknown environment: invalid. Valid options are: prod, dev, local"
        in str(excinfo.value).strip()
    )


def test_init_flow(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    out = capsys.readouterr().out
    assert CONFIGURE_RESOURCES_MESSAGE in out


def test_init_flow_yes(monkeypatch, set_key, capsys):
    Path("Dockerfile").touch()
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--yes"])
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    out = capsys.readouterr().out
    assert CONFIGURE_RESOURCES_MESSAGE in out


def test_init_force_flow(monkeypatch, set_key):
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--force"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    assert "some-other-id" == json.loads(Path("ploomber-cloud.json").read_text())["id"]


def test_init_force_retains_resources(monkeypatch, set_key, capsys):
    Path("ploomber-cloud.json").write_text(
        '{"id": "someid", "type": "docker", \
"resources": {"cpu": 0.5, "ram": 1, "gpu": 0}}'
    )

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--force"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    assert "some-other-id" == json.loads(Path("ploomber-cloud.json").read_text())["id"]
    assert {"cpu": 0.5, "ram": 1, "gpu": 0} == json.loads(
        Path("ploomber-cloud.json").read_text()
    )["resources"]
    assert (
        "WARNING: your previous resources configuration "
        "has been carried over: 0.5 CPU, 1 RAM, 0 GPU\n"
        "To change resources, run: 'ploomber-cloud resources --force'"
    ) in capsys.readouterr().out


def test_init_force_retains_labels(monkeypatch, set_key, capsys):
    Path("ploomber-cloud.json").write_text(
        '{"id": "someid", "type": "docker", \
"labels": ["label-one", "label-two"]}'
    )

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--force"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    assert "some-other-id" == json.loads(Path("ploomber-cloud.json").read_text())["id"]
    assert ["label-one", "label-two"] == json.loads(
        Path("ploomber-cloud.json").read_text()
    )["labels"]
    assert (
        (
            """WARNING: your previously added labels \
have been carried over: 'label-one', and 'label-two'.
To add more labels, run: 'ploomber-cloud resources --add' \
or to delete labels run 'ploomber-cloud resources --delete'"""
        )
        in capsys.readouterr().out
    )


CONFIGURE_WORKFLOW_MESSAGE = f"""You may create a GitHub workflow \
file for deploying your application by running 'ploomber-cloud github'.
To learn more about GitHub actions refer: \
{GITHUB_DOCS_URL}"""


@pytest.mark.parametrize("argv", [[CMD_NAME, "init"], [CMD_NAME, "init", "--force"]])
def test_init_configure_github_msg(monkeypatch, set_key, tmp_empty, capsys, argv):
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    Path(".git").mkdir()

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    assert CONFIGURE_WORKFLOW_MESSAGE.strip() in capsys.readouterr().out


UPDATE_WORKFLOW_MESSAGE = f""".github/workflows/ploomber-cloud.yaml \
seems outdated. You may update it by running 'ploomber-cloud github'.
To learn more about GitHub actions refer: \
{GITHUB_DOCS_URL}"""


@pytest.mark.parametrize("argv", [[CMD_NAME, "init"], [CMD_NAME, "init", "--force"]])
def test_init_configure_github_msg_workflow_file_outdated(
    monkeypatch, set_key, tmp_empty, capsys, argv
):
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))

    Path(".git").mkdir()
    Path(".github", "workflows").mkdir(parents=True)

    Path(".github/workflows/ploomber-cloud.yaml").write_text(
        """
name: Ploomber Cloud
"""
    )

    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )
    assert UPDATE_WORKFLOW_MESSAGE.strip() in capsys.readouterr().out


WORKFLOW_CREATED_MESSAGE = f"""'ploomber-cloud.yaml' file \
created in the path .github/workflows.
Please add, commit and push this file along with the \
'ploomber-cloud.json' file to trigger an action.
For details on configuring a GitHub secret please refer: \
{GITHUB_DOCS_URL}"""


def test_configure_workflow_create(monkeypatch, set_key, tmp_empty, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True]))
    mock_requests_get = Mock(name="requests.get")
    Path(".git").mkdir()

    mock_no_previous_secrets = Mock(return_value={})
    monkeypatch.setattr(
        api.PloomberCloudClient, "get_project_by_id", mock_no_previous_secrets
    )

    def requests_get(*args, **kwargs):
        return Mock(status_code=200, content=b"name: Ploomber Cloud")

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text()
        == "name: Ploomber Cloud"
    )
    assert WORKFLOW_CREATED_MESSAGE.strip() in capsys.readouterr().out


def test_configure_workflow_create_add_config_secret(
    monkeypatch, set_key, tmp_empty, capsys
):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True]))
    mock_requests_get = Mock(name="requests.get")
    Path(".git").mkdir()
    Path("ploomber-cloud.json").write_text(
        '{"id": "someid", "type": "docker", "secret-keys": ["TEST_VARIABLE", "another_one"]}'  # noqa
    )

    mock_no_previous_secrets = Mock(return_value={})
    monkeypatch.setattr(
        api.PloomberCloudClient, "get_project_by_id", mock_no_previous_secrets
    )

    def requests_get(*args, **kwargs):
        return Mock(
            status_code=200,
            content=b"""
      - name: Another job
        run: |
          multi line operation
          pip install ploomber-cloud

      - name: Deploy
        env:
          PLOOMBER_CLOUD_KEY: ${{ secrets.PLOOMBER_CLOUD_KEY }}
        run: |
          ploomber-cloud deploy --watch-incremental
        # Comment should still be in the folder
    """.strip(),
        )

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text()
        == """
      - name: Another job
        run: |
          multi line operation
          pip install ploomber-cloud

      - name: Deploy
        env:
          PLOOMBER_CLOUD_KEY: ${{ secrets.PLOOMBER_CLOUD_KEY }}
          TEST_VARIABLE: ${{ secrets.TEST_VARIABLE }}
          another_one: ${{ secrets.another_one }}
        run: |
          ploomber-cloud deploy --watch-incremental
        # Comment should still be in the folder
        """.strip()
    )
    assert WORKFLOW_CREATED_MESSAGE.strip() in capsys.readouterr().out


@pytest.mark.parametrize(
    "dotenv_secrets, previous_secrets, config_secrets",
    [
        ([], [], []),
        (["SECRET1", "SECRET2"], [], []),
        ([], ["SECRET1", "SECRET2"], []),
        ([], [], ["SECRET1", "SECRET2"]),
        (["SECRET1"], ["SECRET2"], []),
        (["SECRET1", "SECRET2"], ["SECRET2", "SECRET3"], ["SECRET1"]),
        (["SECRET1"], ["SECRET2"], ["SECRET1", "SECRET2"]),
    ],
    ids=[
        "no_secrets",
        "secrets_in_dotenv_only",
        "secrets_from_previous_deployment_only",
        "secrets_in_config_only",
        "secrets_in_dotenv_and_previous_deployment",
        "some_secrets_missing",
        "all_secrets_present",
    ],
)
def test_configure_workflow_add_missing_secret_to_config_when_user_accept(
    monkeypatch,
    set_key,
    tmp_empty,
    capsys,
    dotenv_secrets,
    previous_secrets,
    config_secrets,
):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True, True]))
    mock_requests_get = Mock(name="requests.get")

    # Mock the project
    Path(".git").mkdir()
    if dotenv_secrets:
        env_content = "\n".join(f"{secret}=mock_value" for secret in dotenv_secrets)
        Path(".env").write_text(env_content)
    if config_secrets:
        secret_keys_json = json.dumps(config_secrets)
        Path("ploomber-cloud.json").write_text(
            f'{{"id": "someid", "type": "docker", "secret-keys": {secret_keys_json}}}'
        )
    else:
        Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    # Mock fetch to get the secrets use on the last deployment
    mock_get_project = Mock(
        return_value={
            "id": "someid",
            "type": "docker",
            "name": "Test Project",
            "secrets": previous_secrets,
        }
    )
    monkeypatch.setattr(api.PloomberCloudClient, "get_project_by_id", mock_get_project)

    # Mock the get template request
    def requests_get(*args, **kwargs):
        return Mock(status_code=200, content=b"name: Ploomber Cloud")

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    output = capsys.readouterr().out
    missing_secrets = (set(previous_secrets) | set(dotenv_secrets)) - set(
        config_secrets
    )
    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text()
        == "name: Ploomber Cloud"
    )
    config_file = Path("ploomber-cloud.json").read_text()
    for secret in missing_secrets:
        assert secret in output
        assert secret in config_file
    assert WORKFLOW_CREATED_MESSAGE.strip() in output


def test_configure_workflow_only_warning_about_missing_secret_when_user_refuse(
    monkeypatch,
    set_key,
    tmp_empty,
    capsys,
):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True, False]))
    mock_requests_get = Mock(name="requests.get")
    dotenv_secrets = ["SECRET_1"]
    previous_secrets = ["SECRET_2"]
    config_secrets = ["SECRET_3"]

    # Mock the project
    Path(".git").mkdir()
    if dotenv_secrets:
        env_content = "\n".join(f"{secret}=mock_value" for secret in dotenv_secrets)
        Path(".env").write_text(env_content)
    if config_secrets:
        secret_keys_json = json.dumps(config_secrets)
        Path("ploomber-cloud.json").write_text(
            f'{{"id": "someid", "type": "docker", "secret-keys": {secret_keys_json}}}'
        )
    else:
        Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    # Mock fetch to get the secrets use on the last deployment
    mock_get_project = Mock(
        return_value={
            "id": "someid",
            "type": "docker",
            "name": "Test Project",
            "secrets": previous_secrets,
        }
    )
    monkeypatch.setattr(api.PloomberCloudClient, "get_project_by_id", mock_get_project)

    # Mock the get template request
    def requests_get(*args, **kwargs):
        return Mock(status_code=200, content=b"name: Ploomber Cloud")

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    output = capsys.readouterr().out
    missing_secrets = (set(previous_secrets) | set(dotenv_secrets)) - set(
        config_secrets
    )
    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text()
        == "name: Ploomber Cloud"
    )
    config_file = Path("ploomber-cloud.json").read_text()
    for secret in missing_secrets:
        assert secret in output
        assert secret not in config_file
    assert WORKFLOW_CREATED_MESSAGE.strip() in output


def test_configure_workflow_update(monkeypatch, set_key, tmp_empty, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True]))
    mock_requests_get = Mock(name="requests.get")
    Path(".git").mkdir()
    Path(".github", "workflows").mkdir(parents=True)

    Path(".github/workflows/ploomber-cloud.yaml").write_text(
        """
name: Ploomber Cloud
"""
    )

    def requests_get(*args, **kwargs):
        return Mock(status_code=200, content=b"name: Ploomber Cloud updated")

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text()
        == "name: Ploomber Cloud updated"
    )
    assert WORKFLOW_CREATED_MESSAGE.strip() in capsys.readouterr().out


def test_configure_workflow_update_not_required(
    monkeypatch, set_key, tmp_empty, capsys
):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    mock_requests_get = Mock(name="requests.get")
    Path(".git").mkdir()
    Path(".github", "workflows").mkdir(parents=True)

    Path(".github/workflows/ploomber-cloud.yaml").write_text(
        """
name: Ploomber Cloud
"""
    )

    def requests_get(*args, **kwargs):
        return Mock(status_code=200, content=b"name: Ploomber Cloud")

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert (
        Path(".github/workflows/ploomber-cloud.yaml").read_text().strip()
        == "name: Ploomber Cloud"
    )
    assert "Workflow file is up-to-date." in capsys.readouterr().out


NOT_GITHUB_ERROR_MESSAGE = f"""Error: Expected a \
.git/ directory in the current working directory. \
Run this from the repository root directory.
{COMMUNITY}"""


def test_configure_workflow_in_non_github_folder(
    monkeypatch, set_key, tmp_empty, capsys
):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert NOT_GITHUB_ERROR_MESSAGE.strip() in capsys.readouterr().err


WORKFLOW_REPONSE_ERROR = f"""Error: Failed to fetch \
GitHub workflow template. Please refer: \
{GITHUB_DOCS_URL}
{COMMUNITY}"""


def test_create_workflow_file_response_error(monkeypatch, set_key, tmp_empty, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "github"])
    monkeypatch.setattr(github.click, "confirm", Mock(side_effect=[True]))
    mock_requests_get = Mock(name="requests.get")

    Path(".git").mkdir()

    def requests_get(*args, **kwargs):
        return Mock(status_code=0)

    mock_requests_get.side_effect = requests_get

    monkeypatch.setattr(github.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert Path(".github/workflows/ploomber-cloud.yaml").exists() is False
    assert WORKFLOW_REPONSE_ERROR.strip() in capsys.readouterr().err


def test_init_flow_with_server_error(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["sometype"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=False, json=Mock(return_value={"detail": "some error"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/sometype",
        headers={"accept": "application/json", "api_key": "somekey"},
    )

    assert (
        (
            f"""Error: An error occurred: some error
{COMMUNITY}"""
        )
        in capsys.readouterr().err.strip()
    )


def test_init_infers_with_custom_config(monkeypatch, set_key):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--config", "custom.json"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")
    Path("Dockerfile").touch()

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )

    config = json.loads(Path("custom.json").read_text())
    assert config == {"id": "someid"}


def test_init_infers_project_type_if_dockerfile_exists(monkeypatch, set_key, capsys):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")
    Path("Dockerfile").touch()

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


@pytest.mark.parametrize(
    "project_type, statement",
    [
        ("panel", "import panel"),
        ("docker", "import docker"),
        ("solara", "import solara"),
        ("streamlit", "import streamlit"),
        ("panel", "from panel import test"),
        ("docker", "from docker import test"),
        ("solara", "from solara import test"),
        ("streamlit", "from streamlit import"),
        ("dash", "import dash"),
        ("dash", "from dash import test"),
        ("flask", "import flask"),
        ("flask", "from flask import test"),
        ("chainlit", "import chainlit"),
        ("chainlit", "from chainlit import test"),
    ],
)
def test_init_smart_infers_project_type(
    monkeypatch, set_key, capsys, project_type, statement
):
    Path("app.py").touch()
    Path("app.py").write_text(statement)
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        f"https://cloud-prod.ploomber.io/projects/{project_type}",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


@pytest.mark.parametrize(
    "project_type, statement",
    [
        ("fastapi", "import fastapi"),
        ("fastapi", "from fastapi import test"),
        ("gradio", "import gradio"),
        ("gradio", "from gradio import test"),
        ("shiny", "import shiny"),
        ("shiny", "from shiny import test"),
    ],
)
def test_init_smart_infers_docker_project_type(
    monkeypatch, set_key, capsys, project_type, statement
):
    Path("Dockerfile").touch()
    Path("app.py").touch()
    Path("app.py").write_text(statement)
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    found_type_message = f"This looks like a {project_type.capitalize()} project, \
which is supported via Docker."

    assert excinfo.value.code == 0
    assert found_type_message in capsys.readouterr().out
    mock_requests_post.assert_called_once_with(
        "https://cloud-prod.ploomber.io/projects/docker",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


def test_init_smart_infer_missing_dockerfile_message(
    monkeypatch,
    set_key,
    capsys,
):
    Path("app.py").touch()
    Path("app.py").write_text("import fastapi")
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    missing_dockerfile_message = "Your app is missing a Dockerfile. To learn more, \
go to: https://docs.cloud.ploomber.io/en/latest/apps/fastapi.html"

    assert excinfo.value.code == 0
    assert missing_dockerfile_message in capsys.readouterr().out


@pytest.mark.parametrize(
    "project_file, project_type",
    [("app.R", "shiny-r"), ("Dockerfile", "docker"), ("app.ipynb", "voila")],
)
def test_init_infers_project_type_file_based(
    monkeypatch, set_key, project_file, project_type
):
    Path(project_file).touch()
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(init.click, "confirm", Mock(side_effect=["y"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "someid"}))

    mock_requests_post.side_effect = requests_post

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    mock_requests_post.assert_called_once_with(
        f"https://cloud-prod.ploomber.io/projects/{project_type}",
        headers={"accept": "application/json", "api_key": "somekey"},
    )


@pytest.mark.parametrize(
    "config_path",
    [
        (None),
        ("custom1.json"),
        ("./subdir/custom2.json"),
        ("./subdir/subsubdir/custom3.json"),
        ("valid_case/custom4.json"),
    ],
    ids=[
        "default_config",
        "custom_config",
        "custom_config_in_subdir",
        "custom_config_in_subsubdir",
        "custom_config_in_subdir_with_missing_dot_slash",
    ],
)
def test_init_from_existing_flow(monkeypatch, set_key, capsys, config_path):
    cmd = [CMD_NAME, "init", "--from-existing", "--only-config"]
    if config_path:
        config_dir = Path(config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        cmd.append("--config")
        cmd.append(config_path)
    monkeypatch.setattr(sys, "argv", cmd)
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["someid"]))
    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(
                return_value={
                    "projects": [{"id": "someid", "name": None}],
                    "type": "sometype",
                    "jobs": [{"cpu": 0.5, "ram": 1, "gpu": 0}],
                }
            ),
        )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    # Delete ploomber-cloud.json if it exists
    path_to_json = Path(config_path) if config_path else Path("ploomber-cloud.json")
    if path_to_json.exists():
        path_to_json.unlink()

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert path_to_json.exists()
    with open(path_to_json) as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "sometype",
            "resources": {"cpu": 0.5, "ram": 1, "gpu": 0},
        }
    assert excinfo.value.code == 0
    mock_requests_get.assert_has_calls(
        [
            call(
                "https://cloud-prod.ploomber.io/projects",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
            call(
                "https://cloud-prod.ploomber.io/projects/someid",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
        ]
    )
    assert (
        "WARNING: your previous resources configuration "
        "has been carried over: 0.5 CPU, 1 RAM, 0 GPU\n"
        "To change resources, run: 'ploomber-cloud resources --force'"
    ) in capsys.readouterr().out


def test_init_from_existing_no_project_message(monkeypatch, set_key, capsys):
    # Try to init from existing with no existing projects
    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "init", "--from-existing", "--only-config"]
    )
    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(
                return_value={
                    "projects": [],
                }
            ),
        )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit):
        cli()

    assert (
        "You have no existing projects. Initialize without --from-existing."
        in capsys.readouterr().out
    )


def test_init_from_existing_project_exists(monkeypatch, set_key, capsys):
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "docker"}')

    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "init", "--from-existing", "--only-config"]
    )

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert ALREADY_INITIALIZED_MESSAGE.strip() in capsys.readouterr().err


def test_init_from_existing_force_flow(monkeypatch, set_key):
    Path("ploomber-cloud.json").write_text('{"id": "someid", "type": "sometype"}')
    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "init", "--from-existing", "--only-config", "--force"]
    )
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["some_existing_id"]))
    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(
                return_value={
                    "projects": [{"id": "some_existing_id", "name": None}],
                    "type": "sometype",
                    "jobs": [{"cpu": 0.5, "ram": 1, "gpu": 0}],
                }
            ),
        )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    path_to_json = Path("ploomber-cloud.json")
    assert path_to_json.exists()
    with open(path_to_json) as f:
        assert json.loads(f.read()) == {
            "id": "some_existing_id",
            "type": "sometype",
            "resources": {"cpu": 0.5, "ram": 1, "gpu": 0},
        }
    assert excinfo.value.code == 0
    mock_requests_get.assert_has_calls(
        [
            call(
                "https://cloud-prod.ploomber.io/projects",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
            call(
                "https://cloud-prod.ploomber.io/projects/some_existing_id",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
        ]
    )


@pytest.mark.parametrize("input", ["someid (custom-name)", "custom-name", "someid"])
def test_init_from_existing_custom_id_flow(monkeypatch, set_key, input, capsys):
    monkeypatch.setattr(
        sys, "argv", [CMD_NAME, "init", "--from-existing", "--only-config"]
    )
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=[input]))
    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        return Mock(
            ok=True,
            json=Mock(
                return_value={
                    "projects": [
                        {"id": "someid", "name": "custom-name"},
                        {"id": "another-id", "name": None},
                    ],
                    "type": "sometype",
                    "jobs": [{"cpu": 0.5, "ram": 1, "gpu": 0}],
                    "labels": ["label-one"],
                }
            ),
        )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    # Delete ploomber-cloud.json if it exists
    path_to_json = Path("ploomber-cloud.json")
    if path_to_json.exists():
        path_to_json.unlink()

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert path_to_json.exists()
    with open(path_to_json) as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "sometype",
            "resources": {"cpu": 0.5, "ram": 1, "gpu": 0},
            "labels": ["label-one"],
        }
    assert excinfo.value.code == 0
    mock_requests_get.assert_has_calls(
        [
            call(
                "https://cloud-prod.ploomber.io/projects",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
            call(
                "https://cloud-prod.ploomber.io/projects/someid",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
        ]
    )
    assert (
        "WARNING: your previous resources configuration "
        "has been carried over: 0.5 CPU, 1 RAM, 0 GPU\n"
        "To change resources, run: 'ploomber-cloud resources --force'"
    ) in capsys.readouterr().out


@pytest.fixture
def mock_zip_content():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("file1.txt", "content1")
        zf.writestr("file2.txt", "content2")
    return zip_buffer.getvalue()


@pytest.mark.parametrize(
    "config_flag, output_dir",
    [
        (None, "./test_output"),
        ("custom.json", "./custom_output"),
        ("./will_be_ignore/custom.json", "./someid"),  # Default taken
        ("./will/be/ignore/custom.json", "./nested_output/subdir/"),
        ("will_be_ ignore.json/custom.json", "./someid"),  # Default taken
    ],
    ids=[
        "default_config_specific_dir",
        "custom_config_specific_dir",
        "custom_config_subdir_default_dir",
        "custom_config_subdir_specific_dir",
        "custom_config_spaces_subdir_default_dir",
    ],
)
def test_init_download_from_existing_flow(
    monkeypatch, set_key, capsys, mock_zip_content, config_flag, output_dir
):
    cmd = [CMD_NAME, "init", "--from-existing"]
    if config_flag:
        cmd.append("--config")
        cmd.append(config_flag)
    monkeypatch.setattr(sys, "argv", cmd)
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["someid", output_dir]))
    mock_requests_get = Mock(name="requests.get")

    def requests_get(*args, **kwargs):
        if args[0].endswith("/files"):  # Assuming the zip endpoint ends with '/export'
            return Mock(
                ok=True,
                headers={"Content-Type": "application/zip"},
                content=mock_zip_content,
                iter_content=Mock(return_value=[mock_zip_content]),
            )
        else:
            return Mock(
                ok=True,
                json=Mock(
                    return_value={
                        "projects": [{"id": "someid", "name": None}],
                        "type": "sometype",
                        "jobs": [{"cpu": 0.5, "ram": 1, "gpu": 0}],
                    }
                ),
            )

    mock_requests_get.side_effect = requests_get
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    # Check if ploomber-cloud.json exist and have the correct content

    path_to_json = Path(
        f"{output_dir}/{'custom.json' if config_flag else 'ploomber-cloud.json'}"
    )
    assert path_to_json.exists()
    with open(path_to_json) as f:
        assert json.loads(f.read()) == {
            "id": "someid",
            "type": "sometype",
            "resources": {"cpu": 0.5, "ram": 1, "gpu": 0},
        }

    # Check if file1.txt and file2.txt exist and have correct content
    files = [
        ("file1.txt", Path(f"{output_dir}/file1.txt"), "content1"),
        ("file2.txt", Path(f"{output_dir}/file2.txt"), "content2"),
    ]

    for name, path, content in files:
        assert path.exists(), f"{name} does not exist in {path}"
        with open(path, "r") as f:
            assert f.read() == content, f"Content of {name} is incorrect: {f.read()}"

    assert excinfo.value.code == 0
    mock_requests_get.assert_has_calls(
        [
            call(
                "https://cloud-prod.ploomber.io/projects",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
            call(
                "https://cloud-prod.ploomber.io/projects/someid",
                headers={"accept": "application/json", "api_key": "somekey"},
            ),
            call(
                "https://cloud-prod.ploomber.io/jobs/someid/files",
                headers={"accept": "application/json", "api_key": "somekey"},
                stream=True,
            ),
        ]
    )
    assert (
        "WARNING: your previous resources configuration "
        "has been carried over: 0.5 CPU, 1 RAM, 0 GPU\n"
        "To change resources, run: 'ploomber-cloud resources --force'"
    ) in capsys.readouterr().out
