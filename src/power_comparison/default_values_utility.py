"""Define the default values utility class."""

from pathlib import Path

import platformdirs


class DefaultValuesUtility:
    """Define utility functions for default values."""

    _PROFILES_DIR = "profiles"
    _DB_FILE_PATH = "data/user_data.db"
    _APP_NAME = "Power Comparison"
    _ICON_ICO_PATH = "img/power_compare.ico"
    _ICON_PNG_PATH = "img/power_compare.png"

    @staticmethod
    def create_dirs(filepath: str) -> None:
        """Ensure all directories in filepath are created."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_profiles_dir() -> str:
        """Return a path to the profiles directory."""
        return str(Path(__file__).parent / DefaultValuesUtility._PROFILES_DIR)

    @staticmethod
    def get_icon_ico_path() -> str:
        """Return a path to the program's icon."""
        return str(Path(__file__).parent / DefaultValuesUtility._ICON_ICO_PATH)

    @staticmethod
    def get_icon_png_path() -> str:
        """Return a path to the program's icon."""
        return str(Path(__file__).parent / DefaultValuesUtility._ICON_PNG_PATH)

    @staticmethod
    def get_db_file_path() -> str:
        """Return a path to the database file."""
        return str(
            Path(
                platformdirs.user_data_dir(
                    DefaultValuesUtility._APP_NAME, roaming=True
                )
            )
            / DefaultValuesUtility._DB_FILE_PATH
        )
