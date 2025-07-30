import json
from pathlib import Path

import pytest

from ploomber_cloud import abc
from ploomber_cloud.exceptions import InvalidPloomberConfigException


class KeyNotAllowed(Exception):
    pass


class ConfigFile(abc.PersistedMapping):
    PATH_TO_CONFIG = "config.json"

    def _validate_config(self):
        if "should-not-exist" in self._data:
            raise KeyNotAllowed

    def _dump(self, data_new):
        return json.dumps(data_new)

    def _load(self):
        return {}

    def _validate_path(self, path_to_config):
        if path_to_config == "not-allowed.json":
            raise RuntimeError("Path not allowed")


class AnotherConfig(ConfigFile):
    PATH_TO_CONFIG = "not-allowed.json"


def test_exists(tmp_empty):
    Path("config.json").touch()
    cfg = ConfigFile()
    assert cfg.exists()


def test_not_exists(tmp_empty):
    cfg = ConfigFile()
    assert not cfg.exists()


def test_set_item(tmp_empty):
    cfg = ConfigFile()
    cfg.load()
    cfg["key"] = "value"
    cfg["another"] = "value-another"

    assert json.loads(Path("config.json").read_text()) == {
        "key": "value",
        "another": "value-another",
    }


def test_dump(tmp_empty):
    cfg = ConfigFile()
    cfg.dump({"new-key": "new-value"})

    assert cfg._data == {"new-key": "new-value"}
    assert cfg.data == {"new-key": "new-value"}
    assert json.loads(Path("config.json").read_text()) == {"new-key": "new-value"}


def test_set_item_triggers_validation(tmp_empty):
    cfg = ConfigFile()

    cfg.load()

    with pytest.raises(KeyNotAllowed):
        cfg["should-not-exist"] = "value"


def test_delitem(tmp_empty):
    cfg = ConfigFile()
    cfg.load()
    cfg["key"] = "value"
    cfg["another"] = "value-another"

    del cfg["key"]

    assert cfg._data == {"another": "value-another"}
    assert cfg.data == {"another": "value-another"}
    assert json.loads(Path("config.json").read_text()) == {"another": "value-another"}


def test_delitem_missing_key(tmp_empty):
    cfg = ConfigFile()
    cfg.load()

    with pytest.raises(InvalidPloomberConfigException) as excinfo:
        del cfg["key"]

    assert "Key does not exist: key" in str(excinfo.value)


def test_validate_path(tmp_empty):
    with pytest.raises(RuntimeError) as excinfo:
        AnotherConfig()

    assert "Path not allowed" in str(excinfo.value)
