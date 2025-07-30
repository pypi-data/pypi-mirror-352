from ploomber_cloud import api_key


def test_read_api_key_from_file(set_key):
    assert api_key.get() == "somekey"


def test_read_api_key_from_env_var(set_key, monkeypatch):
    monkeypatch.setenv("PLOOMBER_CLOUD_KEY", "keyfromenv")

    assert api_key.get() == "keyfromenv"
