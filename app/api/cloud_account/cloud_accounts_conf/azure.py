import logging

from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)

logger = logging.getLogger(__name__)


class AzureCNRConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["subscription_id", "client_id", "tenant", "secret"]


class AzureTenantConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["client_id", "tenant", "secret"]
