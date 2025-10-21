import pytest
from httpx import AsyncClient

from app.core.exceptions import APIResponseError


async def test_link_cloud_account_to_org(
    test_data: dict,
    mock_optscale_cloud_account_api_post_method,
    optscale_cloud_account_api,
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    mock_optscale_cloud_account_api_post_method.return_value = mocked_response
    response = await optscale_cloud_account_api.link_cloud_account_with_org(
        conf=payload,
        user_access_token="good token",
        org_id="my_org_id",
    )
    assert response == mocked_response


async def test_link_cloud_account_to_org_exceptions(
    async_client: AsyncClient,
    test_data: dict,
    optscale_cloud_account_api,
    mock_optscale_cloud_account_api_post_method,
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_error_response = {
        "error": {
            "status_code": 400,
            "error_code": "OE0436",
            "reason": "boofoo type is not supported",
            "params": ["boofoo"],
        }
    }
    mock_optscale_cloud_account_api_post_method.return_value = mocked_error_response

    with pytest.raises(APIResponseError):
        await optscale_cloud_account_api.link_cloud_account_with_org(
            conf=payload, user_access_token="good token", org_id="my_org_id"
        )
