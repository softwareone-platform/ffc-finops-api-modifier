import logging
from typing import Optional

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
)
from starlette import status as http_status

from app import settings
from app.core.exceptions import (
    AuthException,
)

JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = "HS256"
JWT_AUDIENCE = "modifier"
JWT_ISSUER = "SWO"
JWT_LEEWAY = settings.jwt_leeway

logger = logging.getLogger(__name__)


def decode_jwt(token: str) -> Optional[dict]:  # noqa: UP007
    """
    Decodes a JWT token and validates its critical claims,
    including time-based and issuer/audience claims.


    :param token: The JWT token to decode.
    :return: The decoded token as a dictionary if valid, or `None`
    if the token is invalid or expired.
    :the functions handles the following exceptions:
        ExpiredSignatureError: If the token's signature has expired.
        DecodeError: If the token cannot be decoded due to formatting or cryptographic issues.
        InvalidTokenError: If the token is otherwise invalid.
        Exception: For any general decoding errors.
    """
    try:
        # Decode token and validate critical claims
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "nbf", "iss", "aud"]},
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            leeway=JWT_LEEWAY,
        )
        return decoded_token

    except ExpiredSignatureError:
        logger.error("Expired Signature for the token")
    except DecodeError:
        logger.error("The token cannot be decoded")
    except MissingRequiredClaimError as error:
        logger.error(f"Invalid Token: {error}")
    except InvalidTokenError as error:
        logger.error(f"The token is not valid {error}")
    return None


def verify_jwt(jw_token: str) -> bool:
    """
    Verifies the validity of a JWT token by decoding it and checking its claims.

    :param jw_token: The JWT token to verify.
    :return: `True` if the token is valid and contains
    the expected claims, otherwise `False`.

    """
    is_token_valid = False
    payload = decode_jwt(jw_token)
    if payload is not None:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False, allow_unauthenticated: bool = False):
        """

        :param auto_error: When auto_error=True, HTTPBearer will raise a 403 error
         without reaching any custom logic.
         To allow more granular error messages, set it to False.

        :type auto_error: bool
        """
        super().__init__(auto_error=auto_error)
        self.allow_unauthenticated = allow_unauthenticated

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            # The token is expired or not valid
            if not verify_jwt(credentials.credentials):
                raise AuthException(
                    title="Authentication failed.",
                    reason="The token is invalid or has expired.",
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    params=[],
                    error_code="OE0235",
                )
            return credentials.credentials
        elif self.allow_unauthenticated:
            return None
        else:
            # The authentication schema is not Bearer
            raise AuthException(
                title="Authentication failed.",
                reason="Invalid authorization scheme.",
                status_code=401,
                params=[],
                error_code="",
            )
