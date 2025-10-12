from app.api.datasources.cloud_accounts.aws import AWSConfigStrategy
from app.api.datasources.cloud_accounts.azure import AzureConfigStrategy
from app.api.datasources.cloud_accounts.cloud_config_strategy import CloudConfigStrategy
from app.core.exceptions import CloudAccountConfigError, CloudAccountTypeError


class CloudStrategyConfiguration:
    ALLOWED_PROVIDERS = {
        "aws_cnr": AWSConfigStrategy,
        "gcp_cnr": None,
        "azure_cnr": AzureConfigStrategy,
    }

    def __init__(self, name: str, provider_type: str, config: dict = None):
        self.name = name
        self.type = provider_type
        self.config = config if config else {}

    def select_strategy(self):
        if self.type not in self.ALLOWED_PROVIDERS:
            raise CloudAccountTypeError(f"{self.type} is not allowed")
        strategy_class = self.ALLOWED_PROVIDERS[self.type]
        strategy = strategy_class()
        strategy.validate_config(config=self.config)
        return strategy


class CloudStrategyManager:
    def __init__(self, strategy: CloudConfigStrategy):
        self.strategy = strategy

    def create_datasource(self, config: CloudStrategyConfiguration, org_id: str):
        try:
            datasource_conf = {
                key: value
                for key, value in config.__dict__.items()
                if key in ["name", "type", "config"]
            }
            return self.strategy.link_to_organization(
                config=datasource_conf, org_id=org_id
            )
        except Exception as error:
            raise CloudAccountConfigError from error
