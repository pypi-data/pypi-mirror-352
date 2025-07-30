from unittest.mock import Mock
import pytest
from ploomber_cloud import exceptions
from ploomber_cloud import util
from ploomber_cloud.util import (
    requires_permission,
    requires_init,
    get_max_allowed_app_size_for_user_type,
)
from ploomber_cloud.models import UserTiers
import ploomber_cloud.resources


#######################################
# Test requires_permission() function #
#######################################


@pytest.mark.parametrize(
    "permissions, allowed_features, should_pass",
    [
        ("read", ["read"], True),
        ("write", ["read"], False),
        (["read", "write"], ["read", "write"], True),
        (["read", "write"], ["read"], False),
        (["read"], ["read", "write"], True),
        ([], ["read", "write"], True),
        ("any_permission", [], False),
    ],
)
def test_requires_permission(
    monkeypatch, set_permissions, permissions, allowed_features, should_pass
):
    set_permissions(allowed_features)

    @requires_permission(permissions)
    def test_func():
        return "Function executed"

    if should_pass:
        assert (
            test_func() == "Function executed"
        ), f"The permission wrapper should not block the execution \
        for permissions: {permissions}"
    else:
        with pytest.raises(exceptions.UserTierForbiddenException):
            test_func()


def test_requires_permission_empty_string(monkeypatch, set_permissions):
    set_permissions(["read", "write"])

    @requires_permission("")
    def test_func():
        return "Function executed"

    assert (
        test_func() == "Function executed"
    ), "The permission wrapper should not block the execution \
    when an empty string is passed"


def test_requires_permission_empty_list(monkeypatch, set_permissions):
    set_permissions(["read", "write"])

    @requires_permission([])
    def test_func():
        return "Function executed"

    assert (
        test_func() == "Function executed"
    ), "The permission wrapper should not block the execution when None is passed"


#################################
# Test requires_init() function #
#################################


# Mock function to be decorated
def mock_function():
    return "Function executed"


# Test when ploomber-cloud.json exists
def test_requires_init_file_exists(tmp_path, monkeypatch):
    # Create a mock ploomber-cloud.json file
    mock_file = tmp_path / "ploomber-cloud.json"
    mock_file.touch()

    # Patch the current working directory
    monkeypatch.chdir(tmp_path)

    @requires_init
    def test_func():
        return mock_function()

    assert test_func() == "Function executed"


def test_requires_init_file_not_exists_user_confirms(tmp_path, monkeypatch):
    monkeypatch.setattr(util.click, "confirm", Mock(side_effect=["y"]))
    monkeypatch.setattr("ploomber_cloud.init.init", lambda **kwargs: None)

    @requires_init
    def test_func():
        return mock_function()

    assert test_func() == "Function executed"


# Test when ploomber-cloud.json doesn't exist and user declines initialization
def test_requires_init_file_not_exists_user_declines(tmp_path, monkeypatch):
    monkeypatch.setattr(util.click, "confirm", Mock(side_effect=[False]))

    @requires_init
    def test_func():
        return mock_function()

    with pytest.raises(exceptions.BasePloomberCloudException) as excinfo:
        test_func()

    assert "This command requires a ploomber-cloud.json file" in str(excinfo.value)


# Test that the wrapper preserves the original function's metadata
def test_requires_init_preserves_metadata():
    @requires_init
    def test_func():
        """Test function docstring"""
        pass

    assert test_func.__name__ == "test_func"
    assert test_func.__doc__ == "Test function docstring"


# Test that the wrapper works with functions that take arguments
def test_requires_init_with_arguments(tmp_path, monkeypatch):
    mock_file = tmp_path / "ploomber-cloud.json"
    mock_file.touch()
    monkeypatch.chdir(tmp_path)

    @requires_init
    def test_func_with_args(arg1, arg2, kwarg1=None):
        return f"{arg1}, {arg2}, {kwarg1}"

    assert test_func_with_args("a", "b", kwarg1="c") == "a, b, c"


# Test that the init function is called with correct parameters
def test_requires_init_calls_init_correctly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(util.click, "confirm", Mock(side_effect=[True]))

    init_called_with = {}

    def mock_init(**kwargs):
        init_called_with.update(kwargs)

    monkeypatch.setattr("ploomber_cloud.init.init", mock_init)

    @requires_init
    def test_func():
        return mock_function()

    test_func()

    assert init_called_with == {
        "from_existing": False,
        "force": False,
        "verbose": False,
    }


def test_get_max_allowed_app_size_for_user_type(monkeypatch):
    # Mock the _get_resource_config_for_user_type function
    def mock_get_resource_config_for_user_type(user_type):
        return {"maxAppSizeMB": 500}

    monkeypatch.setattr(
        ploomber_cloud.resources,
        "_get_resource_config_for_user_type",
        mock_get_resource_config_for_user_type,
    )

    max_size = get_max_allowed_app_size_for_user_type(UserTiers.COMMUNITY)
    assert max_size == 500
