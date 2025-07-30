from ploomber_cloud import api, init, templates
from ploomber_cloud.auth import (
    _make_authentication_field_for_config,
    _make_authentication_field_for_secret,
)
from ploomber_cloud.cli import cli
from ploomber_cloud.config import PloomberCloudConfig, ProjectEnv
from ploomber_cloud.exceptions import (
    ONLY_ADD_OR_REMOVE,
    MUST_HAVE_ADD_OR_REMOVE,
    OVERWRITE_ONLY_WHEN_ADDING,
)
from ploomber_cloud.messages import FEATURE_PROMPT_MSG, no_authentication_error_msg
from ploomber_cloud.models import AuthCompatibleFeatures


import pytest


import json
import sys
from pathlib import Path
from unittest.mock import Mock

from ploomber_cloud.util import camel_case_to_human_readable


CMD_NAME = "ploomber-cloud"

# for the tests to run, we need to set some default permissions
DEFAULT_PERMISSIONS = ["authentication", "viewAnalyticsReport"]


@pytest.mark.parametrize("username", ["username"])
@pytest.mark.parametrize("password", ["password"])
@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
def test_nginx_auth(
    monkeypatch, username, password, for_feature, tmp_empty, set_key, set_permissions
):
    # handle project init
    set_permissions(DEFAULT_PERMISSIONS)
    monkeypatch.setattr(templates.secrets, "token_urlsafe", lambda: "some-secret")
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--add", f"--feature={for_feature.value}"],
    )
    monkeypatch.setattr(templates.click, "confirm", Mock(side_effect=["y"]))
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(
            side_effect=[
                "docker",
                username,
                password,
            ]
        ),
    )

    # handle requests calls
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

    # run
    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 0

    auth_field = _make_authentication_field_for_config(for_feature)
    pc_json_obj = json.loads(Path("ploomber-cloud.json").read_text())

    # Temporary: define conditions for valid auth here:
    def is_not_empty(val):
        return bool(val)

    conditions_username = [is_not_empty]

    conditions_password = [is_not_empty]

    # expect to pass:
    if all([condition(username) for condition in conditions_username]) and all(
        [condition(password) for condition in conditions_password]
    ):
        assert {"username": username, "password": password} == pc_json_obj[auth_field]

        user_field, pass_field = _make_authentication_field_for_secret(for_feature)

        with open(".env", "r") as env_file:
            lines = env_file.readlines()
            assert lines == [
                f"{user_field}={username}\n",
                f"{pass_field}={password}",
            ]
    else:
        pass  # for now, cannot fail


def create_random_project(monkeypatch):
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init"])
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(
            side_effect=[
                "docker",
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
    with pytest.raises(SystemExit):
        cli()


def add_auth_to_project(monkeypatch, for_feature):
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--add", f"--feature={for_feature.value}"],
    )
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(side_effect=["some_username", "some_password"]),
    )
    with pytest.raises(SystemExit):
        cli()


@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
def test_rm_nginx_auth(monkeypatch, for_feature, tmp_empty, set_key, set_permissions):
    # Setup
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)
    add_auth_to_project(monkeypatch, for_feature)
    config_field = _make_authentication_field_for_config(for_feature)

    # Get current config (soon to be old when we load the new one)
    # Check if config field is removed
    old_config = PloomberCloudConfig()
    old_config.load()
    old_data = old_config.get_data()

    # Run
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--remove", f"--feature={for_feature.value}"],
    )
    with pytest.raises(SystemExit) as excinfo:
        cli()

    # Assert
    assert excinfo.value.code == 0

    # Check if config field is removed
    config = PloomberCloudConfig()
    config.load()
    with pytest.raises(KeyError):
        assert config.data[config_field]

    # Check if the content of the config is as expected
    del old_data[config_field]
    new_data = config.get_data()
    assert json.dumps(old_data, sort_keys=True) == json.dumps(new_data, sort_keys=True)

    # Check if .env file is updated
    env = ProjectEnv()
    env.load()
    username, password = _make_authentication_field_for_secret(for_feature)
    assert username not in env.data
    assert password not in env.data


@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
def test_rm_nginx_auth_no_auth_configured(
    monkeypatch, for_feature, tmp_empty, set_key, capsys, set_permissions
):
    # Setup
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)

    # Remove auth
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--remove", f"--feature={for_feature.value}"],
    )
    with pytest.raises(SystemExit) as excinfo:
        cli()

    # Make sure it fails
    assert excinfo.value.code != 0
    assert no_authentication_error_msg(for_feature) in capsys.readouterr().err


@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
def test_keep_auth_when_reinit(
    monkeypatch, for_feature, tmp_empty, set_key, set_permissions
):
    # Setup
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)
    add_auth_to_project(monkeypatch, for_feature)

    # Run re-init command
    monkeypatch.setattr(sys, "argv", [CMD_NAME, "init", "--force"])
    monkeypatch.setattr(init.click, "prompt", Mock(side_effect=["docker"]))
    mock_requests_post = Mock(name="requests.post")

    def requests_post(*args, **kwargs):
        return Mock(ok=True, json=Mock(return_value={"id": "some-other-id"}))

    mock_requests_post.side_effect = requests_post
    monkeypatch.setattr(api.requests, "post", mock_requests_post)
    with pytest.raises(SystemExit):
        cli()

    # Assert auth fields kept after reinit
    auth_field = _make_authentication_field_for_config(for_feature)
    config_data = json.loads(Path("ploomber-cloud.json").read_text())
    assert config_data[auth_field]["username"] == "some_username"
    assert config_data[auth_field]["password"] == "some_password"


@pytest.mark.parametrize(
    "params, expected_error_message",
    [
        (["--add", "--remove"], ONLY_ADD_OR_REMOVE),
        ([], MUST_HAVE_ADD_OR_REMOVE),
        (["--remove", "--overwrite"], OVERWRITE_ONLY_WHEN_ADDING),
    ],
)
def test_invalid_params(
    monkeypatch,
    tmp_empty,
    set_key,
    capsys,
    params,
    expected_error_message,
    set_permissions,
):
    """
    This test will ensure if an invalid combination of parameters is passed, they
    will fail
    """
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", *params],
    )
    with pytest.raises(SystemExit) as excinfo:
        cli()
    assert excinfo.value.code != 0  # Ensure it fails
    assert (
        expected_error_message
    ) in capsys.readouterr().err, "Ensure the correct error message is thrown"


@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
def test_overwrite_auth(monkeypatch, for_feature, tmp_empty, set_key, set_permissions):
    # Setup
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)
    add_auth_to_project(monkeypatch, for_feature)

    # Run
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--add", f"--feature={for_feature.value}", "--overwrite"],
    )
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(side_effect=["some_other_username", "some_other_password"]),
    )
    with pytest.raises(SystemExit):
        cli()

    # Assert changes to the config were made
    config_data = json.loads(Path("ploomber-cloud.json").read_text())
    auth_field = _make_authentication_field_for_config(for_feature)
    assert (
        config_data[auth_field]["username"] == "some_other_username"
    ), "The username should have been overwritten"
    assert (
        config_data[auth_field]["password"] == "some_other_password"
    ), "The password should have been overwritten"


def test_prompt_for_feature(monkeypatch, tmp_empty, set_key, capsys, set_permissions):
    # Setup
    set_permissions(DEFAULT_PERMISSIONS)
    create_random_project(monkeypatch)

    # Run the command
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", "--add"],
    )
    monkeypatch.setattr(
        templates.click,
        "prompt",
        Mock(side_effect=["analytics"]),
    )
    with pytest.raises(StopIteration):
        cli()
    out = capsys.readouterr().out
    print(out)

    # Perform necessary checks
    assert FEATURE_PROMPT_MSG in out


@pytest.mark.parametrize("for_feature", list(AuthCompatibleFeatures))
@pytest.mark.parametrize("add_or_remove", ["--add", "--remove"])
def test_auth_command_fails_without_required_permissions(
    monkeypatch, for_feature, add_or_remove, tmp_empty, set_key, capsys, set_permissions
):
    """
    Test that the 'auth' command fails when the required permissions for the
    selected feature are not present.
    """
    required_permissions = AuthCompatibleFeatures.get_required_permissions_for_feature(
        feature=for_feature
    )
    if not required_permissions:
        # Skip if no permissions are required for the selected feature
        return

    # We set only authentication permission here, since we need to at least run auth
    set_permissions(["authentication"])

    # Create a random project
    create_random_project(monkeypatch)

    # Prompts
    monkeypatch.setattr(
        sys,
        "argv",
        [CMD_NAME, "auth", add_or_remove, f"--feature={for_feature.value}"],
    )
    if add_or_remove == "--add":
        monkeypatch.setattr(
            templates.click,
            "prompt",
            Mock(side_effect=["some_username", "some_password"]),
        )

    # Run the command and expect it to fail
    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code != 0
    captured = capsys.readouterr()
    err = captured.err

    missing_permissions = set(required_permissions) - {"authentication"}

    # Check that the error message mentions the missing permissions
    for permission in missing_permissions:
        assert (
            camel_case_to_human_readable(permission) in err
        ), f"Missing permission '{permission}' should be in error message"
