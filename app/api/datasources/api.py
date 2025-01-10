import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.api.datasources.cloud_accounts_manager import (
    CloudStrategyConfiguration,
    CloudStrategyManager,
)
from app.api.datasources.model import CreateDatasource, DatasourceResponse
from app.api.invitations.api import get_bearer_token
from app.core.exceptions import (
    OptScaleAPIResponseError,
    format_error_response,
)

logger = logging.getLogger("api.organizations")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=DatasourceResponse,
)
async def create_datasource(
    data: CreateDatasource, user_access_token: str = Depends(get_bearer_token)
):
    cloud_account_config = CloudStrategyConfiguration(
        name=data.name,
        provider_type=data.type,
        config=data.config,
        process_recommendations=data.process_recommendations,
        auto_import=data.auto_import,
    )
    try:
        cloud_account_strategy = cloud_account_config.select_strategy()
        strategy_manager = CloudStrategyManager(strategy=cloud_account_strategy)
        response = await strategy_manager.create_datasource(
            config=cloud_account_config,
            org_id=data.org_id,
            user_access_token=user_access_token,
        )

        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )
    except OptScaleAPIResponseError as error:
        logger.error(f"An error occurred adding the cloud account {data.type} {error}")
        return format_error_response(error)
