import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    OptScaleAPIResponseError,
    UserAccessTokenError,
    UserOrgCreationError,
)
from app.optscale_api.auth_api import OptScaleAuth
from app.optscale_api.orgs_api import OptScaleOrgAPI

ORG_RESPONSE = {
    "deleted_at": 0,
    "created_at": 1729695339,
    "id": "dcbe83cd-18bf-4951-87aa-2764d723535b",
    "name": "MyOrg",
    "pool_id": "90991262-16ec-4246-be18-a22a31eeec57",
    "is_demo": False,
    "currency": "USD",
    "cleaned_at": 0,
}


@pytest.fixture
def optscale_org_api_instance():
    return OptScaleOrgAPI()


@pytest.fixture
def optscale_auth_api():
    return OptScaleAuth()


@pytest.fixture
def mock_api_client_post(mocker, optscale_org_api_instance):
    mock_post = mocker.patch.object(
        optscale_org_api_instance.api_client, "post", new=AsyncMock()
    )
    return mock_post


@pytest.fixture
def mock_api_client_get(mocker, optscale_org_api_instance):
    mock_get = mocker.patch.object(
        optscale_org_api_instance.api_client, "get", new=AsyncMock()
    )
    return mock_get


@pytest.fixture
def mock_auth_token(mocker, optscale_auth_api):
    mock_auth_token = mocker.patch.object(
        optscale_auth_api,
        "obtain_user_auth_token_with_admin_api_key",
        return_value="good token",
    )
    return mock_auth_token


@pytest.fixture
def mock_invalid_auth_token(mocker, optscale_auth_api):
    mock_auth_token = mocker.patch.object(
        optscale_auth_api,
        "obtain_user_auth_token_with_admin_api_key",
        return_value=None,
    )
    return mock_auth_token


async def test_create_user_org(
    optscale_org_api_instance, mock_api_client_post, mock_auth_token, optscale_auth_api
):
    mock_api_client_post.return_value = ORG_RESPONSE

    result = await optscale_org_api_instance.create_user_org(
        org_name="MyOrg",
        currency="USD",
        user_id="test_user",
        admin_api_key="test_key",
        auth_client=optscale_auth_api,
    )

    assert result == ORG_RESPONSE
    # Assert that mock_post was called with expected arguments
    mock_api_client_post.assert_called_once_with(
        endpoint="/restapi/v2/organizations",
        data={"name": "MyOrg", "currency": "USD"},
        headers={"Authorization": "Bearer good token"},
    )


async def test_create_user_org_with_invalid_currency(
    caplog,
    optscale_org_api_instance,
    mock_api_client_post,
    mock_auth_token,
    optscale_auth_api,
):
    with caplog.at_level(logging.ERROR):
        result = await optscale_org_api_instance.create_user_org(
            org_name="Test Org",
            currency="not valid currency",
            user_id="test_user",
            admin_api_key="test_key",
            auth_client=optscale_auth_api,
        )

        assert result is None, "Expected None for invalid currency"
        assert (
            "Invalid currency: not valid currency" in caplog.text
        ), "Expected error message for invalid currency"


async def test_get_user_org_with_no_token(
    optscale_org_api_instance,
    mock_api_client_post,
    mock_invalid_auth_token,
    optscale_auth_api,
    caplog,
):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            UserAccessTokenError,
            match="Access token could not be obtained for user: test_user",
        ):
            await optscale_org_api_instance.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=optscale_auth_api,
            )
    # Verify the log entry
    assert (
        "Access token could not be obtained for user: test_user" in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_get_user_org_empty_response(
    optscale_org_api_instance, mock_api_client_get, mock_auth_token, optscale_auth_api
):
    mock_api_client_get.return_value = {"organizations": []}
    result = await optscale_org_api_instance.get_user_org(
        user_id="test_user", admin_api_key="test_key", auth_client=optscale_auth_api
    )
    assert result == {"organizations": []}
    mock_api_client_get.assert_called_once_with(
        endpoint="/restapi/v2/organizations",
        headers={"Authorization": "Bearer good token"},
    )


async def test_get_user_org_response_error(
    optscale_org_api_instance,
    mock_api_client_get,
    mock_auth_token,
    optscale_auth_api,
    caplog,
):
    mock_api_client_get.return_value = {
        "error": "This is an error! ",
        "status_code": 403,
        "data": {"error": {"reason": "Oh no, I made a mistake!"}},
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            OptScaleAPIResponseError, match="Error response from OptScale"
        ):  # noqa: PT012
            await optscale_org_api_instance.get_user_org(
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=optscale_auth_api,
            )


async def test_create_org_access_token_exception_handling(
    optscale_org_api_instance,
    mock_api_client_post,
    mock_auth_token,
    optscale_auth_api,
    caplog,
):
    # Simulate a UserAccessTokenError exception  in `create_user_org`
    mock_api_client_post.side_effect = UserAccessTokenError("Access Token exception")
    # Capture logs
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserAccessTokenError, match="Access Token exception"):
            await optscale_org_api_instance.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=optscale_auth_api,
            )
    # Verify the log entry
    assert (
        "Access token error while creating an org for the user: test_user: Access Token exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_create_org_user_org_creation_exception_handling(
    optscale_org_api_instance,
    mock_api_client_post,
    mock_auth_token,
    optscale_auth_api,
    caplog,
):
    # Simulate a UserOrgCreationError exception  in `create_user_org`
    mock_api_client_post.side_effect = UserOrgCreationError("Org Creation exception")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserOrgCreationError, match="Org Creation exception"):
            await optscale_org_api_instance.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=optscale_auth_api,
            )
    # Verify the log entry
    assert (
        "Organization creation error for user: test_user - Org Creation exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_create_org_user_org_exception_handling(
    optscale_org_api_instance,
    mock_api_client_post,
    mock_auth_token,
    optscale_auth_api,
    caplog,
):
    # Simulate a generic Exception exception  in `create_user_org`
    mock_api_client_post.side_effect = Exception("Test Exception")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match=""):
            await optscale_org_api_instance.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=optscale_auth_api,
            )
    # Verify the log entry
    assert (
        "Exception occurred creating an org for the user: test_user - Test Exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501