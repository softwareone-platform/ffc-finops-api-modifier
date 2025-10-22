import logging

from app.core.exceptions import CloudAccountNotAllowed
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI

logger = logging.getLogger("__name__")
ALLOWED_PROVIDERS = ["aws_cnr", "gcp_cnr", "azure_cnr", "azure_tenant"]


async def link_cloud_account_to_org(
    cloud_account_data: dict,
    org_id: str,
    user_access_token: str,
):
    """

    :param cloud_account_data: The whole config of the given Cloud Account
        {
          "name":"Test2",
          "type":"azure_tenasssssssssnt",
          "config":{
            "client_id":"cd945f4b-0554-4a16-9a09-96a2f30bc0ef",
            "tenant":"1dc9b339-fadb-432e-86df-423c38a0fcb8",
            "secret":"QOt8Q~r.ZkpDN1p2cFsYTCQFDtbB8pzzm6xxydlA"
          },
          "auto_import": false,
          "process_recommendations": false
        }
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

    if cloud_account_data["type"] not in ALLOWED_PROVIDERS:
        raise CloudAccountNotAllowed()
    optscale_cloud_account_api = OptScaleCloudAccountAPI()
    response = await optscale_cloud_account_api.link_cloud_account_with_org(
        user_access_token=user_access_token,  # noqa: E501
        org_id=org_id,
        conf=cloud_account_data,
    )
    datasource_type = cloud_account_data["type"]

    logger.info(
        f"The Cloud Account {datasource_type} has been added to the org {org_id}"
    )
    return response
