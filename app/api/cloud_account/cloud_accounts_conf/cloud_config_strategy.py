import logging
from abc import ABC, abstractmethod

from app.core.exceptions import CloudAccountConfigError
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI

logger = logging.getLogger(__name__)


class CloudConfigStrategy(ABC):
    def __init__(self, optscale_cloud_account_api: OptScaleCloudAccountAPI):
        self.optscale_cloud_account_api = optscale_cloud_account_api

    @abstractmethod
    def required_fields(self) -> list:
        pass

    def validate_config(self, config: dict):
        for field in self.required_fields():
            if field not in config:
                logger.error(f"The {field} is required in the configuration")
                raise CloudAccountConfigError(f"The {field} is required ")

    async def link_cloud_account_to_org(
        self,
        config: dict[str, str],
        org_id: str,
        user_access_token: str,
    ):  # noqa: E501
        """
        This method acts as a wrapper for the OptScale API link_cloud_account_with_org method
        :param config: The Cloud Account payload
        :param org_id: The user's ORG to link the Cloud Account with
        :param user_access_token: The user's access token
        :return: The response as it comes from OptScale
        :raise: Rethrow APIResponseError if an error occurred consuming the
        OptScale APIs.
        """
        response = await self.optscale_cloud_account_api.link_cloud_account_with_org(
            user_access_token=user_access_token,  # noqa: E501
            org_id=org_id,
            conf=config,
        )
        cloud_account_type = config.get("type")
        logger.info(
            f"The Cloud Account {cloud_account_type} has been added to the org {org_id}"
        )
        return response
