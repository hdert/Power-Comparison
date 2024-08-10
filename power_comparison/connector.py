"""Define the abstract class Connector."""

from abc import abstractmethod, ABC
from collections.abc import Callable
from typing import Self
from datetime import date

# from .config import Config


class Connector(ABC):
    """The abstract class for an API Connector."""

    @classmethod
    @abstractmethod
    async def create(
        cls, username: str, password: str, timeout: int = 60
    ) -> Self:
        """Initialize and connect the Connector to its API."""

    @abstractmethod
    async def retrieve_usage(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        callback: Callable[[int], None] | None = None,
    ) -> list[tuple[date, list[float]]]:
        """Retrieve usage data from the Connector's API.

        start_date:
            Default value is end_date - 365 days. Inclusive.
        end_date:
            Default value is today. Inclusive.
        callback:
            Default value is None. Callback accepts date ordinal for user
            feedback while downloading data.
        """

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Return the name of the power utility this connector connects to."""
