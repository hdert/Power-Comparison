"""Define an Enum of Connectors"""

from enum import Enum
from .connector import Connector
from .contact_energy_connector import ContactEnergyConnector
from .blank import BlankEnergyConnector


class Connectors(Enum):
    """An Enum of Connectors."""

    CONTACT_ENERGY = ContactEnergyConnector
    BLANK_ENERGY = BlankEnergyConnector

    @staticmethod
    def get_names() -> dict[str, Connector]:
        """Return a map of names of connectors with connectors."""
        return {
            connector.value.get_name(): connector.value
            for connector in Connectors
        }
