from unittest.mock import Mock

import pytest

from ploomber_cloud.api import PloomberCloudClient
from ploomber_cloud.exceptions import InternalServerErrorException


def test_handle_500_error(set_key):
    client = PloomberCloudClient()
    response = Mock(
        ok=False,
        status_code=500,
        json=Mock(
            side_effect=Exception("cannot parse JSON"),
        ),
    )

    with pytest.raises(InternalServerErrorException):
        client._process_response(response)
