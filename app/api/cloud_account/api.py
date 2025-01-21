import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.api.cloud_account.cloud_accounts_manager import (
    CloudStrategyConfiguration,
    CloudStrategyManager,
)
from app.api.cloud_account.model import AddCloudAccount, AddCloudAccountResponse
from app.api.invitations.api import get_bearer_token
from app.core.exceptions import (
    APIResponseError,
    CloudAccountConfigError,
    format_error_response,
)

logger = logging.getLogger("api.organizations")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=AddCloudAccountResponse,
    response_model_exclude_none=True,
)
async def add_cloud_account(
    data: AddCloudAccount, user_access_token: str = Depends(get_bearer_token)
):
    # Here the config as received is validated
    cloud_account_config = CloudStrategyConfiguration(
        name=data.name,
        provider_type=data.type,
        config=data.config,
        process_recommendations=data.process_recommendations,
        auto_import=data.auto_import,
    )
    try:
        # let's select the correct strategy for the given cloud account
        cloud_account_strategy = cloud_account_config.select_strategy()
        strategy_manager = CloudStrategyManager(strategy=cloud_account_strategy)
        # here the conf will be processed in order to use the OptScale API
        response = await strategy_manager.add_cloud_account(
            config=cloud_account_config,
            org_id=data.org_id,
            user_access_token=user_access_token,
        )

        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )
    except (APIResponseError, CloudAccountConfigError, ValueError) as error:
        logger.error(f"An error occurred adding the cloud account {data.type} {error}")
        return format_error_response(error)
