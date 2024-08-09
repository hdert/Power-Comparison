"""A graphical application to interact with your power usage statistics."""

import asyncio

# from .view import View
from . import Connectors
from .connector import Connector

from contact_energy_nz import AuthException


class Controller:
    """A class to control the application."""

    _connector: Connector

    def __init__(self) -> None:
        """Initialize the controller."""

    def get_connector_names(self) -> list[str]:
        """Return the names of the connectors."""
        return list(Connectors.get_names().keys())

    def try_connect(
        self, connector_name: str, username: str, password: str
    ) -> bool:
        """Try connecting and authenticating with a connector.

        Return success.
        """
        try:
            self._connector = asyncio.run(
                Connectors.get_names()[connector_name].create(
                    username, password
                )
            )
        except (AuthException, asyncio.TimeoutError):
            return False
        return True