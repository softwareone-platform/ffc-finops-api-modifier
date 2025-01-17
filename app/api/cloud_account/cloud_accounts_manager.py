from __future__ import annotations

import logging

from fastapi import status as http_status

from app.api.cloud_account.cloud_accounts_conf.aws import AWSConfigStrategy
from app.api.cloud_account.cloud_accounts_conf.azure import (
    AzureCNRConfigStrategy,
    AzureTenantConfigStrategy,
)
from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)
from app.api.cloud_account.cloud_accounts_conf.gcp import GCPCNRConfigStrategy
from app.core.exceptions import (
    APIResponseError,
    CloudAccountConfigError,
)
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI

logger = logging.getLogger(__name__)


class CloudStrategyConfiguration:
    ALLOWED_PROVIDERS = {
        "aws_cnr": AWSConfigStrategy,
        "gcp_cnr": GCPCNRConfigStrategy,
        "azure_cnr": AzureCNRConfigStrategy,
        "azure_tenant": AzureTenantConfigStrategy,
    }

    def __init__(
        self,
        name: str,
        provider_type: str,
        auto_import: bool = True,
        process_recommendations: bool = True,  # noqa: E501
        config: dict = None,
    ):
        self.name = name
        self.type = provider_type
        self.config = config if config else {}
        self.auto_import = auto_import
        self.process_recommendations = process_recommendations

    def select_strategy(self):
        """
        This method checks if the Cloud Account type is allowed.
        If it's valid, an instance of the Cloud Account Class's Strategy
        will be created and validated.
        :return:
        :rtype:
        """
        if self.type not in self.ALLOWED_PROVIDERS:
            raise APIResponseError(
                title="Wrong Cloud Account",
                error_code="OE0436",
                reason=f"{self.type} is not supported",
                params=[f"{self.type}"],
                status_code=http_status.HTTP_403_FORBIDDEN,
            )

        strategy_class = self.ALLOWED_PROVIDERS[self.type]
        strategy = strategy_class(optscale_cloud_account_api=OptScaleCloudAccountAPI())
        strategy.validate_config(config=self.config)
        cloud_account_type = self.config.get("type")
        logger.info(f"Cloud Account Conf for {cloud_account_type} has been validated")
        return strategy


async def build_payload_dict(
    config: CloudStrategyConfiguration, required_fields: dict | None = None
):
    """
    This function builds the configuration dict that will be used
    as payload for linking a given Cloud Account with a user organization.
    :param required_fields: Optional. The required fields to be available in order to build
    the conf.
    :param config: An instance of CloudStrategyConfiguration with the fields to process
    :return: two dictionaries. One is the datasource_conf with the expected fields
    {   'auto_import': False,
        'config': {'access_key_id': 'ciao', 'secret_access_key': 'cckkckdkkdskd'}, 'name': 'Test',
        'process_recommendations': False, 'type': 'aws_cnr'}
    The second one is needed to check if there are missing fields. If the missing_fields is
    not empty, it means that one or more of the required fields are missing.

    """
    if required_fields is None:  # pragma: no cover
        required_fields = {
            "name",
            "type",
            "config",
            "auto_import",
            "process_recommendations",
        }
    cloud_account_payload = {
        key: value for key, value in config.__dict__.items() if key in required_fields
    }
    # Ensure all required fields are present
    missing_fields = required_fields - cloud_account_payload.keys()
    return cloud_account_payload, missing_fields


class CloudStrategyManager:
    def __init__(self, strategy: CloudConfigStrategy):
        self.strategy = strategy

    async def add_cloud_account(
        self, config: CloudStrategyConfiguration, org_id: str, user_access_token: str
    ):
        """
        Link the given Cloud Account Configuration with
        the user's organization.

        :param config: An instance of CloudStrategyConfiguration with the chosen Cloud Account
        configuration
        :param org_id: The user's organization ID to be linked with the Cloud Account.
        :param user_access_token: The user's access token
        :return: If the datasource is created, a dict like this one will be returned
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
          raises: ValueError if the previously built CloudStrategyConfiguration is tampered.
          Rethrow APIResponseError if an error occurred during the communication with the
          OptScale API.
        """
        if not isinstance(config, CloudStrategyConfiguration):
            raise CloudAccountConfigError

        cloud_account_payload, missing_fields = await build_payload_dict(config)
        if missing_fields:
            logger.error(
                "Something has been altered in the CloudStrategyConfiguration."
                "There are missing required fields in the Cloud Account Conf: {missing_fields}"
            )  # noqa: E501
            raise ValueError(
                f"Missing required fields in the Cloud Account Conf: {missing_fields}"
            )

        response = await self.strategy.link_cloud_account_to_org(
            config=cloud_account_payload,
            org_id=org_id,
            user_access_token=user_access_token,
        )
        return response
