import logging

from app.api.datasources.cloud_accounts.cloud_config_strategy import (
    CloudConfigStrategy,
)

logger = logging.getLogger(__name__)


class AWSConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["access_key_id", "secret_access_key"]

    def link_to_organization(self, config: dict, org_id: str):
        logger.info(f"This will link the {config} to the org {org_id}")
        return True
