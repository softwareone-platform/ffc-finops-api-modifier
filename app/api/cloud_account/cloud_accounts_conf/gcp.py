import logging

from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)

logger = logging.getLogger(__name__)


class GCPCNRConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["credentials", "billing_data"]
