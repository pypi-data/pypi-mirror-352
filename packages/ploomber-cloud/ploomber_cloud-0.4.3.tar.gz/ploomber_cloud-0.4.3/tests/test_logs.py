import sys
import pytest
from unittest.mock import Mock

from ploomber_cloud.cli import cli
from ploomber_cloud import api

CMD_NAME = "ploomber-cloud"


@pytest.mark.parametrize(
    "id_args, mock_project_call",
    [
        (
            ["--job-id", "some-job"],
            False,
        ),
        (
            ["--project-id", "some-proj"],
            True,
        ),
        (["--project-id", "some-proj", "--job-id", "some-job"], False),
    ],
    ids=["job-id", "proj-id", "both-id"],
)
@pytest.mark.parametrize(
    "type_args, expected_logs",
    [
        (
            [],
            [
                "Showing build-docker logs:",
                "These are docker logs",
                "Showing app logs:",
                "These are app logs",
            ],
        ),
        (
            ["--type", "docker"],
            [
                "Showing build-docker logs:",
                "These are docker logs",
            ],
        ),
        (
            ["--type", "web"],
            [
                "Showing app logs:",
                "These are app logs",
            ],
        ),
    ],
    ids=["both-type", "docker", "web"],
)
def test_logs(
    monkeypatch, set_key, capsys, id_args, mock_project_call, type_args, expected_logs
):
    args = [CMD_NAME, "logs"]
    args.extend(id_args)
    args.extend(type_args)

    monkeypatch.setattr(sys, "argv", args)

    # Mock job logs
    job_logs_mock = Mock(
        ok=True,
        json=Mock(
            return_value={
                "logs": {
                    "build-docker": "These are docker logs",
                    "app": "These are app logs",
                }
            }
        ),
    )
    # Mock project call in case user only provides project-id
    project_response_mock = Mock(
        ok=True,
        json=Mock(
            return_value={
                "id": "someid",
                "type": "docker",
                "jobs": [{"id": "some-job"}],
            }
        ),
    )

    if mock_project_call:
        mock_requests_get = Mock(
            name="requests.get",
            side_effect=[
                project_response_mock,
                job_logs_mock,
            ],
        )
    else:
        mock_requests_get = Mock(
            name="requests.get",
            side_effect=[job_logs_mock],
        )

    monkeypatch.setattr(api.requests, "get", mock_requests_get)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    out = capsys.readouterr().out

    assert excinfo.value.code == 0
    for line in expected_logs:
        assert line in out


@pytest.mark.parametrize(
    "args, error",
    [
        ([CMD_NAME, "logs"], "You must specify a job-id or project-id."),
        (
            [CMD_NAME, "logs", "--job-id", "wrongid"],
            "Couldn't find job with ID: wrongid",
        ),
        (
            [CMD_NAME, "logs", "--project-id", "wrongid"],
            "Couldn't find project with ID: wrongid or project has no jobs",
        ),
        (
            [CMD_NAME, "logs", "--type", "wrongtype"],
            "You must specify a job-id or project-id.",
        ),
        (
            [CMD_NAME, "logs", "--job-id", "someid", "--type", "wrongtype"],
            "Invalid logs type. Available options: 'docker' or 'webservice'",
        ),
    ],
    ids=[
        "missing-id",
        "wrong-job-id",
        "wrong-proj-id",
        "missing-id-and-wrong-type",
        "wrong-type",
    ],
)
def test_logs_errors(monkeypatch, set_key, capsys, args, error):
    monkeypatch.setattr(sys, "argv", args)

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1
    assert error in capsys.readouterr().err
