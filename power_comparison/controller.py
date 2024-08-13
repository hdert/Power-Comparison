"""A graphical application to interact with your power usage statistics."""

import asyncio

# from .view import View
from collections.abc import Callable
from datetime import date, timedelta
from contact_energy_nz import AuthException
from .connectors import Connectors
from .connector import Connector
from .data import Data

# Temporary
import matplotlib.pyplot as plt


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

    async def try_connect(
        self, connector_name: str, username: str, password: str
    ) -> None | tuple[str, str]:
        """Try connecting and authenticating with a connector.

        Return None, or an error title and message.
        """
        if connector_name == "":
            return (
                "No Power Utility Selected",
                "You haven't selected a power utility to connect to.",
            )
        if connector_name not in Connectors.get_names():
            return (
                "Invalid Power Utility Selected",
                "You haven't selected a valid power utility to connect to.",
            )
        if username.strip() == "":
            return (
                "No username/email",
                "You haven't entered a username/email",
            )
        if password.strip() == "":
            return "No password", "You haven't entered a password."
        try:
            self._connector = await Connectors.get_names()[
                connector_name
            ].create(username, password)
        except (AuthException, asyncio.TimeoutError):
            return (
                "Invalid login",
                "Your username/email and/or your password are incorrect.",
            )
        self._data.initialize_user(username)
        return None

    def download_data(
        self,
        finished_callback: Callable[[], None],
        callback: Callable[[str], None] | None = None,
    ) -> None:
        """Download user data."""
        self._callback = callback
        asyncio.get_event_loop().create_task(
            self.data_download_call(finished_callback)
        )

    async def data_download_call(
        self, finished_callback: Callable[[], None]
    ) -> None:
        """Call and await's connectors retrieve usage."""
        if self._connector is None:
            raise ValueError("Controller._connector not set")
        start_date = self._data.get_last_date()
        if start_date:
            start_date += timedelta(days=1)
        try:
            data = await self._connector.retrieve_usage(
                start_date=start_date,
                callback=self.user_feedback_callback,
            )
        except asyncio.TimeoutError:
            if self._callback:
                self._callback("Error: Downloading date timed out")
        if self._callback is not None:
            self._callback("Saving downloaded data")
        self._data.ingest_data(data)
        finished_callback()

    def user_feedback_callback(self, date_ordinal: int) -> None:
        """Accept a date ordinal to callback stored callback with str."""
        if self._callback is None:
            return
        display_date = date.fromordinal(date_ordinal).strftime("%Y-%m-%d")
        self._callback(f"Retrieving usage data for date: {display_date}")

    def show_data(self) -> None:
        """Show data in matplotlib displays."""
        usage_data = self._data.get_usage_per_weekday()
        if usage_data is None:
            raise ValueError("No usage data found")
        x_axis = [i for i in range(24)]
        axes = plt.subplot()
        axes.set_xticks(x_axis)
        axes.set_title("Average Power Usage Per Hour")
        axes.set_xlabel("Hour of day")
        axes.set_ylabel("Power Usage in KWh")
        axes.grid(True, "both", "y")
        plt.bar(x_axis, usage_data)
        plt.show()
