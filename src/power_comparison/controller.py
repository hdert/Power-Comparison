"""A graphical application to interact with your power usage statistics."""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from power_comparison.connectors import Connectors
from power_comparison.connectors.connector import AuthException
from power_comparison.default_values_utility import DefaultValuesUtility as DVU

if TYPE_CHECKING:
    from collections.abc import Callable

    from power_comparison.connectors.connector import Connector
    from power_comparison.data import Data, Profiles


class Controller:
    """A class to control the application."""

    _connector: Connector | None = None
    _data: Data
    _profiles: Profiles
    _callback: Callable[[str], None] | None = None
    _username: str | None = None

    def __init__(self, data: Data, profiles: Profiles) -> None:
        """Initialize the controller."""
        self._data = data
        self._profiles = profiles

    def get_icon_path(self) -> str:
        """Return the path to the app's icon."""
        return DVU.get_icon_png_path()

    def get_lightmode_icon_path(self) -> str:
        """Return the path to the lightmode icon."""
        return DVU.get_lightmode_icon_path()

    def get_darkmode_icon_path(self) -> str:
        """Return the path to the darkmode icon."""
        return DVU.get_darkmode_icon_path()

    def get_theme_path(self) -> str:
        """Return the path to the theme file."""
        return DVU.get_theme_path()

    def get_connector_names(self) -> list[str]:
        """Return the names of the connectors."""
        return list(Connectors.get_names().keys())

    def get_profile_set_names(self) -> list[str]:
        """Return the names of the power plan profile sets."""
        return self._profiles.get_profile_set_names()

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
        except AuthException:
            return (
                "Invalid login",
                "Your username/email and/or your password are incorrect.",
            )
        except asyncio.TimeoutError:
            return (
                "Timed out",
                "Timed out trying to connect, \
make sure your internet is working.",
            )
        except ValueError:
            return (
                "Error retrieving info",
                "We encountered an error trying to retrieve your information, \
please try again later.",
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
            msg = "Controller._connector not set"
            raise ValueError(msg)
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
                self._callback("Error: Downloading data timed out")
            return
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

    def get_last_date(self) -> date:
        """Return default end date."""
        result = self._data.get_last_date()
        return date.today() if result is None else result

    def get_start_date(self) -> date:
        """Return default start date."""
        last_date = self.get_last_date()
        return (date.today() if last_date is None else last_date) - timedelta(
            days=365
        )

    def get_usage_data(
        self, start_date: str, end_date: str
    ) -> list[float] | tuple[str, str]:
        """Return Usage Data or Error title and message."""
        try:
            start = datetime.strptime(start_date, "%x").date()
            end = datetime.strptime(end_date, "%x").date()
        except ValueError:
            return (
                "Error parsing dates",
                f"Your dates must be in the format: {date.today().strftime('%x')}",
            )
        result = self._data.get_usage_per_hour(start, end)
        if result is None:
            return "No Data", "Error no data was found for this range."
        return result

    def get_comparison_data(
        self, plan_set_name: str, start_date: str, end_date: str
    ) -> list[tuple[str, float]] | tuple[str, str]:
        """Show comparison data in matplotlib display.

        Returns None on success or error messages on failure.
        """
        if plan_set_name == "":
            return (
                "No Profile Set Selected",
                "You haven't selected a set of plans to compare.",
            )
        if plan_set_name not in self._profiles.get_profile_set_names():
            return (
                "Invalid Profile Set Selected",
                "You haven't selected a valid set of plans to compare.",
            )
        try:
            start = datetime.strptime(start_date, "%x").date()
            end = datetime.strptime(end_date, "%x").date()
        except ValueError:
            return (
                "Error parsing dates",
                f"Your dates must be in the format: {date.today().strftime('%x')}",
            )
        usage_data = self._data.get_average_usage(start, end)
        if usage_data is None:
            return "No Data", "Error no data was found for this range."
        data = self._profiles.generate_plan_comparison(
            usage_data, plan_set_name
        )
        if data is None:
            return (
                "Error Fetching Profile Set",
                "We encountered an error fetching this profile set, \
and it is not available for comparison at this time.",
            )
        return data
