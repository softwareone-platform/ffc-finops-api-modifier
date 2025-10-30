import logging

import pytest

from app.core.exceptions import APIResponseError


async def test_create_cloud_account(
    optscale_cloud_account_api,
    mock_optscale_cloud_account_api_post_method,
    test_data: dict,
):
    mock_optscale_cloud_account_api_post_method.return_value = (test_data)[
        "cloud_accounts_conf"
    ]["create"]["data"]["azure"]["response"]
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    response = await optscale_cloud_account_api.link_cloud_account_with_org(
        user_access_token="good token", org_id="ABC-101-DEF-1001", conf=payload
    )

    got = response
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"

    # Assert that mock_post was called with expected arguments
    mock_optscale_cloud_account_api_post_method.assert_called_once_with(
        endpoint="/organizations/ABC-101-DEF-1001/cloud_accounts",
        data=payload,
        headers={"Authorization": "Bearer good token"},
    )


async def test_account_already_exists(
    optscale_cloud_account_api,
    mock_optscale_cloud_account_api_post_method,
    test_data: dict,
    caplog,
):
    mock_optscale_cloud_account_api_post_method.return_value = {
        "error": {
            "status_code": 409,
            "error_code": "OE0402",
            "reason": "Cloud account for this account already exist",
            "params": [],
        }
    }
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(APIResponseError):
            await optscale_cloud_account_api.link_cloud_account_with_org(
                user_access_token="good token", org_id="ABC-101-DEF-1001", conf=payload
            )
