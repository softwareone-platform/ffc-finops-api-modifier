from fastapi import status as http_status

from app.api.datasources.cloud_accounts.aws import AWSConfigStrategy
from app.api.datasources.cloud_accounts.azure import (
    AzureCNRConfigStrategy,
    AzureTenantConfigStrategy,
)
from app.api.datasources.cloud_accounts.cloud_config_strategy import CloudConfigStrategy
from app.core.exceptions import (
    CloudAccountConfigError,
    OptScaleAPIResponseError,
)
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI


class CloudStrategyConfiguration:
    ALLOWED_PROVIDERS = {
        "aws_cnr": AWSConfigStrategy,
        "gcp_cnr": None,
        "azure_cnr": AzureCNRConfigStrategy,
        "azure_tenant": AzureTenantConfigStrategy,
    }

    def __init__(
        self,
        name: str,
        provider_type: str,
        auto_import: bool = False,
        process_recommendations: bool = False,  # noqa: E501
        config: dict = None,
    ):
        self.name = name
        self.type = provider_type
        self.config = config if config else {}
        self.auto_import = auto_import
        self.process_recommendations = process_recommendations

    def select_strategy(self):
        if self.type not in self.ALLOWED_PROVIDERS:
            raise OptScaleAPIResponseError(
                title="Wrong Cloud Account",
                error_code="OE0436",
                reason=f"{self.type} is not supported",
                params=[f"{self.type}"],
                status_code=http_status.HTTP_403_FORBIDDEN,
            )

        strategy_class = self.ALLOWED_PROVIDERS[self.type]
        strategy = strategy_class()
        strategy.validate_config(config=self.config)
        return strategy


class CloudStrategyManager:
    def __init__(self, strategy: CloudConfigStrategy):
        self.strategy = strategy
        self.cloud_account_api = OptScaleCloudAccountAPI()

    async def create_datasource(
        self, config: CloudStrategyConfiguration, org_id: str, user_access_token: str
    ):
        if not isinstance(config, CloudStrategyConfiguration):
            raise CloudAccountConfigError
        datasource_conf = {
            key: value
            for key, value in config.__dict__.items()
            if key in ["name", "type", "config"]
        }  # noqa: E501
        try:
            return await self.strategy.link_cloud_account_to_org(
                config=datasource_conf,
                org_id=org_id,
                user_access_token=user_access_token,
                cloud_account_api=self.cloud_account_api,
            )
        except OptScaleAPIResponseError as exception:
            raise exception
