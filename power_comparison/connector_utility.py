"""Define utility functions for Connectors."""

# from io import TextIOWrapper
# from pathlib import Path
# import datetime
# import csv
# from .default_values_utility import DefaultValuesUtility as DVU
# from .config import Config


class ConnectorUtility:
    """Define utility functions for Connectors."""

    # @staticmethod
    # def save_data(
    #     data_file: TextIOWrapper, data: tuple[datetime.datetime, list[float]]
    # ) -> None:
    #     """Save sorted data to data_file."""
    #     data_file.write(str(data[0].date()))
    #     for usage in data[1]:
    #         data_file.write(f", {usage}")
    #     data_file.write("\n")

    # @staticmethod
    # def write_header(file_path: str) -> None:
    #     """Write header to the data file."""
    #     with open(file_path, "w", encoding="utf-8") as usage_file:
    #         header = ["Date"]
    #         header += [f"{i:02}" for i in range(24)]
    #         usage_file.write(", ".join(header) + "\n")

    # @staticmethod
    # def get_start(file_path: str) -> datetime.datetime | None:
    #     """Retrieve the starting datetime from the file at file_path."""
    #     if not Path(file_path).exists():
    #         return None
    #    with open(file_path, "r", encoding="utf-8", newline="") as usage_file:
    #         reader = csv.reader(usage_file, delimiter=",")
    #         start = None
    #         for row in reader:
    #             if len(row) > 0:
    #                 start = row
    #         if start is None:
    #             return None
    #         try:
    #             return datetime.datetime.strptime(
    #                 start[0].strip(), "%Y-%m-%d"
    #             ) + datetime.timedelta(days=1)
    #         except ValueError:
    #             return None

    # @staticmethod
    # def get_file_path(config: Config) -> str:
    #     """Return the default file path for the usage_data file."""
    #     return DVU.get_usage_data_file_path(config.get_username())
