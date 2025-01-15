from unittest.mock import AsyncMock

import pytest

from app.api.cloud_account.cloud_accounts_conf.aws import AWSConfigStrategy
from app.api.cloud_account.cloud_accounts_conf.azure import (
    AzureCNRConfigStrategy,
    AzureTenantConfigStrategy,
)
from app.api.cloud_account.cloud_accounts_conf.cloud_config_strategy import (
    CloudConfigStrategy,
)
from app.api.cloud_account.cloud_accounts_conf.gcp import GCPCNRConfigStrategy
from app.api.cloud_account.cloud_accounts_manager import (
    CloudStrategyConfiguration,
    CloudStrategyManager,
)
from app.core.exceptions import CloudAccountConfigError, OptScaleAPIResponseError
from app.optscale_api.cloud_accounts import OptScaleCloudAccountAPI


class TestCloudConfigStrategy(CloudConfigStrategy):
    def required_fields(self) -> list:
        return ["field1", "field2", "field3"]


@pytest.fixture
def optscale_cloud_strategy_manager_api():
    """Provides a clean instance of CloudConfigStrategy for each test."""
    return CloudStrategyManager(
        strategy=TestCloudConfigStrategy(
            optscale_cloud_account_api=OptScaleCloudAccountAPI()
        )
    )  # noqa: E501


@pytest.fixture
def mock_link_cloud_account_to_org(mocker, optscale_cloud_strategy_manager_api):
    """Mock the `link_cloud_account_to_org` ."""
    mock_post = mocker.patch.object(
        optscale_cloud_strategy_manager_api.strategy,
        "link_cloud_account_to_org",
        new=AsyncMock(),
    )
    return mock_post


def test_aws_valid_conf():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    assert isinstance(aws_strategy, AWSConfigStrategy)
    assert aws_config.auto_import is True
    assert aws_config.process_recommendations is True


def test_azure_tenant_valid_conf():
    azure_config = CloudStrategyConfiguration(
        name="Azure Service",
        provider_type="azure_tenant",
        config={  # noqa: E501
            "client_id": "ABC",
            "tenant": "XYZ",
            "secret": "SuperSecret",
        },
    )
    azure_strategy = azure_config.select_strategy()
    assert isinstance(azure_strategy, AzureTenantConfigStrategy)
    # Test default values for auto_import and process_recommendations
    assert azure_config.auto_import is True
    assert azure_config.process_recommendations is True


def test_azure_cnr_valid_conf():
    azure_config = CloudStrategyConfiguration(
        name="Azure Service",
        provider_type="azure_cnr",
        config={  # noqa: E501
            "subscription_id": "SUB-101",
            "client_id": "ABC",
            "tenant": "XYZ",
            "secret": "SuperSecret",
        },
    )
    azure_strategy = azure_config.select_strategy()
    assert isinstance(azure_strategy, AzureCNRConfigStrategy)
    # Test default values for auto_import and process_recommendations
    assert azure_config.auto_import is True
    assert azure_config.process_recommendations is True


def test_aws_not_valid_conf():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"blabla": "ciao", "boohoo": "cckkckdkkdskd"},
    )
    with pytest.raises(CloudAccountConfigError):
        aws_config.select_strategy()


def test_azure_not_valid_conf():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="azure_cnr",
        config={"blabla": "ciao", "boohoo": "cckkckdkkdskd"},
    )
    with pytest.raises(CloudAccountConfigError):
        aws_config.select_strategy()


def test_gcp_cnr_valid_conf():
    gcp_cnr_conf = CloudStrategyConfiguration(
        name="GCP Service",
        provider_type="gcp_cnr",
        config={
            "credentials": {
                "name": "ciao",
                "type": "aws_cnr",
                "config": {
                    "access_key_id": "dkdkdk",
                    "secret_access_key": "ckckck",
                    "linked": True,
                },
            },
            "billing_data": {
                "dataset_name": "click",
                "table_name": "klick",
                "project_id": "lklklk",
            },
        },
    )

    gcp_cnr_strategy = gcp_cnr_conf.select_strategy()
    assert isinstance(gcp_cnr_strategy, GCPCNRConfigStrategy)
    # Test default values for auto_import and process_recommendations
    assert gcp_cnr_conf.auto_import is True
    assert gcp_cnr_conf.process_recommendations is True


def test_gcp_cnr_valid_conf_set_auto_import_and_process_recommendations():
    gcp_cnr_conf = CloudStrategyConfiguration(
        name="GCP Service",
        provider_type="gcp_cnr",
        auto_import=False,
        process_recommendations=False,
        config={
            "credentials": {
                "name": "ciao",
                "type": "aws_cnr",
                "config": {
                    "access_key_id": "dkdkdk",
                    "secret_access_key": "ckckck",
                    "linked": True,
                },
            },
            "billing_data": {
                "dataset_name": "click",
                "table_name": "klick",
                "project_id": "lklklk",
            },
        },
    )

    gcp_cnr_strategy = gcp_cnr_conf.select_strategy()
    assert isinstance(gcp_cnr_strategy, GCPCNRConfigStrategy)
    # Test default values for auto_import and process_recommendations
    assert gcp_cnr_conf.auto_import is False
    assert gcp_cnr_conf.process_recommendations is False


def test_gcp_cnr_not_valid_conf():
    aws_config = CloudStrategyConfiguration(
        name="GCP Service",
        provider_type="gcp_cnr",
        config={
            "blabla": {
                "name": "ciao",
                "type": "aws_cnr",
                "config": {
                    "access_key_id": "dkdkdk",
                    "secret_access_key": "ckckck",
                    "linked": True,
                },
            },
            "ciao": {
                "dataset_name": "click",
                "table_name": "klick",
                "project_id": "lklklk",
            },
        },
    )
    with pytest.raises(CloudAccountConfigError):
        aws_config.select_strategy()


def test_passing_not_allowed_cloud_type():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="xxxxx",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    with pytest.raises(OptScaleAPIResponseError):
        aws_config.select_strategy()


async def test_strategy_instance():
    aws_config = CloudStrategyConfiguration(
        name="Test",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    aws_manager = CloudStrategyManager(strategy=aws_strategy)

    assert isinstance(aws_manager, CloudStrategyManager)


async def test_create_datasource(
    test_data: dict, mock_link_cloud_account_to_org, optscale_cloud_strategy_manager_api
):
    aws_config = CloudStrategyConfiguration(
        name="Test",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    mocked_response = {
        "data": test_data["cloud_accounts_conf"]["create"]["data"]["azure"]["response"]
    }
    mock_link_cloud_account_to_org.return_value = mocked_response
    response = await optscale_cloud_strategy_manager_api.add_cloud_account(
        config=aws_config, org_id="my_org", user_access_token="good token"
    )
    assert response == mocked_response


async def test_exception_on_cloud_strategy_manager(
    test_data: dict, mock_link_cloud_account_to_org, optscale_cloud_strategy_manager_api
):
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    aws_manager = CloudStrategyManager(strategy=aws_strategy)

    with pytest.raises(CloudAccountConfigError):
        await aws_manager.add_cloud_account(
            config=None, org_id="my_org_id", user_access_token="good token"
        )

    mocked_error_response = {
        "error": {
            "status_code": 400,
            "error_code": "OE0436",
            "reason": "boofoo type is not supported",
            "params": ["boofoo"],
        }
    }
    mock_link_cloud_account_to_org.return_value = mocked_error_response
    with pytest.raises(OptScaleAPIResponseError):
        await aws_manager.add_cloud_account(
            config=aws_config, org_id="my_org_id", user_access_token="good token"
        )


async def test_inject_value_in_valid_conf(
    test_data: dict, mock_link_cloud_account_to_org, optscale_cloud_strategy_manager_api
):
    # valid conf
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )

    # let's modify something
    del aws_config.name
    with pytest.raises(
        ValueError, match="Missing required fields in the Cloud Account Conf: {'name'}"
    ):
        await optscale_cloud_strategy_manager_api.add_cloud_account(
            config=aws_config, org_id="my_org_id", user_access_token="good token"
        )
