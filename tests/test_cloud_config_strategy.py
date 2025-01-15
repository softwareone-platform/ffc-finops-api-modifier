from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)
from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI


@pytest.fixture
def optscale_cloud_account_api():
    """Provides a clean instance of OptScaleCloudAccountAPI for each test."""
    return OptScaleCloudAccountAPI()


@pytest.fixture
def mock_post(mocker, optscale_cloud_account_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(
        optscale_cloud_account_api.api_client, "post", new=AsyncMock()
    )
    return mock_post


class TestCloudConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["field1", "field2", "field3"]


async def test_link_cloud_account_to_org(
    async_client: AsyncClient, test_data: dict, optscale_cloud_account_api, mock_post
):
    payload = test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["conf"]
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    mock_post.return_value = mocked_response
    strategy = TestCloudConfigStrategy(
        optscale_cloud_account_api=optscale_cloud_account_api
    )
    response = await strategy.link_cloud_account_to_org(
        config=payload,
        user_access_token="good token",
        org_id="my_org_id",
    )
    assert response == mocked_response


async def test_link_cloud_account_to_org_exceptions(
    async_client: AsyncClient, test_data: dict, optscale_cloud_account_api, mock_post
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
    mock_post.return_value = mocked_error_response

    strategy = TestCloudConfigStrategy(
        optscale_cloud_account_api=optscale_cloud_account_api
    )
    with pytest.raises(OptScaleAPIResponseError):
        await strategy.link_cloud_account_to_org(
            config=payload, user_access_token="good token", org_id="my_org_id"
        )


def test_required_fields():
    strategy = TestCloudConfigStrategy(
        optscale_cloud_account_api=OptScaleCloudAccountAPI()
    )
    fields = strategy.required_fields()
    assert isinstance(fields, list)
    assert fields == ["field1", "field2", "field3"]


def test_abstract_class_instantiation():
    with pytest.raises(
        TypeError, match="Can't instantiate abstract class CloudConfigStrategy"
    ):
        CloudConfigStrategy()
