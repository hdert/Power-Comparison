"""Implement Connector for the Contact Energy API."""

import asyncio
from datetime import datetime, timedelta
from typing import Self
import async_timeout
from contact_energy_nz import AuthException, ContactEnergyApi, UsageDatum
from power_comparison.connector import Connector

# from power_comparison.config import Config


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
        """Initialize the ContactEnergyConnector."""
        self = cls()
        self._timeout = timeout
        self._connector = await self._authenticate(username, password)
        self._token = self._connector.token
        await self._connector.account_summary()
        return self

    async def _authenticate(
        self, username: str, password: str
    ) -> ContactEnergyApi:
        """Authenticate with the Contact API."""
        try:
            async with async_timeout.timeout(self._timeout):
                return await ContactEnergyApi.from_credentials(
                    username, password
                )
        except asyncio.TimeoutError as e:
            raise e
        except AuthException as e:
            raise e

    async def retrieve_usage(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[tuple[datetime, list[float]]]:
        """Retrieve usage data from the Connector's API.

        start_date:
            Default value is end_date - 365 days. Inclusive.
        end_date:
            Default value is today. Inclusive."""
        end_date = end_date if end_date else datetime.today()
        start_date = (
            start_date if start_date else end_date - timedelta(days=365)
        )
        data: list[tuple[datetime, list[UsageDatum]]] = []
        valid_data = False
        day = end_date
        while day >= start_date:
            try:
                async with async_timeout.timeout(self._timeout):
                    day_data = await self._connector.get_hourly_usage(day)
                    if day_data is None or len(day_data) == 0:
                        if valid_data:
                            break
                    else:
                        data.append(day_data)
                        valid_data = True
            except asyncio.TimeoutError as e:
                raise e
            day -= timedelta(days=1)
        return [
            (date, [usage_datum.value for usage_datum in usage_datums])
            for date, usage_datums in data
        ]

    @staticmethod
    def get_name() -> str:
        """Return the name of the power utility this connector connects to."""
        return ContactEnergyConnector._UTILITY_NAME
