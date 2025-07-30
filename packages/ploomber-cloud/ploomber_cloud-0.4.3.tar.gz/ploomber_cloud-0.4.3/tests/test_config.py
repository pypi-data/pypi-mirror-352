import json
import pytest
from pathlib import Path

from ploomber_cloud.config import PloomberCloudConfig, ProjectEnv, path_to_config
from ploomber_cloud.exceptions import InvalidPloomberConfigException


def test_not_exists(tmp_empty):
    config = PloomberCloudConfig()
    assert config.exists() is False


def test_exists(tmp_empty):
    Path("ploomber-cloud.json").touch()
    config = PloomberCloudConfig()
    assert config.exists() is True


def test_load(tmp_empty):
    Path("ploomber-cloud.json").write_text('{"id": "foo", "type": "docker"}')
    config = PloomberCloudConfig()
    config.load()
    assert config.data == {"id": "foo", "type": "docker"}


def test_dump(tmp_empty):
    data = {"id": "foo", "type": "docker"}
    config = PloomberCloudConfig()
    config.dump(data)
    assert json.loads(Path("ploomber-cloud.json").read_text()) == data


def test_setitem(tmp_empty):
    Path("ploomber-cloud.json").write_text('{"id": "foo", "type": "docker"}')

    config = PloomberCloudConfig()
    config.load()
    config["resources"] = {"cpu": 0.5, "ram": 1, "gpu": 1}

    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "foo",
        "type": "docker",
        "resources": {"cpu": 0.5, "ram": 1, "gpu": 1},
    }


def test_delitem(tmp_empty):
    Path("ploomber-cloud.json").write_text(
        '{"id": "foo", "type": "docker", "labels": ["abc"]}'
    )
    config = PloomberCloudConfig()
    config.load()
    del config["labels"]
    assert json.loads(Path("ploomber-cloud.json").read_text()) == {
        "id": "foo",
        "type": "docker",
    }


def test_delitem_error(tmp_empty):
    Path("ploomber-cloud.json").write_text(
        '{"id": "foo", "type": "docker", "labels": ["abc"]}'
    )
    config = PloomberCloudConfig()
    config.load()

    with pytest.raises(InvalidPloomberConfigException) as excinfo:
        del config["missing"]

    assert "Key does not exist: missing" in str(excinfo.value)


def test_change_path_to_config(tmp_empty):
    Path("ploomber-cloud.json").write_text(json.dumps({"id": "foo", "type": "docker"}))
    Path("another.json").write_text(json.dumps({"id": "another", "type": "docker"}))

    with path_to_config("another.json"):
        config = PloomberCloudConfig()
        config.load()
        assert config.data == {"id": "another", "type": "docker"}

    config = PloomberCloudConfig()
    config.load()
    assert config.data == {"id": "foo", "type": "docker"}


def test_do_not_change_path_to_config_if_none(tmp_empty):
    Path("ploomber-cloud.json").write_text(json.dumps({"id": "foo", "type": "docker"}))
    Path("another.json").write_text(json.dumps({"id": "another", "type": "docker"}))

    with path_to_config(None):
        config = PloomberCloudConfig()
        config.load()
        assert config.data == {"id": "foo", "type": "docker"}


def test_error_if_missing_json_extension(tmp_empty):
    Path("ploomber-cloud").touch()

    class CustomConfig(PloomberCloudConfig):
        PATH_TO_CONFIG = "ploomber-cloud"

    with pytest.raises(InvalidPloomberConfigException) as excinfo:
        CustomConfig()

    assert "Invalid config file name: ploomber-cloud. Must have .json extension" in str(
        excinfo.value
    )


def test_env_dump(tmp_empty):
    env = ProjectEnv()
    env.load()

    env["API_KEY"] = "123"
    env["SECRET"] = "456"

    assert Path(".env").read_text() == "API_KEY=123\nSECRET=456"


def test_load_existing_file(tmp_empty):
    Path(".env").write_text("API_KEY=123\nSECRET=456")

    env = ProjectEnv()
    env.load()

    assert env.data == {"API_KEY": "123", "SECRET": "456"}
