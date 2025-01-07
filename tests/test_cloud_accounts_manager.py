import pytest

from app.api.datasources.cloud_accounts.aws import AWSConfigStrategy
from app.api.datasources.cloud_accounts.azure import AzureConfigStrategy
from app.api.datasources.cloud_accounts_manager import (
    CloudStrategyConfiguration,
    CloudStrategyManager,
)
from app.core.exceptions import CloudAccountConfigError, CloudAccountTypeError


def test_aws_valid_conf():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    assert isinstance(aws_strategy, AWSConfigStrategy)


def test_azure_valid_conf():
    azure_config = CloudStrategyConfiguration(
        name="Azure Service",
        provider_type="azure_cnr",
        config={  # noqa: E501
            "client_id": "ABC",
            "tenant": "XYZ",
            "secret": "SuperSecret",
        },
    )
    azure_strategy = azure_config.select_strategy()
    assert isinstance(azure_strategy, AzureConfigStrategy)


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


def test_passing_not_allowed_cloud_type():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="xxxxx",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    with pytest.raises(CloudAccountTypeError):
        aws_config.select_strategy()


def test_create_datasource():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    aws_manager = CloudStrategyManager(strategy=aws_strategy)
    assert isinstance(aws_manager, CloudStrategyManager)
    result = aws_manager.create_datasource(config=aws_config, org_id="ck10-1001001")
    assert result is True


def test_exception_on_cloud_strategy_managert():
    aws_config = CloudStrategyConfiguration(
        name="AWS Service",
        provider_type="aws_cnr",
        config={"access_key_id": "ciao", "secret_access_key": "cckkckdkkdskd"},
    )
    aws_strategy = aws_config.select_strategy()
    aws_manager = CloudStrategyManager(strategy=aws_strategy)
    with pytest.raises(CloudAccountConfigError):
        aws_manager.create_datasource(config=None, org_id="ckckck-1k1k")
