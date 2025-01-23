import logging

from app.api.cloud_account.cloud_accounts_manager import (
    CloudStrategyConfiguration,
    CloudStrategyManager,
)

logger = logging.getLogger("__name__")


async def link_cloud_account_to_org(
    name: str,
    type: str,
    config: dict,
    process_recommendations: bool,
    auto_import: bool,
    org_id: str,
    user_access_token: str,
):
    """

    :param name: The name of the Cloud Account
    :param type:  One of the Cloud Account allowed types
    :param config: The whole config of the given Cloud Account
    :param process_recommendations: a value required by OptScale
    :param auto_import: a value required by OptScale
    :param org_id: The org ID to link the Cloud Account to
    :param user_access_token: The user's access token the org belongs to
    :return: If the given cloud account is linked, a dict like this one will be returned
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
          raises:
          Rethrow ValueError if the previously built CloudStrategyConfiguration is tampered.
          Rethrow APIResponseError if an error occurred during the communication with the
          OptScale API.
    """
    # Here the config as received is validated
    cloud_account_config = CloudStrategyConfiguration(
        name=name,
        provider_type=type,
        config=config,
        process_recommendations=process_recommendations,
        auto_import=auto_import,
    )

    # let's select the correct strategy for the given cloud account
    cloud_account_strategy = cloud_account_config.select_strategy()
    strategy_manager = CloudStrategyManager(strategy=cloud_account_strategy)
    # here the conf will be processed in order to use the OptScale API
    response = await strategy_manager.add_cloud_account(
        config=cloud_account_config,
        org_id=org_id,
        user_access_token=user_access_token,
    )
    logger.info(f"The Cloud Account {type} has been linked to the org {org_id}")
    return response
