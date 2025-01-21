from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.api.users.services.optscale_users_registration import validate_user_invitation
from app.optscale_api.invitation_api import OptScaleInvitationAPI


@pytest.fixture
def mock_get_list_of_invitations():
    patcher = patch.object(
        OptScaleInvitationAPI, "get_list_of_invitations", new=AsyncMock()
    )  # noqa: E501
    mock = patcher.start()
    yield mock
    patcher.stop()


async def test_validate_user_invitation(
    async_client: AsyncClient,
    mock_get_list_of_invitations,
):
    mock_get_list_of_invitations.return_value = {
        "data": {"invites": [{"field": "value"}]}
    }
    response = await validate_user_invitation(email="homer.simpson@springfield.wow")
    assert response is True


async def test_validate_user_invitation_no_invitation(
    async_client: AsyncClient,
    mock_get_list_of_invitations,
):
    mock_get_list_of_invitations.return_value = {"data": {"invites": []}}
    response = await validate_user_invitation(email="homer.simpson@springfield.wow")
    assert response is False
