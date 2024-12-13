"""Implement Connector for signing into old accounts."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Self


from power_comparison.connectors.connector import Connector


class BlankEnergyConnector(Connector):
    """Implement Connector for signing into old accounts."""

    _UTILITY_NAME = "Sign into deactivated accounts"

    @classmethod
    async def create(
        cls, username: str, password: str, timeout: int = 60
    ) -> Self:
        """Initialize the blank BlankEnergyConnector."""
        return cls()

    async def retrieve_usage(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        callback: Callable[[int], None] | None = None,
    ) -> list[tuple[date, list[float]]]:
        """Pretend to retrieve usage data.

        Args:
            start_date:
                No default value, doesn't matter.
            end_date:
                No default value, doesn't matter.
            callback:
                Default value is None. Callback accepts date ordinal for user
                feedback while not downloading data.

        Returns:
            An empty list.
        """
        return []

    @staticmethod
    def get_name() -> str:
        """Return the name of the power utility this connector connects to."""
        return BlankEnergyConnector._UTILITY_NAME
