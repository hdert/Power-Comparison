"""Define the default values utility class."""

import base64
from pathlib import Path


class DefaultValuesUtility:
    """Define utility functions for default values."""

    _PREFIX_DIR = "PowerComparison-UserData/"
    _PROFILES_DIR = "profiles/Christchurch-Apr-2024/"
    _ANALYSIS_FILE_PATH = "data/analysis.csv"
    _USAGE_DATA_FILE_PATH = "data/usage_data.csv"
    _CONFIG_FILE_PATH = "config/credentials.env"
    _DB_FILE_PATH = "data/user_data.db"

    @staticmethod
    def create_dirs(dirpath: str) -> None:
        """Ensure all directories in dirpath are created."""
        Path(dirpath).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_profiles_dir() -> str:
        """Return a path to the profiles directory."""
        return DefaultValuesUtility._PROFILES_DIR

    @staticmethod
    def get_db_file_path() -> str:
        """Return a path to the database file."""
        return (
            DefaultValuesUtility._PREFIX_DIR
            + DefaultValuesUtility._DB_FILE_PATH
        )

    @staticmethod
    def get_analysis_file_path(username: str) -> str:
        """Return a path to the analysis file."""
        return (
            DefaultValuesUtility._PREFIX_DIR
            + DefaultValuesUtility._username_to_b64(username)
            + "/"
            + DefaultValuesUtility._ANALYSIS_FILE_PATH
        )

    @staticmethod
    def get_usage_data_file_path(username: str) -> str:
        """Return a path to the usage data file."""
        return (
            DefaultValuesUtility._PREFIX_DIR
            + DefaultValuesUtility._username_to_b64(username)
            + "/"
            + DefaultValuesUtility._USAGE_DATA_FILE_PATH
        )

    @staticmethod
    def get_config_file_path(username: str) -> str:
        """Return a path to the config file."""
        return (
            DefaultValuesUtility._PREFIX_DIR
            + DefaultValuesUtility._username_to_b64(username)
            + "/"
            + DefaultValuesUtility._CONFIG_FILE_PATH
        )

    @staticmethod
    def get_users() -> list[str]:
        """Return a list of all users."""
        return [
            base64.urlsafe_b64decode(str(d)).decode("utf-8")
            for d in Path(DefaultValuesUtility._PREFIX_DIR).iterdir()
            if d.is_dir()
        ]

    @staticmethod
    def _username_to_b64(username: str) -> str:
        """Return the directory name of a user."""
        return base64.urlsafe_b64encode(bytes(username, "utf-8")).decode(
            "utf-8"
        )
