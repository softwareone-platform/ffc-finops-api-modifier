import logging
from abc import ABC, abstractmethod

from app.core.exceptions import (
    CloudAccountConfigError,
    OptScaleAPIResponseError,
)
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI

logger = logging.getLogger(__name__)


class CloudConfigStrategy(ABC):
    @abstractmethod
    def required_fields(self) -> list:
        pass

    def validate_config(self, config: dict):
        for field in self.required_fields():
            if field not in config:
                logger.error(f"The {field} is required in the configuration")
                raise CloudAccountConfigError(f"The {field} is required ")

    @staticmethod
    async def link_cloud_account_to_org(
        config: dict,
        org_id: str,
        user_access_token: str,
        cloud_account_api: OptScaleCloudAccountAPI,
    ):  # noqa: E501
        try:
            response = await cloud_account_api.create_cloud_account_datasource(
                user_access_token=user_access_token,  # noqa: E501
                org_id=org_id,
                conf=config,
            )
            return response

        except OptScaleAPIResponseError as exception:
            raise exception
