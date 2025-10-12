import logging
from abc import ABC, abstractmethod

from app.core.exceptions import CloudAccountConfigError

logger = logging.getLogger(__name__)


class CloudConfigStrategy(ABC):  # pragma: no cover
    @abstractmethod
    def required_fields(self) -> list:
        pass

    def validate_config(self, config: dict):
        for field in self.required_fields():
            if field not in config:
                logger.error(f"The {field} is required in the configuration")
                raise CloudAccountConfigError(f"The {field} is required ")

    @abstractmethod
    def link_to_organization(self, config: dict, org_id: str):  # pragma: no cover
        pass
