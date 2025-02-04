import logging

from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)

logger = logging.getLogger(__name__)


class AWSConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["access_key_id", "secret_access_key"]
