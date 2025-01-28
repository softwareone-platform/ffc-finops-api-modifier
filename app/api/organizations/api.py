from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app import settings
from app.api.cloud_account.model import AddCloudAccount, AddCloudAccountResponse
from app.api.invitations.api import get_bearer_token
from app.api.organizations.model import (
    CreateOrgData,
    OptScaleOrganization,
    OptScaleOrganizationResponse,
)
from app.api.organizations.services.optscale_cloud_accounts import (
    link_cloud_account_to_org,
)
from app.core.auth_jwt_bearer import JWTBearer
from app.core.exceptions import (
    APIResponseError,
    CloudAccountConfigError,
    format_error_response,
)
from app.optscale_api.auth_api import OptScaleAuth
from app.optscale_api.helpers.auth_tokens_dependency import get_auth_client
from app.optscale_api.orgs_api import OptScaleOrgAPI

router = APIRouter()

logger = logging.getLogger("__name__")


@router.get(
    path="",
    status_code=http_status.HTTP_200_OK,
    response_model=OptScaleOrganizationResponse,
    dependencies=[Depends(JWTBearer())],
)
async def get_orgs(
    user_id: str,
    auth_client: Annotated[OptScaleAuth, Depends(get_auth_client)],
    optscale_api: Annotated[OptScaleOrgAPI, Depends()],
):
    """
    Retrieve the organization data associated with a given user.

    This endpoint fetches the organization(s) for the specified user by interacting
    with the OptScale API.
    It returns the organization data as a JSON response.

    :param jwt_payload: A dictionary that will contain the access token or an error
    :param user_id:  The ID of the user whose organization data is to be retrieved.
    :param optscale_api: An instance of OptScaleOrgAPI for interacting with the organization API.
                        Dependency injection via `Depends()`.
    :param auth_client: An instance of OptScaleAuth for authentication.
                        Dependency injection via Depends(get_auth_client)`.

    :return: JSONResponse: A JSON response containing the organization data with an
            appropriate HTTP status code.

    :raises:
        the optscale_api.get_user_org() may raise these exceptions

        - APIResponseError: If an error occurs when communicating with the OptScale API.
        - UserAccessTokenError: If there is an issue obtaining the user's access token.
        - Exception: For any other unexpected errors.

        This Endpoint, returns a formatted error object like this one, as a result of
        each exception.
        {
            "detail": {
                "type": "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.3",
                "title": "Error response from OptScale",
                "status": 403,
                "traceId": "c4bd62b3fe154456af99380796fb669c",
                "errors": {
                    "reason": "Oh no, I made a mistake!"0
                }
            }
        }


    :dependencies:
        JWTBearer: Ensures that the request is authenticated using a valid JWT.
    """
    try:
        # send request with the Secret token to the OptScale API
        response = await optscale_api.access_user_org_list_with_admin_key(
            user_id=user_id, admin_api_key=settings.admin_token, auth_client=auth_client
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_200_OK),
            content=response.get("data", {}),
        )

    except Exception as error:
        return format_error_response(error)


@router.post(
    path="/{org_id}/cloud_accounts",
    status_code=http_status.HTTP_201_CREATED,
    response_model=AddCloudAccountResponse,
    dependencies=[],
)
async def link_cloud_account(
    org_id: str,
    data: AddCloudAccount,
    user_access_token: Annotated[str, Depends(get_bearer_token)],
    auth_client: Annotated[OptScaleAuth, Depends(get_auth_client)],
):
    try:
        # here, we need to validate the bearer token to ensure that any authorization
        # related errors will be checked first. In case of an invalid/expired token,
        # an APIResponseError with a http statu 401 will re raised

        await auth_client.validate_authorization(
            bearer_token=user_access_token, org_id=org_id
        )
        response = await link_cloud_account_to_org(
            name=data.name,
            type=data.type,
            config=data.config,
            process_recommendations=data.process_recommendations,
            auto_import=data.auto_import,
            org_id=org_id,
            user_access_token=user_access_token,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )

    except (APIResponseError, CloudAccountConfigError, ValueError) as error:
        logger.error(f"An error occurred adding the cloud account {data.type} {error}")
        return format_error_response(error)


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=OptScaleOrganization,
    dependencies=[Depends(JWTBearer())],
)
async def create_orgs(
    data: CreateOrgData,
    auth_client: Annotated[OptScaleAuth, Depends(get_auth_client)],
    org_api: Annotated[OptScaleOrgAPI, Depends()],
):
    """
    Create a new FinOPs organization.

    :param data: The input data required to create an organization,including the user_id
    :param org_api: An instance of OptScaleOrgAPI for managing organization operations.
                    Dependency injection via `Depends()`.
    :param auth_client: An instance of OptScaleAuth for authentication.
                        Dependency injection via `Depends(get_auth_client)`.

    :return: A response model containing the details of the created organization.
    Example

        {
            "deleted_at": 0,
            "created_at": 1732792923,
            "id": "4c40d5e4-4313-45de-af2a-9fab19e46d3b",
            "name": "Alpha Agency 3 ",
            "pool_id": "42ce59d1-c091-469d-bfae-5ac528c56a26",
            "is_demo": false,
            "currency": "USD",
            "cleaned_at": 0
        }

        This Endpoint, returns a formatted error object like this one, as a result of
        each exception.
        {
            "detail": {
                "type": "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.3",
                "title": "Error response from OptScale",
                "status": 403,
                "traceId": "c4bd62b3fe154456af99380796fb669c",
                "errors": {
                    "reason": "Oh no, I made a mistake!"
                }
            }
        }

    :dependencies:
        JWTBearer: Ensures that the request is authenticated using a valid JWT.

    """

    try:
        # handle_jwt_dependency(jwt_payload)
        response = await org_api.create_user_org(
            org_name=data.org_name,
            user_id=data.user_id,
            currency=data.currency,
            admin_api_key=settings.admin_token,
            auth_client=auth_client,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )

    except Exception as error:
        return format_error_response(error)
