"""Define the Data class."""

import sqlite3
from datetime import date
from .default_values_utility import DefaultValuesUtility as DVU


class Data:
    """Hold usage data, and manipulation tools."""

    def __init__(self) -> None:
        """Initialize the Data object."""
        db_filepath = DVU.get_db_file_path()
        DVU.create_dirs(db_filepath)
        self.connection = sqlite3.connect(db_filepath)
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def initialize_database(self) -> None:
        """Ensure database is initialized and table exists."""
        result = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE name='usage_data'"
        )
        if result.fetchone() is not None:
            return
        self.cursor.execute(
            """CREATE TABLE
            user_data(
               user_id NOT NULL PRIMARY KEY,
               username_email TEXT
            )"""
        )
        self.cursor.execute(
            """CREATE TABLE
            usage_data(
                user_id INTEGER NOT NULL,
                date INTEGER NOT NULL,
                day INTEGER NOT NULL,
                hour_0 INTEGER NOT NULL,
                hour_1 INTEGER NOT NULL,
                hour_2 INTEGER NOT NULL,
                hour_3 INTEGER NOT NULL,
                hour_4 INTEGER NOT NULL,
                hour_5 INTEGER NOT NULL,
                hour_6 INTEGER NOT NULL,
                hour_7 INTEGER NOT NULL,
                hour_8 INTEGER NOT NULL,
                hour_9 INTEGER NOT NULL,
                hour_10 INTEGER NOT NULL,
                hour_11 INTEGER NOT NULL,
                hour_12 INTEGER NOT NULL,
                hour_13 INTEGER NOT NULL,
                hour_14 INTEGER NOT NULL,
                hour_15 INTEGER NOT NULL,
                hour_16 INTEGER NOT NULL,
                hour_17 INTEGER NOT NULL,
                hour_18 INTEGER NOT NULL,
                hour_19 INTEGER NOT NULL,
                hour_20 INTEGER NOT NULL,
                hour_21 INTEGER NOT NULL,
                hour_22 INTEGER NOT NULL,
                hour_23 INTEGER NOT NULL,
                PRIMARY KEY (user_id, date),
                FOREIGN KEY (user_id)
                    REFERENCES user_data (user_id)
            )"""
        )
        self.connection.commit()

    def get_last_date(self, username: str) -> date | None:
        """Return usage data date, or None."""
        result = self.cursor.execute(
            """SELECT date
            FROM usage_data
            WHERE username_email = ?
            LEFT JOIN user_data
            ON usage_data.user_id = user_data.user_id
            ORDER BY date DESC
            """,
            username,
        )
        row = result.fetchone()
        if row is None:
            return None
        return date.fromtimestamp(row[0])

    def close(self) -> None:
        """Close Data."""
        self.connection.commit()
        self.connection.close()
