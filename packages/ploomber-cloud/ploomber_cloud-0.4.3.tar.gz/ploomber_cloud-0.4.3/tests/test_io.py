from unittest.mock import Mock

from ploomber_cloud import io


def test_prompt(monkeypatch, capsys):
    monkeypatch.setattr(io.click, "prompt", Mock(side_effect=["a", "2"]))

    def isdigit(value):
        if value.isdigit():
            return io.ValidationResult(
                is_valid=True,
                error_message=None,
                value_validated=value,
            )
        else:
            return io.ValidationResult(
                is_valid=False,
                error_message="must be a digit",
                value_validated=None,
            )

    value = io.prompt(isdigit, text="Enter a digit value")

    assert capsys.readouterr().out == "Invalid value: a (must be a digit)\n"
    assert value == "2"


def test_prompt_that_modifies_value(monkeypatch, capsys):
    monkeypatch.setattr(io.click, "prompt", Mock(side_effect=["a", "2"]))

    def isdigit(value):
        if value.isdigit():
            return io.ValidationResult(
                is_valid=True,
                error_message=None,
                # in this test, we cast the value to int
                value_validated=int(value),
            )
        else:
            return io.ValidationResult(
                is_valid=False,
                error_message="must be a digit",
                value_validated=None,
            )

    value = io.prompt(isdigit, text="Enter a digit value")

    assert capsys.readouterr().out == "Invalid value: a (must be a digit)\n"
    assert value == 2


def test_prompt_without_validator(monkeypatch, capsys):
    monkeypatch.setattr(io.click, "prompt", Mock(side_effect=["a"]))

    value = io.prompt(validator=None, text="Enter a digit value")

    assert value == "a"
