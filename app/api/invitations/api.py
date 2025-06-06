import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse

from app import settings
from app.api.invitations.model import DeclineInvitation
from app.api.invitations.services.invitations import (
    remove_user,
)
from app.core.exceptions import (
    APIResponseError,
    format_error_response,
)
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.optscale_api.users_api import OptScaleUserAPI

# HTTPBearer scheme to parse Authorization header
bearer_scheme = HTTPBearer()
logger = logging.getLogger(__name__)
router = APIRouter()


def get_bearer_token(
    auth: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> str:
    return auth.credentials  # Return the raw token


@router.patch(
    path="/users/invites/{invite_id}",
    status_code=http_status.HTTP_200_OK,
)
async def decline_invitation(
    invite_id: str,
    data: DeclineInvitation,
    background_task: BackgroundTasks,
    invitation_api: Annotated[OptScaleInvitationAPI, Depends()],
    org_api: Annotated[OptScaleOrgAPI, Depends()],
    user_api: Annotated[OptScaleUserAPI, Depends()],
    invited_user_token: Annotated[str, Depends(get_bearer_token)],
):
    try:
        user_id = data.user_id
        response = await invitation_api.decline_invitation(
            user_access_token=invited_user_token, invitation_id=invite_id
        )

        background_task.add_task(
            remove_user,
            user_access_token=invited_user_token,
            user_id=user_id,
            invitation_api=invitation_api,
            org_api=org_api,
            user_api=user_api,
            admin_api_key=settings.optscale_cluster_secret,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_200_OK),
            content={"response": "Invitation declined"},
        )
    except APIResponseError as error:
        return format_error_response(error)
