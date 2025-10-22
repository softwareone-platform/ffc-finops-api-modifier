import json
import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import settings
from app.core.api_client import APIClient
from app.core.auth_jwt_bearer import JWTBearer
from app.core.exceptions import APIResponseError, UserAccessTokenError
from app.main import app
from app.optscale_api.auth_api import OptScaleAuth
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.optscale_api.users_api import OptScaleUserAPI


# Mock dependency to bypass JWTBearer authentication
def mock_jwt_bearer():
    return True  # Mocking successful authentication


def pytest_configure():
    # Override settings with defaults for testing
    settings.model_config["env_file"] = "/app/.env.test"


# Override JWTBearer dependency for all tests
@pytest.fixture(scope="session", autouse=True)
def override_jwt_bearer():
    app.dependency_overrides[JWTBearer] = mock_jwt_bearer
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://") as client:
        yield client


@pytest.fixture
def test_data() -> dict:
    path = os.getenv("PYTEST_CURRENT_TEST")
    path = os.path.join(*os.path.split(path)[:-1], "data.json")
    if not os.path.exists(path):
        path = os.path.join("tests/data", "data.json")

    with open(path) as file:
        data = json.loads(file.read())

    return data


@pytest.fixture
def optscale_cloud_account_api():
    """Provides a clean instance of OptScaleCloudAccountAPI for each test."""
    return OptScaleCloudAccountAPI()


@pytest.fixture
def mock_optscale_cloud_account_api_post_method(mocker, optscale_cloud_account_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(
        optscale_cloud_account_api.api_client, "post", new=AsyncMock()
    )
    return mock_post


@pytest.fixture
def optscale_api():
    """Provides a clean instance of OptScaleUserAPI for each test."""
    return OptScaleUserAPI()


@pytest.fixture
def opt_scale_invitation():
    return OptScaleInvitationAPI()


@pytest.fixture
def optscale_org_api():
    return OptScaleOrgAPI()


@pytest.fixture
def opt_scale_auth():
    return OptScaleAuth()


@pytest.fixture
def mock_opt_scale_invitation_patch(mocker, opt_scale_invitation):
    mock_patch = mocker.patch.object(
        opt_scale_invitation.api_client, "patch", new=AsyncMock()
    )
    return mock_patch


@pytest.fixture
def mock_opt_scale_invitation_get(mocker, opt_scale_invitation):
    mock_get = mocker.patch.object(
        opt_scale_invitation.api_client, "get", new=AsyncMock()
    )
    return mock_get


@pytest.fixture
def mock_optscale_auth_api_post(mocker, opt_scale_auth):
    mock_post = mocker.patch.object(opt_scale_auth.api_client, "post", new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_optscale_auth_api_get(mocker, opt_scale_auth):
    mock_get = mocker.patch.object(opt_scale_auth.api_client, "get", new=AsyncMock())
    return mock_get


@pytest.fixture
def mock_optscale_api_post(mocker, optscale_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(optscale_api.api_client, "post", new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_optscale_api_client_get(mocker, optscale_api):
    """Mock the `get` method in `api_client`."""
    mock_optscale_api_client_get = mocker.patch.object(
        optscale_api.api_client, "get", new=AsyncMock()
    )
    return mock_optscale_api_client_get


@pytest.fixture
def mock_optscale_api_delete(mocker, optscale_api):
    """Mock the `post` method in `api_client`."""
    mock_delete = mocker.patch.object(
        optscale_api.api_client, "delete", new=AsyncMock()
    )
    return mock_delete


@pytest.fixture
def mock_optscale_org_api_post(mocker, optscale_org_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(
        optscale_org_api.api_client, "post", new=AsyncMock()
    )
    return mock_post


@pytest.fixture
def mock_optscale_org_api_client_get(mocker, optscale_org_api):
    mock_get = mocker.patch.object(optscale_org_api.api_client, "get", new=AsyncMock())
    return mock_get


@pytest.fixture
def mock_auth_token(mocker, opt_scale_auth):
    mock_auth_token = mocker.patch.object(
        opt_scale_auth,
        "obtain_user_auth_token_with_admin_api_key",
        return_value="good token",
    )
    return mock_auth_token


@pytest.fixture
def mock_invalid_auth_token(mocker, opt_scale_auth):
    mock_auth_token = mocker.patch.object(
        opt_scale_auth,
        "obtain_user_auth_token_with_admin_api_key",
        side_effect=UserAccessTokenError("Failed to get an admin access token"),
    )
    return mock_auth_token


@pytest.fixture
def mock_auth_post_create_cloud_account():
    patcher = patch.object(
        OptScaleAuth, "check_user_allowed_to_create_cloud_account", new=AsyncMock()
    )
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_optscale_post_link_cloud_account_with_org():
    patcher = patch.object(
        OptScaleCloudAccountAPI, "link_cloud_account_with_org", new=AsyncMock()
    )
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def api_client():
    return APIClient(base_url="http://testserver")


@pytest.fixture
def mock_invitation_api(mocker):
    def _mock_invitation_api(return_value):
        mock = AsyncMock()
        mock.get_list_of_invitations.return_value = return_value
        mocker.patch(
            "app.optscale_api.invitation_api.OptScaleInvitationAPI", return_value=mock
        )
        return mock

    return _mock_invitation_api


@pytest.fixture
def mock_org_api(mocker):
    def _mock_org_api(return_value):
        mock = AsyncMock()
        mock.get_user_org_list.return_value = return_value
        mocker.patch(
            "app.optscale_api.orgs_api.OptScaleOrgAPI", return_value=mock_org_api
        )
        return mock

    return _mock_org_api


@pytest.fixture
def mock_user_api(mocker):
    def _mock_user_api(should_raise=False):
        mock = AsyncMock()
        if should_raise:
            mock.delete_user.side_effect = APIResponseError(
                title="Error response from OptScale",
                reason="Test",
                status_code=403,
                error_code="test error code",
            )
        else:
            mock.delete_user.return_value = None
        mocker.patch("app.optscale_api.users_api.OptScaleUserAPI", return_value=mock)
        return mock

    return _mock_user_api


@pytest.fixture
def mock_register_invited():
    patcher = patch.object(OptScaleUserAPI, "create_user", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_decline_invitation():
    patcher = patch.object(OptScaleInvitationAPI, "decline_invitation", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_get_list_of_invitations():
    patcher = patch.object(
        OptScaleInvitationAPI, "get_list_of_invitations", new=AsyncMock()
    )  # noqa: E501
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_optscale_auth_post():
    patcher = patch.object(
        OptScaleAuth, "obtain_user_auth_token_with_admin_api_key", new=AsyncMock()
    )  # noqa: E501
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_get_org():
    patcher = patch.object(
        OptScaleOrgAPI, "access_user_org_list_with_admin_key", new=AsyncMock()
    )
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_create_org():
    patcher = patch.object(OptScaleOrgAPI, "create_user_org", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_create_user():
    patcher = patch.object(OptScaleUserAPI, "create_user", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()
