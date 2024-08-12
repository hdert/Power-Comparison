"""A graphical application to interact with your power usage statistics."""

import asyncio

# from .view import View
from collections.abc import Callable
from datetime import date
from contact_energy_nz import AuthException
from .connectors import Connectors
from .connector import Connector
from .data import Data


class Controller:
    """A class to control the application."""

    _connector: Connector | None = None
    _data: Data
    _callback: Callable[[str], None] | None = None
    _username: str | None = None

    def __init__(self, data: Data) -> None:
        """Initialize the controller."""
        self._data = data

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
        self._data.initialize_user(username)
        return None

    def download_data(
        self, callback: Callable[[str], None] | None = None
    ) -> bool:
        """Download user data."""
        if self._connector is None:
            return False
        if self._data is None:
            return False
        self._callback = callback
        try:
            data = asyncio.run(
                self._connector.retrieve_usage(
                    start_date=self._data.get_last_date(),
                    callback=self.user_feedback_callback,
                )
            )
        except asyncio.TimeoutError:
            return False
        self._data.ingest_data(data)
        return True

    def user_feedback_callback(self, date_ordinal: int) -> None:
        """Accept a date ordinal to callback stored callback with str."""
        if self._callback is None:
            return
        self._callback(
            "Retrieving usage data for date: {}".format(
                date.fromordinal(date_ordinal).strftime("%x")
            )
        )
