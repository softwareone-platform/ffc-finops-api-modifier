import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.core.auth_jwt_bearer import JWTBearer
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.organizations.model import CreateOrgData, OrgDataResponse

logger = logging.getLogger("api.organizations")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=OrgDataResponse,
    dependencies=[Depends(JWTBearer())]
)
async def create_orgs(
        data: CreateOrgData,
        org_api: OptScaleOrgAPI = Depends()
):
    """
    Require Admin Authentication Token

    Create a new FinOps for Cloud organization
    """
    return JSONResponse(status_code=201,
                        content={})
