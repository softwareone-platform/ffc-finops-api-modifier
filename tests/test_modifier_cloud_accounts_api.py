import logging

import pytest
from httpx import AsyncClient

from app.core.exceptions import APIResponseError, CloudAccountNotAllowed


async def test_link_cloud_account(
    async_client: AsyncClient,
    test_data: dict,
    mock_optscale_post_link_cloud_account_with_org,
    mock_auth_post_create_cloud_account,
):
    mock_response = test_data["auth_token"]["authorize"]["valid_response"]
    mock_auth_post_create_cloud_account.return_value = mock_response
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    mock_optscale_post_link_cloud_account_with_org.return_value = mocked_response

    response = await async_client.post(
        "/organizations/my_org_id/cloud_accounts",
        json=payload,
        headers={"Authorization": "Bearer good token"},
    )
    assert response.status_code == 201
    got = response.json()
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"


async def test_create_datasource_with_inject_conf(
    async_client: AsyncClient,
    test_data: dict,
    mock_optscale_post_link_cloud_account_with_org,
    mock_auth_post_create_cloud_account,
):
    mock_response = test_data["auth_token"]["authorize"]["valid_response"]
    mock_auth_post_create_cloud_account.return_value = mock_response
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    mock_optscale_post_link_cloud_account_with_org.return_value = mocked_response

    response = await async_client.post(
        "/organizations/my_org_id/cloud_accounts",
        json=payload,
        headers={"Authorization": "Bearer good token"},
    )
    assert response.status_code == 201
    got = response.json()
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"


async def test_not_allowed_datasource_exception_handling(
    async_client: AsyncClient,
    test_data: dict,
    caplog,
    mock_auth_post_create_cloud_account,
):
    mock_response = test_data["auth_token"]["authorize"]["valid_response"]
    mock_auth_post_create_cloud_account.return_value = mock_response
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    payload["type"] = "blalbla"
    with pytest.raises(CloudAccountNotAllowed):
        await async_client.post(
            "/organizations/my_org_id/cloud_accounts",
            json=payload,
            headers={"Authorization": "Bearer good token"},
        )


async def test_exception_handling(
    async_client: AsyncClient,
    test_data: dict,
    caplog,
    mock_optscale_post_link_cloud_account_with_org,
    mock_auth_post_create_cloud_account,
):
    mock_response = test_data["auth_token"]["authorize"]["valid_response"]
    mock_auth_post_create_cloud_account.return_value = mock_response
    mock_optscale_post_link_cloud_account_with_org.side_effect = APIResponseError(
        title="Error response from OptScale",
        reason="Test Exception",
        status_code=403,
        error_code="test error code",
    )
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        response = await async_client.post(
            "/organizations/my_org_id/cloud_accounts",
            json=payload,
            headers={"Authorization": "Bearer good token"},
        )
        assert response.status_code == 403
        got = response.json()
        assert got.get("error").get("reason") == "Test Exception"
        assert got.get("error").get("error_code") == "test error code"
        assert (
            "An error occurred adding the cloud account azure_tenant "
            == caplog.messages[0]
        )


async def test_no_auth(
    async_client: AsyncClient,
    test_data: dict,
    caplog,
    mock_optscale_post_link_cloud_account_with_org,
    mock_auth_post_create_cloud_account,
):
    mock_response = test_data["auth_token"]["authorize"]["error_response"]
    mock_auth_post_create_cloud_account.return_value = mock_response
    mock_optscale_post_link_cloud_account_with_org.side_effect = APIResponseError(
        title="Error response from OptScale",
        reason="Test Exception",
        status_code=403,
        error_code="test error code",
    )
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        response = await async_client.post(
            "/organizations/my_org_id/cloud_accounts",
            json=payload,
            headers={},
        )
        assert response.status_code == 403
