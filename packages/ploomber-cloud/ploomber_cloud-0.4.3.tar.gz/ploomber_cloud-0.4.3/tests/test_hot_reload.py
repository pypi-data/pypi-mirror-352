import os
from unittest.mock import Mock
import subprocess
import click

from ploomber_cloud.file_watcher import (
    start_watcher,
    ChangeHandler,
    EXCLUDED_FILES,
)


def test_start_watcher_default_path(monkeypatch):
    mock_observer = Mock()
    monkeypatch.setattr(
        "ploomber_cloud.file_watcher.Observer", Mock(return_value=mock_observer)
    )

    observer = start_watcher()

    assert observer == mock_observer
    mock_observer.schedule.assert_called_once()

    # Check that the path is the current working directory
    schedule_args = mock_observer.schedule.call_args[0]
    assert schedule_args[1] == os.getcwd()


def test_start_watcher_custom_path(monkeypatch, tmp_path):
    mock_observer = Mock()
    monkeypatch.setattr(
        "ploomber_cloud.file_watcher.Observer", Mock(return_value=mock_observer)
    )

    custom_path = str(tmp_path)
    observer = start_watcher(path=custom_path)

    assert observer == mock_observer
    mock_observer.schedule.assert_called_once()

    # Check that the path is the custom path
    schedule_args = mock_observer.schedule.call_args[0]
    assert schedule_args[1] == custom_path


def test_change_handler_excluded_files(monkeypatch):
    handler = ChangeHandler()

    mock_subprocess = Mock()
    monkeypatch.setattr("subprocess.run", mock_subprocess)

    for filename in EXCLUDED_FILES:
        event = Mock()
        event.is_directory = False
        event.src_path = str(filename)

        handler.on_modified(event)
        mock_subprocess.assert_not_called()
        mock_subprocess.reset_mock()


def test_change_handler_excluded_zip_pattern(monkeypatch):
    handler = ChangeHandler()

    mock_subprocess = Mock()
    monkeypatch.setattr("subprocess.run", mock_subprocess)

    test_patterns = ["app-job-id.zip", "app-123.zip", "app-job123.zip"]

    for pattern in test_patterns:
        mock_subprocess.reset_mock()
        event = Mock()
        event.is_directory = False
        event.src_path = str(pattern)

        handler.on_modified(event)
        mock_subprocess.assert_not_called()


def test_change_handler_deployment_triggered(monkeypatch, tmp_path):
    handler = ChangeHandler()

    mock_subprocess = Mock()
    monkeypatch.setattr("subprocess.run", mock_subprocess)

    event = Mock()
    event.is_directory = False
    event.src_path = str(tmp_path / "test_file.py")

    handler.on_modified(event)
    mock_subprocess.assert_called_once_with(["pc", "deploy"], check=True)


def test_change_handler_directory_changes_ignored(monkeypatch, tmp_path):
    handler = ChangeHandler()

    mock_subprocess = Mock()
    monkeypatch.setattr("subprocess.run", mock_subprocess)

    event = Mock()
    event.is_directory = True
    event.src_path = str(tmp_path / "some_directory")

    handler.on_modified(event)
    mock_subprocess.assert_not_called()


def test_change_handler_subprocess_error_handling(monkeypatch, tmp_path, capsys):
    handler = ChangeHandler()

    # Simulate a subprocess error
    err_message = "pc deploy failed with some error"

    def mock_run(*args, **kwargs):
        click.echo(err_message)
        raise subprocess.CalledProcessError(1, ["pc", "deploy"])

    monkeypatch.setattr(subprocess, "run", mock_run)

    event = Mock()
    event.is_directory = False
    event.src_path = str(tmp_path / "test_file.py")

    handler.on_modified(event)

    # Capture printed output
    captured = capsys.readouterr()

    assert "test_file.py modified." in captured.out
    assert err_message in captured.out
