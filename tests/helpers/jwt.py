import time

import jwt

from app import settings
from app.core.auth_jwt_bearer import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER

JWT_SECRET = settings.jwt_secret
SUBJECT = "test"


# Helper function to create tokens
def create_jwt_token(subject: str = SUBJECT, expires_in: int = 3600) -> str:
    """
    Generates a JWT token with the required claims: exp, nbf, iss, aud.

    :param subject: The subject (sub) claim
    :param expires_in: Token validity period in seconds.
    :return: A signed JWT token as a string.
    """
    now = int(time.time())
    expire_time = now + expires_in

    payload = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": expire_time,
    }

    # Encode the token with the specified algorithm and secret
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
