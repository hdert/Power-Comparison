"""Implement Connector for the Contact Energy API."""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from typing import Self

import async_timeout
import contact_energy_nz
from contact_energy_nz import ContactEnergyApi, UsageDatum

from power_comparison.connectors import connector
from power_comparison.connectors.connector import Connector


class ContactEnergyConnector(Connector):
    """Implement Connector for the Contact Energy API."""

    _token: str
    _connector: ContactEnergyApi
    _timeout: int
    _UTILITY_NAME = "Contact Energy"

    @classmethod
    async def create(
        cls, username: str, password: str, timeout: int = 60
    ) -> Self:
        """Initialize the ContactEnergyConnector.

        Raises:
            AuthException:
                username and/or password incorrect.
            ValueError:
                Something else has gone wrong.
        """
        self = cls()
        self._timeout = timeout
        try:
            self._connector = await self._authenticate(username, password)
        except contact_energy_nz.AuthException as e:
            raise connector.AuthException from e
        self._token = self._connector.token
        await self._connector.account_summary()
        return self

    async def _authenticate(
        self, username: str, password: str
    ) -> ContactEnergyApi:
        """Authenticate with the Contact API."""
        async with async_timeout.timeout(self._timeout):
            return await ContactEnergyApi.from_credentials(username, password)

    async def retrieve_usage(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        callback: Callable[[int], None] | None = None,
    ) -> list[tuple[date, list[float]]]:
        """Retrieve usage data from the Connector's API.

        Arguments:
            start_date:
                Default value is end_date - 365 days. Inclusive.
            end_date:
                Default value is today. Inclusive.
            callback:
                Default value is None. Callback accepts date ordinal for user
                feedback while downloading data.

        Throws:
            asyncio.TimeoutError
        """
        end_date = end_date if end_date else date.today()
        start_date = (
            start_date if start_date else end_date - timedelta(days=365)
        )
        data: list[list[UsageDatum]] = []
        valid_data = False
        day = end_date
        while day >= start_date:
            if callback:
                callback(day.toordinal())
            async with async_timeout.timeout(self._timeout):
                day_data = await self._connector.get_hourly_usage(day)
                if day_data is None or len(day_data) == 0:
                    if valid_data:
                        break
                else:
                    data.append(day_data)
                    valid_data = True
            day -= timedelta(days=1)
        return [
            (
                usage_datums[0].date.date(),
                [usage_datum.value for usage_datum in usage_datums],
            )
            for usage_datums in data
        ]

    @staticmethod
    def get_name() -> str:
        """Return the name of the power utility this connector connects to."""
        return ContactEnergyConnector._UTILITY_NAME
