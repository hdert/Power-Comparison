"""Define the default values utility class."""

from pathlib import Path


class DefaultValuesUtility:
    """Define utility functions for default values."""

    _PREFIX_DIR = "PowerComparison-UserData/"
    _PROFILES_DIR = "profiles"
    _DB_FILE_PATH = "data/user_data.db"

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
        return (
            DefaultValuesUtility._PREFIX_DIR
            + DefaultValuesUtility._DB_FILE_PATH
        )
