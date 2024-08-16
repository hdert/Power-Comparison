"""Define the default values utility class."""

from pathlib import Path
import platformdirs


class DefaultValuesUtility:
    """Define utility functions for default values."""

    _PROFILES_DIR = "profiles"
    _DB_FILE_PATH = "data/user_data.db"
    _APP_NAME = "Power Comparison"

    @staticmethod
    def create_dirs(dirpath: str, filepath: bool = False) -> None:
        """Ensure all directories in dirpath are created."""
        if filepath:
            Path(dirpath).parent.mkdir(parents=True, exist_ok=True)
        else:
            Path(dirpath).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_profiles_dir() -> str:
        """Return a path to the profiles directory."""
        return str(Path(__file__).parent / DefaultValuesUtility._PROFILES_DIR)

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
