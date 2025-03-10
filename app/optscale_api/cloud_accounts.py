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
        self.api_client = APIClient(base_url=settings.opt_scale_rest_api_url)

    async def link_cloud_account_with_org(
        self, user_access_token: str, org_id: str, conf: dict[str, str]
    ):
        """
        This method sends a request to the OptScale API to link the cloud account
        specified in the given conf with the user's org ID

        :param user_access_token: The access token of the user that wants to link
        the cloud account with his org
        :param org_id: The ID of the organization
        :type conf: The dict with the Cloud Account configuration to link
        :return: A dict with the response as it returned from OptScale, like

        {
            "deleted_at": 0,
            "id": "8e8501fa-403a-477b-bd6f-e7569f277f54",
            "created_at": 1736349441,
            "name": "Test2",
            "type": "azure_tenant",
            "config": {
              "client_id": "my_client_id",
              "tenant": "my_tenant_id"
            },
            "organization_id": "my_org_id",
            "auto_import": false,
            "import_period": 1,
            "last_import_at": 0,
            "last_import_modified_at": 0,
            "account_id": "my_account_id",
            "process_recommendations": false,
            "last_import_attempt_at": 0,
            "last_import_attempt_error": null,
            "last_getting_metrics_at": 0,
            "last_getting_metric_attempt_at": 0,
            "last_getting_metric_attempt_error": null,
            "cleaned_at": 0,
            "parent_id": null
          }

        :raise: APIResponseError if an error occurs

        """
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
