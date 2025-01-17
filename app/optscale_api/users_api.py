from __future__ import annotations

import logging

from app import settings
from app.api.users.services.user_verification import validate_user_invitation
from app.core.api_client import APIClient
from app.core.exceptions import InvitationDoesNotExist, raise_api_response_exception

from .auth_api import build_admin_api_key_header

AUTH_USERS_ENDPOINT = "/auth/v2/users"
logger = logging.getLogger(__name__)


class OptScaleUserAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    # todo: check the password lenght and strength
    async def create_user(
        self,
        email: str,
        display_name: str,
        password: str,
        admin_api_key: str,
        verified: bool = False,
        check_user_email: bool = False,
    ) -> dict[str, str] | Exception:
        """
        Creates a new user in the system.

        :param check_user_email: If True, we need to check if an invitation has been
        generated for the given user before creating it.
        :param verified: if verified is True, an access token will be
        generated for the registered user. Otherwise, the token will be None
        :param admin_api_key: the secret admin API key
        :param email: The email of the user.
        :param display_name: The display name of the user
        :param password: The password of the user.
        :return:dict[str, str] : User information.
        :raises APIResponseError if any error occurs
        contacting the OptScale APIs
        """
        email_check = False
        if check_user_email:
            # We need to verify if an invitation has been sent for the given user
            # If an invitation exists, the user will be created
            email_check = await validate_user_invitation(email=email)
            if email_check:
                verified = False
            else:
                # there is no invitation for the given user. Stop here!
                logger.error(f"An error occurred registering the invited user {email}")
                raise InvitationDoesNotExist(
                    f"There is no invitation for this email  {email}"
                )
        payload = {
            "email": email,
            "display_name": display_name,
            "password": password,
            "verified": verified,
        }
        headers = build_admin_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.post(
            endpoint=AUTH_USERS_ENDPOINT, data=payload, headers=headers
        )
        if response.get("error"):
            logger.error("Failed to create the requested user")
            return raise_api_response_exception(response)
        if email_check:
            logger.info(f"Invited User successfully registered: {response}")
        else:
            logger.info(f"User successfully created: {response}")
        return response

    async def get_user_by_id(
        self, admin_api_key: str, user_id: str
    ) -> dict[str, str] | None:
        """
        Retrieves a user's information

        :param admin_api_key: The secret admin API key
        :param user_id: The user's ID for whom we want to retrieve the information
        :return: A dict with the user's information if found
        :raises APIResponseError if any error occurs
        contacting the OptScale APIs
        example
        {
            "created_at": 1730126521,
            "deleted_at": 0,
            "id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a",
            "display_name": "Spider Man",
            "is_active": True,
            "type_id": 1,
            "email": "peter.parker@iamspiderman.com",
            "scope_id": None,
            "slack_connected": False,
            "is_password_autogenerated": False,
            "jira_connected": False,
            "scope_name": None
        }

        """

        headers = build_admin_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.get(
            endpoint=AUTH_USERS_ENDPOINT + "/" + user_id, headers=headers
        )
        if response.get("error"):
            logger.info(f"Failed to get the user {user_id} data from OptScale")
            return raise_api_response_exception(response)
        logger.info(f"User Successfully fetched : {response}")
        return response

    async def delete_user(self, user_id: str, admin_api_key: str):
        """
        Removes a user from OptScale
        :param user_id: The ID of the user to remove
        :param admin_api_key: The secret admin API key
        :return: No content if the operation is completed without errors.
        :raises: APIResponseError if any error occurs
        contacting the OptScale APIs
        """
        headers = build_admin_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.delete(
            endpoint=AUTH_USERS_ENDPOINT + f"/{user_id}", headers=headers
        )
        if response.get("error"):
            logger.error(f"Failed to delete the user {user_id} from OptScale")
            return raise_api_response_exception(response)
        logger.info(f"User {user_id} successfully deleted")
        return response
