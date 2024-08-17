"""Define the Data class."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Self

import numpy as np
import numpy.typing as npt

from power_comparison.default_values_utility import DefaultValuesUtility as DVU


class Data:
    """Hold usage data, and manipulation tools."""

    _username: str | None = None
    _user_id: int | None = None

    def __init__(self) -> None:
        """Initialize the Data object without a user.

        To properly initialize with a user, call initialize_user().
        """
        db_filepath = DVU.get_db_file_path()
        DVU.create_dirs(db_filepath)
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
            msg = "Data: _user_id not set"
            raise ValueError(msg)
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
            msg = "Data: _user_id not set"
            raise ValueError(msg)
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

        Returns:
            None if there is no or not enough data for the user, else returns
            a list (size seven, ordered by day) of lists
            (size 24, ordered by hour) of floats.

        Args:
            start_date:
                Defaults to one year ago. The first date to include.
            end_date:
                Defaults to today. The last date to include.

        Raises:
            ValueError if initialize_user hasn't been called.
        """
        if self._user_id is None:
            msg = "Data: _user_id not set"
            raise ValueError(msg)
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
        if len(data) != 7 * 24:
            return None
        return [
            [row[0] for row in data[i * 24 : (i + 1) * 24]] for i in range(7)
        ]

    def get_usage_per_hour(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[float] | None:
        """Get average usage data per hour.

        Returns None if there is no data for the user, else returns
        a list of 24 floats ordered by hour.
        Throws ValueError if initialize_user hasn't been called.
        start_date:
            Defaults to one year ago. The first date to include.
        end_date:
        Defaults to today. The last date to include.
        """
        if self._user_id is None:
            msg = "Data: _user_id not set"
            raise ValueError(msg)
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
        if len(data) == 0:
            return None
        return [row[0] for row in data]

    def close(self) -> None:
        """Close Data."""
        self.connection.commit()
        self.connection.close()


class Profiles:
    """Hold profile data and tools."""

    def __init__(self) -> None:
        """Initialize a Profiles."""

    def get_profile_set_names(self) -> list[str]:
        """Return a list of names of profile sets."""
        return [
            x.name
            for x in Path(DVU.get_profiles_dir()).iterdir()
            if x.is_dir()
        ]

    def _get_profile_data_numpy(
        self, profile: str
    ) -> list[tuple[str, float, npt.NDArray]] | None:
        """Return a list of plan profiles, or None if profile not valid.

        Returns a profile data list of containing tuples of names,
        daily charges, and numpy arrays of shape (7,24).
        """
        path = Path(DVU.get_profiles_dir()) / profile
        if not path.exists():
            return None
        return [
            (
                data_path.stem,
                float(
                    np.loadtxt(
                        str(data_path),
                        dtype=float,
                        delimiter=",",
                        skiprows=8,
                        usecols=1,
                    )
                ),
                np.loadtxt(
                    str(data_path),
                    dtype=float,
                    delimiter=",",
                    skiprows=1,
                    usecols=range(1, 25),
                    max_rows=7,
                ),
            )
            for data_path in path.iterdir()
            if data_path.is_file()
        ]

    def get_profile_data(
        self, profile: str
    ) -> list[tuple[str, float, list[list[float]]]] | None:
        """Return a list of plan profiles or None if profile not valid.

        A plan profile is a tuple of it's name, daily charge, and
        hour usage-based charges, all monetary values in cents.
        A profile data list is nested list of day, followed by hour.
        A profile data list should be size (7,24).
        """
        data = self._get_profile_data_numpy(profile)
        return (
            data
            if data is None
            else [
                (name, daily_charge, numbers.tolist())
                for name, daily_charge, numbers in data
            ]
        )

    def generate_plan_comparison(
        self, usage: list[list[float]], profile: str
    ) -> list[tuple[str, float]] | None:
        """Returns sorted comparison name and cost for year.

        Returns None if profile is not valid.
        """
        profile_data = self._get_profile_data_numpy(profile)
        if profile_data is None:
            return None
        usage_np = np.array(usage, dtype=float)
        result = [
            (
                name,
                (usage_np * data).sum() * ((365 / 100) / 7)
                + daily_charge * (365 / 100),
            )
            for name, daily_charge, data in profile_data
        ]
        result.sort(key=lambda x: x[1])
        return result
