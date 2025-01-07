import logging

from app.api.datasources.cloud_accounts.cloud_config_strategy import CloudConfigStrategy

logger = logging.getLogger(__name__)


class AzureConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["client_id", "tenant", "secret"]

    def link_to_organization(self, config: dict, org_id: str):
        logger.info(f"This will link the {config} to the org {org_id}")
