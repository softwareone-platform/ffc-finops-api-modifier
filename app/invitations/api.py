import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.core.auth_jwt_bearer import JWTBearer
from app.invitations.model import (
    CreateInvitationData,
    CreateInvitationResponse,
    InvitationResponse,
)

logger = logging.getLogger("api.invitations")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=InvitationResponse,
    dependencies=[Depends(JWTBearer())]
)
async def create_invitations(
        data: CreateInvitationData,
):
    """
    Send an invitation email to a new user within an organisation
    """
    return JSONResponse(status_code=201,
                        content={"message": "Invitation has been sent"})

@router.post(
    path="/{id}/accept",
    status_code=http_status.HTTP_201_CREATED,
    response_model=CreateInvitationResponse,
    dependencies=[Depends(JWTBearer())]
)
async def create_invited_user(
        data: CreateInvitationData,
        id: int,  # invitation id
):
    """
    Create the invited user
    """
    return JSONResponse(status_code=201,
                        content={"display_name": "your friendly neighborhood spider-man",
                                 "email": "peter.parker@spider.com",
                                 "org_id": "ABC-1223-ABC-123"})


@router.get(
    path="",
    status_code=http_status.HTTP_200_OK,
    response_model=CreateInvitationData,
    dependencies=[Depends(JWTBearer())]
)
async def get_list_of_invitations(
        data: CreateInvitationData,
):
    """
    Get list of invitations
    """
    return JSONResponse(status_code=200,
                        content=[
                            {
                            "invitation_id" : "1001-10010-1001-1001",
                            "email" : "peter.parker@spiderman.com",
                            "org_id" : "abc-1010-100-10"
                        },
                            {
                                "invitation_id" : "1002-10010-1001-1001",
                                "email" : "bruce.wayne@batman.com",
                                "org_id" : "abc-1010-100-10"
                            },
                        ])