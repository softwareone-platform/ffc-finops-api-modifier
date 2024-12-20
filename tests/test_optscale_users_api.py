import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.users_api import OptScaleUserAPI

USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789a"
INVALID_USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789k"
ADMIN_API_KEY = "f2312f2b-46h0-4456-o0i9-58e64f2j6725"
EMAIL = "peter.parker@iamspiderman.com"
DISPLAY_NAME = "Spider Man"
PASSWORD = "With great power comes great responsibility"


@pytest.fixture
def optscale_api():
    """Provides a clean instance of OptScaleUserAPI for each test."""
    return OptScaleUserAPI()


@pytest.fixture
def mock_post(mocker, optscale_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(optscale_api.api_client, "post", new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_get(mocker, optscale_api):
    """Mock the `get` method in `api_client`."""
    mock_get = mocker.patch.object(optscale_api.api_client, "get", new=AsyncMock())
    return mock_get


async def test_create_valid_user(optscale_api, mock_post):
    mock_response = {
        "created_at": 1730126521,
        "deleted_at": 0,
        "id": USER_ID,
        "display_name": DISPLAY_NAME,
        "is_active": True,
        "type_id": 1,
        "email": EMAIL,
        "verified": True,
        "scope_id": None,
        "slack_connected": False,
        "is_password_autogenerated": False,
        "jira_connected": False,
        "token": "valid_jwt_token",
    }
    mock_post.return_value = mock_response

    result = await optscale_api.create_user(
        email=EMAIL,
        display_name=DISPLAY_NAME,
        password=PASSWORD,
        admin_api_key="test_key",
    )

    mock_post.assert_called_once_with(
        endpoint="/auth/v2/users",
        headers={"Secret": "test_key"},
        data={
            "email": EMAIL,
            "display_name": DISPLAY_NAME,
            "password": PASSWORD,
            "verified": True,
        },
    )
    assert result == mock_response, "Expected a valid user creation response"


async def test_create_duplicate_user(caplog, optscale_api, mock_post):
    mock_response = {
        "data": {
            "error": {
                "error_code": "OA0042",
                "params": ["jerry.drake2@alphaagancy.com"],
                "reason": "User jerry.drake2@alphaagancy.com already exists",
                "status_code": 409,
            }
        },
        "error": 'HTTP error: 409 - {"error": {"status_code": 409, "error_code": "OA0042", '
        '"reason": "User jerry.drake2@alphaagancy.com already exists", '
        '"params": ["jerry.drake2@alphaagancy.com"]}}',
        "status_code": 409,
    }
    mock_post.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(  # noqa: PT012
            OptScaleAPIResponseError, match=""
        ):
            await optscale_api.create_user(
                email=EMAIL,
                display_name=DISPLAY_NAME,
                password=PASSWORD,
                admin_api_key="test_key",
            )
            mock_post.assert_called_once_with(
                endpoint="/auth/v2/users",
                data={
                    "email": EMAIL,
                    "display_name": DISPLAY_NAME,
                    "password": PASSWORD,
                },
            )
            # Verify the error log
    assert "Failed to create the requested user" in caplog.text


async def test_valid_get_user_by_id(optscale_api, mock_get, user_id=USER_ID):
    mock_response = {
        "created_at": 1730126521,
        "deleted_at": 0,
        "id": user_id,
        "display_name": DISPLAY_NAME,
        "is_active": True,
        "type_id": 1,
        "email": EMAIL,
        "scope_id": None,
        "slack_connected": False,
        "is_password_autogenerated": False,
        "jira_connected": False,
        "scope_name": None,
    }
    mock_get.return_value = mock_response

    await optscale_api.get_user_by_id(user_id=user_id, admin_api_key=ADMIN_API_KEY)

    mock_get.assert_called_once_with(
        endpoint=f"/auth/v2/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
    )


async def test_invalid_get_user_by_id(optscale_api, mock_get, user_id=INVALID_USER_ID):
    mock_response = {
        "error": {
            "status_code": 404,
            "error_code": "OA0043",
            "reason": f"Failed to get the user {INVALID_USER_ID} data from OptScale",
            "params": [user_id],
        }
    }

    mock_get.return_value = mock_response
    with pytest.raises(OptScaleAPIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=user_id, admin_api_key=ADMIN_API_KEY)
        mock_get.assert_called_once_with(
            endpoint=f"/auth/v2/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
        )


async def test_get_user_with_invalid_admin_api_key(optscale_api, mock_get):
    mock_response = {
        "error": {
            "status_code": 403,
            "error_code": "OA0006",
            "reason": "Bad secret",
            "params": [],
        }
    }
    mock_get.return_value = mock_response

    with pytest.raises(OptScaleAPIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=USER_ID, admin_api_key="invalid_key")

        mock_get.assert_called_once_with(
            endpoint=f"/auth/v2/users/{USER_ID}", headers={"Secret": "invalid_key"}
        )
