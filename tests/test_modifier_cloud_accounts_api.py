import logging
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.api.cloud_account.cloud_accounts_manager import (
    CloudStrategyManager,
)
from app.core.exceptions import OptScaleAPIResponseError


@pytest.fixture
def mock_add_cloud_account():
    patcher = patch.object(CloudStrategyManager, "add_cloud_account", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


async def test_create_datasource(
    async_client: AsyncClient,
    test_data: dict,
    mock_add_cloud_account,
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    mock_add_cloud_account.return_value = mocked_response

    response = await async_client.post(
        "/cloud_accounts", json=payload, headers={"Authorization": "Bearer good token"}
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
    mock_add_cloud_account,
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    want = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    mock_add_cloud_account.return_value = mocked_response

    response = await async_client.post(
        "/cloud_accounts", json=payload, headers={"Authorization": "Bearer good token"}
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
    mock_add_cloud_account,
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    payload["type"] = "blalbla"
    response = await async_client.post(
        "/cloud_accounts", json=payload, headers={"Authorization": "Bearer good token"}
    )
    assert response.status_code == 403
    got = response.json()
    assert got.get("error").get("reason") == "blalbla is not supported"
    assert got.get("error").get("error_code") == "OE0436"


async def test_exception_handling(
    async_client: AsyncClient,
    test_data: dict,
    caplog,
    mock_add_cloud_account,
):
    mock_add_cloud_account.side_effect = OptScaleAPIResponseError(
        title="Error response from OptScale",
        reason="Test Exception",
        status_code=403,
        error_code="test error code",
    )
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        response = await async_client.post(
            "/cloud_accounts",
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
    mock_add_cloud_account,
):
    mock_add_cloud_account.side_effect = OptScaleAPIResponseError(
        title="Error response from OptScale",
        reason="Test Exception",
        status_code=403,
        error_code="test error code",
    )
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    with caplog.at_level(logging.ERROR):
        response = await async_client.post(
            "/cloud_accounts",
            json=payload,
            headers={},
        )
        assert response.status_code == 403
