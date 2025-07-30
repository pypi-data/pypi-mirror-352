import json
from pathlib import Path
import os
import sys
from unittest.mock import Mock

from ploomber_cloud.models import UserTiers
from ploomber_cloud.cli import cli
from ploomber_cloud import templates, api
from ploomber_cloud.cli import templates_ as cli_templates
from ploomber_cloud.config import PloomberCloudConfig

import pytest

CMD_NAME = "ploomber-cloud"


def test_templates_custom_config(monkeypatch, tmp_empty, set_key):
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "templates", "sometemplate", "--config", "someconfig.json"],
    )

    Path("someconfig.json").write_text(json.dumps({"id": "someid", "type": "docker"}))

    class CLIFunction:
        def __call__(self, name):
            cfg = PloomberCloudConfig()
            cfg.load()
            self.config = cfg._data

    cli_function = CLIFunction()
    monkeypatch.setattr(cli_templates, "template", cli_function)

    with pytest.raises(SystemExit):
        cli()

    assert cli_function.config == {"id": "someid", "type": "docker"}


def test_templates_vllm(monkeypatch, tmp_empty, set_key):
    Path("vllm").mkdir()
    os.chdir("vllm")

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "vllm"])
    monkeypatch.setattr(
        templates.click, "prompt", Mock(side_effect=["facebook/opt-125m"])
    )
    monkeypatch.setattr(templates.click, "confirm", Mock(side_effect=["y"]))

    mock_get_user_type = Mock(return_value=UserTiers.TEAMS)
    monkeypatch.setattr("ploomber_cloud.deploy.get_user_type", mock_get_user_type)

    mock_requests_post = Mock(name="requests.post")
    mock_requests_post.side_effect = [
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "id": "someid",
                    "type": "docker",
                }
            ),
        ),
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "project_id": "projectid",
                    "id": "jobid",
                }
            ),
        ),
    ]

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert Path("Dockerfile").exists()
    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "someid",
        "type": "docker",
        "resources": {"cpu": 4.0, "ram": 12, "gpu": 1},
    }
    assert Path("requirements.txt").exists()
    assert Path("test-vllm.py").exists()


def test_templates_vllm_gated_model(monkeypatch, tmp_empty, set_key):
    Path("vllm").mkdir()
    os.chdir("vllm")

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "vllm"])
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(
            side_effect=[
                "google/gemma-2b-it",
                "fake-ht-token",
            ]
        ),
    )
    monkeypatch.setattr(templates.click, "confirm", Mock(side_effect=["y"]))

    mock_get_user_type = Mock(return_value=UserTiers.TEAMS)
    monkeypatch.setattr("ploomber_cloud.deploy.get_user_type", mock_get_user_type)

    mock_requests_get = Mock(name="requests.get")
    mock_requests_get.side_effect = [
        # call to: validate_model_name (simulate a gated model)
        Mock(
            ok=False,
            json=Mock(
                return_value={
                    "error": "model is gated!",
                }
            ),
        ),
        # call to: has_access_to_model (simulate hf token has access)
        Mock(ok=True),
        # call to: ploomber-api to fetch the previously use secret
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "secrets": [],
                }
            ),
        ),
    ]

    mock_requests_post = Mock(name="requests.post")
    mock_requests_post.side_effect = [
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "id": "someid",
                    "type": "docker",
                }
            ),
        ),
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "project_id": "projectid",
                    "id": "jobid",
                }
            ),
        ),
    ]

    monkeypatch.setattr(api.requests, "post", mock_requests_post)
    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert Path("Dockerfile").exists()
    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "someid",
        "type": "docker",
        "resources": {"cpu": 4.0, "ram": 12, "gpu": 1},
    }
    assert Path("requirements.txt").exists()
    assert Path("test-vllm.py").exists()


def test_templates_auth0_not_initialized_error(monkeypatch, tmp_empty, set_key, capsys):
    Path("auth0").mkdir()
    os.chdir("auth0")

    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "auth0"])
    monkeypatch.setattr(templates.click, "confirm", Mock(side_effect=[False]))

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert (
        "This command requires a ploomber-cloud.json file.\n"
        "Run 'ploomber-cloud init' to initialize your project."
    ) in capsys.readouterr().err


@pytest.mark.parametrize(
    "base_url_entered, base_url_env",
    [
        ["https://some-url", "https://some-url"],
        ["some-url.auth0.com", "https://some-url.auth0.com"],
    ],
)
def test_templates_auth0_not_initialized(
    monkeypatch, tmp_empty, set_key, base_url_entered, base_url_env
):
    Path("auth0").mkdir()
    os.chdir("auth0")

    monkeypatch.setattr(templates.secrets, "token_urlsafe", lambda: "some-secret")
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "auth0"])
    monkeypatch.setattr(templates.click, "confirm", Mock(side_effect=["y"]))
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(
            side_effect=[
                "docker",
                "some-client-id",
                "some-client-secret",
                base_url_entered,
            ]
        ),
    )
    mock_requests_post = Mock(name="requests.post")

    mock_requests_post.side_effect = [
        Mock(
            ok=True,
            json=Mock(
                return_value={
                    "id": "some-id",
                    "type": "docker",
                }
            ),
        ),
    ]

    monkeypatch.setattr(api.requests, "post", mock_requests_post)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0
    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "some-id",
        "type": "docker",
        "template": "node-auth0",
    }

    with open(".env", "r") as env_file:
        lines = env_file.readlines()
        assert lines == [
            "AUTH_CLIENT_ID=some-client-id\n",
            "AUTH_CLIENT_SECRET=some-client-secret\n",
            f"AUTH_ISSUER_BASE_URL={base_url_env}\n",
            "AUTH_SECRET=some-secret",
        ]


def test_templates_auth0_initialized(monkeypatch, tmp_empty, set_key, capsys):
    Path("auth0").mkdir()
    os.chdir("auth0")

    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text(
        json.dumps(
            {
                "id": "some-id",
                "type": "docker",
            }
        )
    )

    Path(".env").touch()
    Path(".env").write_text("KEY1=VAL1\nKEY2=VAL2")

    monkeypatch.setattr(templates.secrets, "token_urlsafe", lambda: "some-secret")
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "auth0"])
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(
            side_effect=[
                "some-client-id",
                "some-client-secret",
                "https://some-url",
            ]
        ),
    )

    with pytest.raises(SystemExit) as excinfo:
        cli()

    env_file_msg = (
        "Your Auth0 credentials have been stored in your `.env` file. "
        "To update them, edit the values in `.env`."
    )

    instructions_msg = (
        "\n"
        "Before deploying, you must update your Auth0 project "
        "configurations to match your application URL. "
        "For detailed instructions, see here:\n"
        "https://docs.cloud.ploomber.io/en/latest/user-guide/password.html"
        "#set-callback-and-status-urls\n"
    )

    out = capsys.readouterr().out

    assert excinfo.value.code == 0
    assert ("Successfully configured Auth0.") in out
    assert env_file_msg in out
    assert instructions_msg in out

    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "some-id",
        "type": "docker",
        "template": "node-auth0",
    }

    with open(".env", "r") as env_file:
        lines = env_file.readlines()
        assert lines == [
            "KEY1=VAL1\n",
            "KEY2=VAL2\n",
            "AUTH_CLIENT_ID=some-client-id\n",
            "AUTH_CLIENT_SECRET=some-client-secret\n",
            "AUTH_ISSUER_BASE_URL=https://some-url\n",
            "AUTH_SECRET=some-secret",
        ]


@pytest.mark.parametrize(
    "defined_credentials, env_text, new_credential_vals",
    [
        (
            [],
            (""),
            [
                "some-client-id",
                "some-client-secret",
                "https://some-url",
            ],
        ),
        (
            [
                "AUTH_CLIENT_ID",
            ],
            ("AUTH_CLIENT_ID=some-client-id\n"),
            [
                "some-client-secret",
                "https://some-url",
            ],
        ),
        (
            [
                "AUTH_CLIENT_SECRET",
            ],
            ("AUTH_CLIENT_SECRET=some-client-secret\n"),
            [
                "some-client-id",
                "https://some-url",
            ],
        ),
        (
            [
                "AUTH_ISSUER_BASE_URL",
            ],
            ("AUTH_ISSUER_BASE_URL=https://some-url\n"),
            [
                "some-client-id",
                "some-client-secret",
            ],
        ),
        (
            [
                "AUTH_CLIENT_ID",
                "AUTH_CLIENT_SECRET",
            ],
            (
                "AUTH_CLIENT_ID=some-client-id\n"
                "AUTH_CLIENT_SECRET=some-client-secret\n"
            ),
            [
                "https://some-url",
            ],
        ),
        (
            [
                "AUTH_CLIENT_ID",
                "AUTH_CLIENT_SECRET",
                "AUTH_ISSUER_BASE_URL",
            ],
            (
                "AUTH_CLIENT_ID=some-client-id\n"
                "AUTH_CLIENT_SECRET=some-client-secret\n"
                "AUTH_ISSUER_BASE_URL=https://some-url\n"
            ),
            [],
        ),
    ],
    ids=[
        "defined-none",
        "defined-id",
        "defined-secret",
        "defined-url",
        "defined-2",
        "defined-all",
    ],
)
def test_templates_auth0_credentials_prompting(
    monkeypatch,
    tmp_empty,
    set_key,
    capsys,
    defined_credentials,
    env_text,
    new_credential_vals,
):
    Path("auth0").mkdir()
    os.chdir("auth0")

    Path("ploomber-cloud.json").touch()
    Path("ploomber-cloud.json").write_text(
        json.dumps(
            {
                "id": "some-id",
                "type": "docker",
            }
        )
    )

    Path(".env").touch()
    Path(".env").write_text(env_text)

    monkeypatch.setattr(templates.secrets, "token_urlsafe", lambda: "some-secret")
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "templates", "auth0"])
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(side_effect=new_credential_vals),
    )

    with pytest.raises(SystemExit):
        cli()

    # assert capsys doesn't contain certain prompts
    for c in defined_credentials:
        assert f"Enter the value for {c}" not in capsys.readouterr().out

    with open(".env", "r") as env_file:
        lines = [line.strip() for line in env_file.readlines()]
        assert set(lines) == {
            "AUTH_CLIENT_ID=some-client-id",
            "AUTH_CLIENT_SECRET=some-client-secret",
            "AUTH_ISSUER_BASE_URL=https://some-url",
            "AUTH_SECRET=some-secret",
        }
