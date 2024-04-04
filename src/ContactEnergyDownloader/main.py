"""Get energy usage API data from the Contact Energy API and save as CSV."""

from contact_energy_nz import AuthException, ContactEnergyApi, UsageDatum
from contact_energy_nz.consts import API_BASE_URL
import asyncio, async_timeout
from io import TextIOWrapper
from sys import argv  # TODO
from configparser import ConfigParser
from os import path
import datetime
import csv


def get_configuration(file_path: str = "config/credentials.env") -> ConfigParser:
    """Get a configuration from the filesystem."""
    if not path.exists(file_path):
        raise FileNotFoundError(
            f'File at "{file_path}" does not exist, if you haven\'t created one, try copying the example'
        )
    config = ConfigParser()
    config.read(file_path)
    config_default = config["DEFAULT"]
    if not "token" in config_default:
        if not "email" in config_default:
            raise KeyError(f"email not specified in config file {file_path}")
        if not "password" in config_default:
            raise KeyError(f"password not specified in ")
    return config


def save_configuration(
    config: ConfigParser, file_path: str = "config/credentials.env"
) -> None:
    """Save a config file to the filesystem."""
    with open(file_path, "w") as config_file:
        token = config["DEFAULT"]["token"]
        config.remove_option("DEFAULT", "token")
        config.write(config_file)
        config.set("DEFAULT", "token", token)


async def authenticate(config: ConfigParser, timeout: int = 60) -> ContactEnergyApi:
    """Return the API connector interface.

    May modify config, so save config afterwards
    """
    try:
        async with async_timeout.timeout(timeout):
            connector = await ContactEnergyApi.from_credentials(
                config["DEFAULT"]["email"], config["DEFAULT"]["password"]
            )
    except asyncio.TimeoutError as e:
        raise e
        # return  # TODO
    except AuthException as e:
        raise e
        # return  # TODO
    config.set("DEFAULT", "TOKEN", connector.token)
    if not "account_id" in config["DEFAULT"] or not "contract_id" in config["DEFAULT"]:
        await connector.account_summary()
        config.set("DEFAULT", "account_id", connector.account_id)
        config.set("DEFAULT", "contract_id", connector.contract_id)
        return connector
    connector.account_id = config["DEFAULT"]["account_id"]
    connector.contract_id = config["DEFAULT"]["contract_id"]
    return connector


def get_start(
    connector: ContactEnergyApi,
    file_path: str,
    timeout: int = 60,
    default_start: datetime.datetime = datetime.datetime(
        year=datetime.date.today().year, month=1, day=1
    ),
) -> datetime:
    if path.exists(file_path):
        with open(file_path, "r", newline="") as usage_file:
            reader = csv.reader(usage_file, delimiter=",")
            start = [str(default_start.date())]
            for row in reader:
                if len(row) > 0:
                    start = row
            return datetime.datetime.strptime(
                start[0].strip(), "%Y-%m-%d"
            ) + datetime.timedelta(days=1)
    else:
        return default_start


async def get_usage(
    connector: ContactEnergyApi,
    file_path: str = "data/usage_data.csv",
    timeout: int = 60,
    default_start: datetime.datetime | None = None,
) -> None:
    """Retrieve energy usage from the API."""
    if default_start is not None:
        start = get_start(connector, file_path, timeout, default_start)
    else:
        start = get_start(connector, file_path, timeout)
    end = datetime.datetime.today()
    with open(file_path, "a") as usage_file:
        start_time = start
        while start_time < end:
            try:
                async with async_timeout.timeout(timeout):
                    data = await get_usage_backend(connector, start_time, start_time)
            except asyncio.TimeoutError as e:
                return  # TODO
            save_data(usage_file, data)
            start_time += datetime.timedelta(days=1)


def save_data(data_file: TextIOWrapper, data: [UsageDatum]) -> None:
    """Helper function for get_usage to save data on the fly to the disk."""
    if data is None or len(data) <= 0:
        return
    data_file.write(str(data[0].date.date()))
    for hour in data:
        data_file.write(f", {hour.value}")
    data_file.write("\n")


async def get_usage_backend(
    connector: ContactEnergyApi, start_date: datetime, end_date: datetime
):
    """Query hourly usage stats for given range. Keep to a week max.

    From https://github.com/tkhadimullin/contact-energy-nz/blob/master/contact_energy_nz/contact_energy_api.py
    Parts may be corresponding license.
    """

    formatted_start_date = start_date.strftime("%Y-%m-%d")
    formatted_end_date = end_date.strftime("%Y-%m-%d")

    url = f"{API_BASE_URL}/usage/v2/{connector.contract_id}?ba={connector.account_id}&interval=hourly&from={formatted_start_date}&to={formatted_end_date}"
    # print(url)
    hourly_stats = await connector._try_fetch_data(url, "post")
    # print(hourly_stats)
    if type(hourly_stats) == dict and "message" in hourly_stats.keys():
        print(f"failure: {hourly_stats}")
        print(
            f"connector.token: {connector.token}, connector.account_id: {connector.account_id}, connector.contract_id: {connector.contract_id}"
        )
        print(url)
        return
    return sorted(
        [UsageDatum(item) for item in hourly_stats],
        key=lambda x: x.date,
        reverse=False,
    )


async def main() -> None:
    config = get_configuration()
    connector = await authenticate(config)
    save_configuration(config)
    await get_usage(connector)


if __name__ == "__main__":
    asyncio.run(main())
