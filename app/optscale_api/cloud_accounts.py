from __future__ import annotations

import logging

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import raise_api_response_exception
from app.optscale_api.auth_api import (
    build_bearer_token_header,
)

logger = logging.getLogger(__name__)
CLOUD_ACCOUNT_ENDPOINT = "/restapi/v2/organizations"


class OptScaleCloudAccountAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def create_cloud_account_datasource(
        self, user_access_token: str, org_id: str, conf: dict[str, str]
    ):
        response = await self.api_client.post(
            endpoint=CLOUD_ACCOUNT_ENDPOINT + f"/{org_id}/cloud_accounts",
            headers=build_bearer_token_header(bearer_token=user_access_token),
            data=conf,
        )
        if response.get("error"):
            logger.error(f"Failed to add a cloud account to the org {org_id}")
            return raise_api_response_exception(response)
        logger.info(f"Cloud Account Successfully linked to the org {org_id} {response}")
        return response
