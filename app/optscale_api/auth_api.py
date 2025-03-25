from __future__ import annotations

import logging

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import UserAccessTokenError, raise_api_response_exception

logger = logging.getLogger(__name__)

AUTH_TOKEN_ENDPOINT = "/tokens"  # nosec B105
AUTH_TOKEN_AUTHORIZE_ENDPOINT = "/authorize"  # nosec B105"


def build_admin_api_key_header(admin_api_key: str) -> dict[str, str]:
    """
    Builds headers with the admin API key for root-level operations
    :param admin_api_key: the secret API key
    :type admin_api_key: string
    :return: a dictionary {"Secret": "secret key here"}
    """
    return {"Secret": admin_api_key}


def build_bearer_token_header(bearer_token: str) -> dict[str, str]:
    """
    Builds the headers with the Bearer token for user-level operations
    :param bearer_token: the Bearer token to use
    :type bearer_token: string
    :return: a dict {"Authorization": f"Bearer MYTOKENHERE"}
    """
    return {"Authorization": f"Bearer {bearer_token}"}


class OptScaleAuth:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.optscale_auth_api_base_url)

    async def check_user_allowed_to_create_cloud_account(
        self, bearer_token: str, org_id: str
    ) -> None | Exception:
        """
         It validates the given bearer_token by making a request
         to auth/v2/authorize.
         This is used to protect the /organization/{org_id}/cloud_accounts
         endpoint from being consumed with a not valid bearer token and fix
         the following corner case scenario:
         - Wrong Authentication Bearer Token or an expired one.
        -  Wrong value in the type field of the payload.
        Result: The service will return a 403 with an indication about a
        not-allowed cloud type instead of processing the wrong authorization
        as the first thing.
        :param bearer_token: The user access's token
        :param org_id: The org ID that owned by the user identified by the bearer_token
        :return:
        """
        payload = {
            "action": "MANAGE_CLOUD_CREDENTIALS",
            "resource_type": "organization",
            "uuid": org_id,
        }
        headers = build_bearer_token_header(bearer_token=bearer_token)
        response = await self.api_client.post(
            endpoint=AUTH_TOKEN_AUTHORIZE_ENDPOINT, headers=headers, data=payload
        )
        if response.get("error"):
            logger.error("Failed validate the given bearer token")
            return raise_api_response_exception(response)

    async def obtain_user_auth_token_with_admin_api_key(
        self, user_id: str, admin_api_key: str
    ) -> str | Exception:
        """
        Obtains an authentication token for the given user_id using the admin API key
        :param user_id: the user's ID for whom the access token will be generated
        :type user_id: string
        :param admin_api_key: the secret API key
        :type admin_api_key: string
        :return: The user authentication token if successfully obtained and verified,
        otherwise a UserAccessTokenError exception

        """
        payload = {"user_id": user_id}
        headers = build_admin_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.post(
            endpoint=AUTH_TOKEN_ENDPOINT, headers=headers, data=payload
        )
        if response.get("error"):
            logger.error(f"Failed to get an admin access token for user {user_id}")
            return raise_api_response_exception(response)

        if response.get("data", {}).get("user_id", 0) != user_id:
            unmatched_user_id = response.get("data", {}).get("user_id", 0)
            logger.error(
                f"User ID mismatch: requested {user_id}, "
                f"received {unmatched_user_id}"
            )
            raise UserAccessTokenError("Access Token User ID mismatch")
        token = response.get("data", {}).get("token")
        if token is None:
            logger.error("Token not found in the response.")
            raise UserAccessTokenError("Token not found in the response.")
        logger.info("Admin Access Token successfully obtained")
        return token
