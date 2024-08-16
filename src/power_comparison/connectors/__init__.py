"""Define an Enum of Connectors"""

from enum import Enum
from .connector import Connector
from .contact_energy_connector import ContactEnergyConnector


class Connectors(Enum):
    """An Enum of Connectors."""

    CONTACT_ENERGY = ContactEnergyConnector

    @staticmethod
    def get_names() -> dict[str, Connector]:
        """Return a map of names of connectors with connectors."""
        return {
            connector.value.get_name(): connector.value
            for connector in Connectors
        }
