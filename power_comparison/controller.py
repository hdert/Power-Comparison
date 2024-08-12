"""A graphical application to interact with your power usage statistics."""

import asyncio

# from .view import View
from collections.abc import Callable
from datetime import date
from contact_energy_nz import AuthException
from . import Connectors, Data
from .connector import Connector


class Controller:
    """A class to control the application."""

    _connector: Connector | None = None
    _data: Data | None = None
    _callback: Callable[[str], None] | None = None

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
        self._data = Data(username)
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

    def close(self) -> None:
        """Close controller."""
        if self._data:
            self._data.close()
