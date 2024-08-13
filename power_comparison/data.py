"""Define the Data class."""

import sqlite3
from datetime import date, timedelta
from .default_values_utility import DefaultValuesUtility as DVU
from typing import Self


class Data:
    """Hold usage data, and manipulation tools."""

    _username: str | None = None
    _user_id: int | None = None

    def __init__(self) -> None:
        """Initialize the Data object without a user.

        To properly initialize with a user, call initialize_user().
        """
        db_filepath = DVU.get_db_file_path()
        DVU.create_dirs(db_filepath, filepath=True)
        self.connection = sqlite3.connect(db_filepath)
        self.cursor = self.connection.cursor()
        self.initialize_database()

    @classmethod
    def from_username(cls, username: str) -> Self:
        """Initialize a Data object from a username."""
        self = cls()
        self.initialize_user(username)
        return self

    def initialize_user(self, username: str) -> None:
        """Ensure the user `username` is initialized."""
        self._username = username
        result = self.cursor.execute(
            "SELECT user_id FROM user_data WHERE username_email=?",
            (self._username,),
        )
        row = result.fetchone()
        if row is not None:
            self._user_id = row[0]
            return
        self.cursor.execute(
            """INSERT INTO user_data (username_email)
        VALUES(?)""",
            (self._username,),
        )
        result = self.cursor.execute(
            "SELECT user_id FROM user_data WHERE username_email=?",
            (self._username,),
        )
        self._user_id = result.fetchone()[0]
        self.connection.commit()

    def initialize_database(self) -> None:
        """Ensure database is initialized and table and user exist."""
        try:
            result = self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE name='usage_data'"
            )
            if result.fetchone() is not None:
                return
            self.cursor.execute(
                """CREATE TABLE
                user_data(
                user_id INTEGER PRIMARY KEY,
                username_email TEXT
                )"""
            )
            self.cursor.execute(
                """CREATE TABLE
                usage_data(
                    user_id INTEGER NOT NULL,
                    date INTEGER NOT NULL, -- Gregorian Ordinal day
                    day INTEGER NOT NULL, -- 0 index day of week
                    hour INTEGER NOT NULL, -- 0 index hour of day
                    value REAL NOT NULL,
                    PRIMARY KEY (user_id, date, hour),
                    FOREIGN KEY (user_id)
                        REFERENCES user_data (user_id)
                )"""
            )
        finally:
            self.connection.commit()

    def get_last_date(self) -> date | None:
        """Return usage data date, or None."""
        if self._user_id is None:
            raise ValueError("Data: _user_id not set")
        result = self.cursor.execute(
            """SELECT date
            FROM usage_data
            WHERE user_id = ?
            ORDER BY date DESC
            """,
            (self._user_id,),
        )
        row = result.fetchone()
        if row is None:
            return None
        return date.fromordinal(row[0])

    def ingest_data(self, data: list[tuple[date, list[float]]]) -> None:
        """Ingest data."""
        if self._user_id is None:
            raise ValueError("Data: _user_id not set")
        for data_date, values in data:
            data_date_ord = data_date.toordinal()
            day = data_date.weekday()
            self.cursor.executemany(
                """INSERT INTO usage_data VALUES(?, ?, ?, ?, ?)""",
                (
                    (self._user_id, data_date_ord, day, hour, value)
                    for hour, value in enumerate(values)
                ),
            )
        self.connection.commit()

    def get_average_usage(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[list[float]] | None:
        """Get average of usage data for every hour of every weekday.

        start_date:
            Defaults to one year ago. The first date to include.
        end_date:
            Defaults to today. The last date to include."""
        if self._user_id is None:
            raise ValueError("Data: _user_id not set")
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        result = self.cursor.execute(
            """SELECT AVG(value), day, hour
            FROM usage_data
            WHERE user_id = ?
            AND date > ?
            AND date < ?
            GROUP BY day, hour
            ORDER BY day ASC, hour ASC""",
            (self._user_id, start_date.toordinal(), end_date.toordinal()),
        )
        data = result.fetchall()
        if len(data) == 0:
            return None
        if len(data) != 7 * 24:
            print("WARNING: Data not right size.")
        return [
            [row[0] for row in data[i * 24 : (i + 1) * 24]] for i in range(7)
        ]

    def get_usage_per_weekday(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[float] | None:
        """Get average usage data per weekday.

        start_date:
            Defaults to one year ago. The first date to include.
        end_date:
            Defaults to today. The last date to include."""
        if self._user_id is None:
            raise ValueError("Data: _user_id not set")
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        result = self.cursor.execute(
            """SELECT AVG(value), hour
            FROM usage_data
            WHERE user_id = ?
            AND date > ?
            AND date < ?
            GROUP BY hour
            ORDER BY hour ASC""",
            (self._user_id, start_date.toordinal(), end_date.toordinal()),
        )
        data = result.fetchall()
        return [row[0] for row in data]

    def close(self) -> None:
        """Close Data."""
        self.connection.commit()
        self.connection.close()
