"""A graphical application to interact with your power usage statistics."""

import asyncio

# from .view import View
from . import Connectors
from .connector import Connector
from collections.abc import Callable

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
    ) -> None | tuple[str, str]:
        """Try connecting and authenticating with a connector.

        Return None, or an error title and message.
        """
        if connector_name == "":
            return (
                "No Power Utility Selected.",
                "You haven't selected a power utility to connect to.",
            )
        if username.strip() == "":
            return (
                "No username/email",
                "You haven't entered a username/email",
            )
        if password.strip() == "":
            return "No password", "You haven't entered a password."
        try:
            self._connector = asyncio.run(
                Connectors.get_names()[connector_name].create(
                    username, password
                )
            )
        except (AuthException, asyncio.TimeoutError):
            return (
                "Invalid login",
                "Your username/email and/or your password are incorrect.",
            )
        return None

    def download_data(self, Callable[[str], None]) -> None:
        """Download user data."""
        try:
            # data = self._connector.retrieve_usage()
        except asyncio.TimeoutError:
            pass
