import logging

import pytest

from app.core.exceptions import APIResponseError

INVITATION_ENDPOINT = "/invites"


async def test_decline_invitation(
    mock_opt_scale_invitation_patch, opt_scale_invitation, caplog
):
    payload = {"action": "decline"}
    mock_response = {"status_code": 204}
    mock_opt_scale_invitation_patch.return_value = mock_response
    await opt_scale_invitation.decline_invitation(
        user_access_token="valid user token",
        invitation_id="db540aac-451f-4288-b7b3-53e60e0a3653",
    )
    assert (
        "Invitation db540aac-451f-4288-b7b3-53e60e0a3653 has been declined"
        == caplog.messages[0]
    )
    mock_opt_scale_invitation_patch.assert_called_once_with(
        data=payload,
        endpoint=INVITATION_ENDPOINT + "/db540aac-451f-4288-b7b3-53e60e0a3653",
        headers={"Authorization": "Bearer valid user token"},
    )


async def test_decline_invitation_using_not_valid_invitation(
    mock_opt_scale_invitation_patch, opt_scale_invitation, caplog
):
    payload = {"action": "decline"}
    mock_response = {
        "error": {
            "status_code": 404,
            "error_code": "OA0043",
            "reason": "Invite db540aac-451f-4288-b7b3-53e60e0a3653 not found",
            "params": ["Invite", "db540aac-451f-4288-b7b3-53e60e0a3653"],
        }
    }
    mock_opt_scale_invitation_patch.return_value = mock_response
    with pytest.raises(APIResponseError):  # noqa: PT012
        await opt_scale_invitation.decline_invitation(
            user_access_token="valid user token",
            invitation_id="db540aac-451f-4288-b7b3-53e60e0a3653",
        )
        mock_opt_scale_invitation_patch.assert_called_once_with(
            data=payload,
            endpoint=INVITATION_ENDPOINT + "/db540aac-451f-4288-b7b3-53e60e0a3653",
            headers={"Authorization": "Bearer valid user token"},
        )


async def test_get_list_of_invitations(
    mock_opt_scale_invitation_get, opt_scale_invitation, caplog, test_data: dict
):
    mock_response = test_data["invitation"]["case_get"]["response"]
    mock_opt_scale_invitation_get.return_value = mock_response
    response = await opt_scale_invitation.get_list_of_invitations(
        user_access_token="user_token"
    )
    assert response == mock_response


async def test_get_list_of_invitations_with_email(
    mock_opt_scale_invitation_get, opt_scale_invitation, caplog, test_data: dict
):
    mock_response = test_data["invitation"]["case_get"]["response"]
    mock_opt_scale_invitation_get.return_value = mock_response
    response = await opt_scale_invitation.get_list_of_invitations(
        email="user_test_2@test.com"
    )
    assert response == mock_response


async def test_get_list_of_invitations_error(
    mock_opt_scale_invitation_get, opt_scale_invitation, caplog
):
    mock_response = {
        "status_code": 403,
        "data": {
            "error": {
                "status_code": 403,
                "error_code": "OA0042",
                "reason": "Test",
            }
        },
        "error": 'HTTP error: 403 - {"error": {"status_code": 403, "error_code": "OA0042",'  # noqa: E501
        '"reason": "Test"}}',
    }
    mock_opt_scale_invitation_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(APIResponseError):  # noqa: PT012
            await opt_scale_invitation.get_list_of_invitations(
                user_access_token="user_token"
            )
        assert "Failed to get list of invitations." == caplog.messages[0]


async def test_get_list_of_invitations_value_error(
    mock_opt_scale_invitation_get, opt_scale_invitation, caplog
):
    mock_response = {
        "status_code": 403,
        "data": {
            "error": {
                "status_code": 403,
                "error_code": "OA0042",
                "reason": "Test",
            }
        },
        "error": 'HTTP error: 403 - {"error": {"status_code": 403, "error_code": "OA0042",'  # noqa: E501
        '"reason": "Test"}}',
    }
    mock_opt_scale_invitation_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):  # noqa: PT012
            await opt_scale_invitation.get_list_of_invitations()
        assert (
            "Both 'user_access_token' and 'email' cannot be None." == caplog.messages[0]
        )
