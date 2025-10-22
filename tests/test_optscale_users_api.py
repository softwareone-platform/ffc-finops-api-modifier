import logging

import pytest

from app.core.exceptions import APIResponseError

USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789a"
INVALID_USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789k"
ADMIN_API_KEY = "f2312f2b-46h0-4456-o0i9-58e64f2j6725"
EMAIL = "peter.parker@iamspiderman.com"
DISPLAY_NAME = "Spider Man"
PASSWORD = "With great power comes great responsibility"


async def test_create_valid_user(optscale_api, mock_optscale_api_post, test_data: dict):
    mock_response = test_data["user"]["case_create"]["response"]
    mock_response["data"]["token"] = "valid_jwt"
    mock_optscale_api_post.return_value = mock_response

    response = await optscale_api.create_user(
        email=EMAIL,
        display_name=DISPLAY_NAME,
        password=PASSWORD,
        admin_api_key="test_key",
        verified=True,
    )
    got = response
    want = test_data["user"]["case_create"]["response"]
    want["data"]["token"] = "valid_jwt"
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"
    mock_optscale_api_post.assert_called_once_with(
        endpoint="/users",
        headers={"Secret": "test_key"},
        data={
            "email": EMAIL,
            "display_name": DISPLAY_NAME,
            "password": PASSWORD,
            "verified": True,
        },
    )


async def test_valid_get_user_by_id(
    optscale_api, mock_optscale_api_client_get, test_data: dict, user_id=USER_ID
):  # noqa: PT028
    mock_response = test_data["user"]["case_create"]["response"]
    mock_response["data"]["token"] = "valid_jwt"
    mock_optscale_api_client_get.return_value = mock_response

    response = await optscale_api.get_user_by_id(
        user_id=user_id, admin_api_key=ADMIN_API_KEY
    )
    got = response
    want = test_data["user"]["case_create"]["response"]
    want["data"]["token"] = "valid_jwt"
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"
    mock_optscale_api_client_get.assert_called_once_with(
        endpoint=f"/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
    )


async def test_invalid_get_user_by_id(
    optscale_api, mock_optscale_org_api_client_get, user_id=INVALID_USER_ID
):  # noqa: PT028
    mock_response = {
        "error": {
            "status_code": 404,
            "error_code": "OA0043",
            "reason": f"Failed to get the user {INVALID_USER_ID} data from OptScale",
            "params": [user_id],
        }
    }

    mock_optscale_org_api_client_get.return_value = mock_response
    with pytest.raises(APIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=user_id, admin_api_key=ADMIN_API_KEY)
        mock_optscale_org_api_client_get.assert_called_once_with(
            endpoint=f"/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
        )


async def test_get_user_with_invalid_admin_api_key(
    optscale_api, mock_optscale_org_api_client_get
):
    mock_response = {
        "error": {
            "status_code": 403,
            "error_code": "OA0006",
            "reason": "Bad secret",
            "params": [],
        }
    }
    mock_optscale_org_api_client_get.return_value = mock_response

    with pytest.raises(APIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=USER_ID, admin_api_key="invalid_key")

        mock_optscale_org_api_client_get.assert_called_once_with(
            endpoint=f"/users/{USER_ID}", headers={"Secret": "invalid_key"}
        )


async def test_delete_user(optscale_api, mock_optscale_api_delete, caplog):
    mock_response = {"status_code": 204}
    mock_optscale_api_delete.return_value = mock_response
    await optscale_api.delete_user(user_id="user_id", admin_api_key="test_key")
    assert "User user_id successfully deleted" == caplog.messages[0]
    mock_optscale_api_delete.assert_called_once_with(
        endpoint="/users/user_id", headers={"Secret": "test_key"}
    )


async def test_delete_user_exception_handling(
    optscale_api, mock_optscale_api_delete, caplog
):
    mock_response = {
        "error": {
            "status_code": 403,
            "error_code": "OA0006",
            "reason": "Bad secret",
            "params": [],
        }
    }
    mock_optscale_api_delete.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(APIResponseError):
            await optscale_api.delete_user(user_id="user_id", admin_api_key="test_key")
        assert "Failed to delete the user user_id from OptScale" == caplog.messages[0]
