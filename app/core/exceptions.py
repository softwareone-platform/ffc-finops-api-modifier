from __future__ import annotations

import logging

from starlette import status as http_status
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class UserCreationError(Exception):
    """Custom exception for errors during user creation."""

    pass


class UserAccessTokenError(Exception):
    """Custom exception for errors during user access token creation."""

    pass


class UserOrgCreationError(Exception):
    """Custom exception for errors during organization creation."""

    pass


class InvitationDoesNotExist(Exception):
    """Custom exception for validating a user invitation ."""

    pass


class CloudAccountConfigError(Exception):
    pass


class APIResponseError(Exception):
    """
    Attributes:
        status_code (int): The HTTP status code of the API response.
        title (str): A short title describing the error.
        reason (str): A detailed reason explaining the cause of the error.
        error_code (str) : A specific error code as returned from OptScale
    """

    def __init__(
        self,
        status_code: int,
        reason: str,
        error_code: str,
        title: str = None,
        params: list = None,
    ):  # noqa: E501
        if params is None:
            params = []
        self.status_code = status_code
        self.title = title
        self.error = {
            "status_code": status_code,
            "reason": reason,
            "error_code": error_code,
            "params": params,
        }


def format_error_response(error):
    if hasattr(error, "status_code"):
        status_code = error.status_code
    else:
        status_code = http_status.HTTP_403_FORBIDDEN
    if hasattr(error, "error"):
        error_payload = error.error
    else:
        error_payload = str(error)
    return JSONResponse(
        status_code=status_code,
        content={"error": error_payload},
    )


def raise_api_response_exception(response):
    """

    :param response:
    :type response:
    :return:
    :rtype:
    """
    error_payload = response.get("data", {}).get("error", {})
    raise APIResponseError(
        title=error_payload.get("title", "OptScale API ERROR"),
        error_code=error_payload.get("error_code", ""),
        params=error_payload.get("params", []),
        reason=error_payload.get("reason", "No details available"),
        status_code=response.get("status_code", http_status.HTTP_403_FORBIDDEN),
    )
