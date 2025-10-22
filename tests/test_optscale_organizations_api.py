import logging

import pytest

from app.core.exceptions import (
    APIResponseError,
    UserAccessTokenError,
    UserOrgCreationError,
)


async def test_create_user_org(
    optscale_org_api,
    mock_optscale_org_api_post,
    mock_auth_token,
    opt_scale_auth,
    test_data: dict,
):
    mock_optscale_org_api_post.return_value = test_data["org"]["case_create"][
        "response"
    ]

    response = await optscale_org_api.create_user_org(
        org_name="MyOrg",
        currency="USD",
        user_id="test_user",
        admin_api_key="test_key",
        auth_client=opt_scale_auth,
    )

    got = response
    want = test_data["org"]["case_create"]["response"]
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"

    # Assert that mock_post was called with expected arguments
    mock_optscale_org_api_post.assert_called_once_with(
        endpoint="/organizations",
        data={"name": "MyOrg", "currency": "USD"},
        headers={"Authorization": "Bearer good token"},
    )


async def test_create_user_org_with_invalid_currency(
    caplog,
    optscale_org_api,
    mock_auth_token,
    opt_scale_auth,
):
    with caplog.at_level(logging.ERROR):
        result = await optscale_org_api.create_user_org(
            org_name="Test Org",
            currency="not valid currency",
            user_id="test_user",
            admin_api_key="test_key",
            auth_client=opt_scale_auth,
        )

        assert result is None, "Expected None for invalid currency"
        assert (
            "Invalid currency: not valid currency" in caplog.text
        ), "Expected error message for invalid currency"


async def test_get_user_org_with_no_token(
    optscale_org_api,
    mock_invalid_auth_token,
    opt_scale_auth,
    caplog,
):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            UserAccessTokenError,
            match="Failed to get an admin access token",
        ):
            await optscale_org_api.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    # Verify the log entry
    assert (
        "Failed to get an admin access token" in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_get_user_org_empty_response(
    optscale_org_api, mock_optscale_org_api_client_get, mock_auth_token, opt_scale_auth
):
    mock_optscale_org_api_client_get.return_value = {"organizations": []}
    result = await optscale_org_api.access_user_org_list_with_admin_key(
        user_id="test_user", admin_api_key="test_key", auth_client=opt_scale_auth
    )
    assert result == {"organizations": []}
    mock_optscale_org_api_client_get.assert_called_once_with(
        endpoint="/organizations",
        headers={"Authorization": "Bearer good token"},
    )


async def test_get_user_org_response_error(
    optscale_org_api,
    mock_optscale_org_api_client_get,
    mock_auth_token,
    opt_scale_auth,
    caplog,
):
    mock_optscale_org_api_client_get.return_value = {
        "error": "This is an error! ",
        "status_code": 403,
        "data": {"error": {"reason": "Oh no, I made a mistake!"}},
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(APIResponseError):  # noqa: PT012
            await optscale_org_api.access_user_org_list_with_admin_key(
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )


async def test_get_user_orgs_exceptions_handling(
    optscale_org_api,
    mock_optscale_org_api_client_get,
    mock_auth_token,
    opt_scale_auth,
    caplog,
):
    mock_optscale_org_api_client_get.side_effect = UserAccessTokenError(
        "Access Token exception"
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserAccessTokenError, match="Access Token exception"):
            await optscale_org_api.access_user_org_list_with_admin_key(
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    # Verify the log entry
    assert (
        "Failed to get access token for user test_user: Access Token exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501

    mock_optscale_org_api_client_get.side_effect = Exception("Generic Exception")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Generic Exception"):
            await optscale_org_api.access_user_org_list_with_admin_key(
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    # Verify the log entry
    assert (
        "Failed to get access token for user test_user: Access Token exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_create_org_access_token_exception_handling(
    optscale_org_api,
    mock_optscale_org_api_post,
    mock_auth_token,
    opt_scale_auth,
    caplog,
):
    # Simulate a UserAccessTokenError exception  in `create_user_org`
    mock_optscale_org_api_post.side_effect = UserAccessTokenError(
        "Access Token exception"
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserAccessTokenError, match="Access Token exception"):
            await optscale_org_api.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    # Verify the log entry
    assert (
        "Failed to get access token for user test_user: Access Token exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


async def test_create_org_user_org_creation_exception_handling(
    optscale_org_api,
    mock_optscale_org_api_post,
    mock_auth_token,
    opt_scale_auth,
    caplog,
):
    # Simulate a UserOrgCreationError exception  in `create_user_org`
    mock_optscale_org_api_post.side_effect = UserOrgCreationError(
        "Org Creation exception"
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserOrgCreationError, match="Org Creation exception"):
            await optscale_org_api.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    # Verify the log entry
    assert (
        "Exception occurred creating an organization on OptScale: Org Creation exception"
        in caplog.text
    ), "Expected error log message for the exception"  # noqa: E501


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "side_effect, expected_exception, expected_message",  # noqa: PT006
    [
        (
            Exception("Test Exception"),
            Exception,
            "Exception occurred creating an organization on OptScale: Test Exception",
        ),
        (
            UserAccessTokenError("User Access Token not valid"),
            UserAccessTokenError,
            "Failed to get access token for user test_user: User Access Token not valid",
        ),
    ],
)
async def test_create_org_user_exception_handling(
    optscale_org_api,
    mock_optscale_org_api_post,
    mock_auth_token,
    opt_scale_auth,
    caplog,
    side_effect,
    expected_exception,
    expected_message,
):
    mock_optscale_org_api_post.side_effect = side_effect
    with caplog.at_level(logging.ERROR):
        with pytest.raises(expected_exception, match=str(side_effect)):
            await optscale_org_api.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )
    assert any(expected_message in record.message for record in caplog.records)


async def test_create_org_user_response_error(
    optscale_org_api,
    mock_optscale_org_api_post,
    mock_auth_token,
    opt_scale_auth,
    caplog,
):
    mock_optscale_org_api_post.return_value = {
        "status_code": 403,
        "error": "Invalid JSON format in response",
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(APIResponseError) as exc_info:
            await optscale_org_api.create_user_org(
                org_name="MyOrg",
                currency="USD",
                user_id="test_user",
                admin_api_key="test_key",
                auth_client=opt_scale_auth,
            )

        exception = exc_info.value
        assert exception.error.get("error_code") == ""
        assert exception.error.get("reason") == "No details available"
        assert exception.status_code == 403

        # check the logging message printed by the create_user_org
        assert any(
            "An error occurred creating an organization for user test_user."
            in record.message
            for record in caplog.records
        )
        # check the logging message printed by the APIResponseError
        assert any(
            "Exception occurred creating an organization on OptScale" in record.message
            for record in caplog.records
        )
