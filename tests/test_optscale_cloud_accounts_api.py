import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI


@pytest.fixture
def optscale_cloud_account_api_instance():
    return OptScaleCloudAccountAPI()


@pytest.fixture
def mock_api_client_post(mocker, optscale_cloud_account_api_instance):
    mock_post = mocker.patch.object(
        optscale_cloud_account_api_instance.api_client, "post", new=AsyncMock()
    )
    return mock_post


async def test_create_cloud_account(
    optscale_cloud_account_api_instance,
    mock_api_client_post,
    test_data: dict,
):
    mock_api_client_post.return_value = test_data["cloud_accounts_conf"]["create"][
        "data"
    ]["azure"]["response"]  # noqa: E501
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    response = (
        await optscale_cloud_account_api_instance.create_cloud_account_datasource(
            user_access_token="good token", org_id="ABC-101-DEF-1001", conf=payload
        )
    )

    got = response
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"

    # Assert that mock_post was called with expected arguments
    mock_api_client_post.assert_called_once_with(
        endpoint="/restapi/v2/organizations/ABC-101-DEF-1001/cloud_accounts",
        data=payload,
        headers={"Authorization": "Bearer good token"},
    )


async def test_account_already_exists(
    optscale_cloud_account_api_instance, mock_api_client_post, test_data: dict, caplog
):
    mock_api_client_post.return_value = {
        "error": {
            "status_code": 409,
            "error_code": "OE0402",
            "reason": "Cloud account for this account already exist",
            "params": [],
        }
    }
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(OptScaleAPIResponseError):
            await optscale_cloud_account_api_instance.create_cloud_account_datasource(
                user_access_token="good token", org_id="ABC-101-DEF-1001", conf=payload
            )
