# """Holds the users's configuration."""

# from configparser import ConfigParser, SectionProxy
# from os import path
# from typing import Self
# from collections.abc import MutableMapping
# from .default_values_utility import DefaultValuesUtility as DVU


# class Config:
#     """Holds the users's configuration."""

#     _config: ConfigParser
#     _config_values: SectionProxy

#     def __init__(self, config: ConfigParser) -> None:
#         self._config = config
#         self._config_values = config["DEFAULT"]

#     @classmethod
#     def _from_filepath(cls, file_path: str) -> Self:
#         """Retrieve a Config from a file."""
#         if not path.exists(file_path):
#             raise FileNotFoundError(
#                 f'File at "{file_path}" does not exist, if you haven\'t \
#                     created one, try copying the example'
#             )
#         config = ConfigParser()
#         config.read(file_path)
#         config_values = config["DEFAULT"]
#         if "email" not in config_values:
#             raise KeyError(f"Email not specified in config file: {file_path}")
#         if "password" not in config_values:
#             raise KeyError(
#                 f"Password not specified in config file: {file_path}"
#             )
#         return cls(config)

#     @classmethod
#     def from_username(cls, username: str) -> Self:
#         """Retrieve a Config from a username."""
#         try:
#             return cls._from_filepath(DVU.get_config_file_path(username))
#         except FileNotFoundError:
#             config = ConfigParser()
#             config.set("DEFAULT", "email", username)
#             return cls(config)

#     # @classmethod
#     # def from_credentials(cls, username: str, password: str) -> Self:
#     #     """Create a Config from credentials."""
#     #     config = ConfigParser()
#     #     config.set("DEFAULT", "email", username)
#     #     config.set("DEFAULT", "password", password)
#     #     return cls(config)

#     def save(self, file_path: str | None = None) -> None:
#         """Write the current configuration to disk."""
#         if file_path is None:
#             file_path = DVU.get_config_file_path(self.get_username())
#         with open(file_path, "w", encoding="utf-8") as config_file:
#             self._config.write(config_file)

#     def _get_config_values(self) -> MutableMapping[str, str]:
#         """Return config_values."""
#         return self._config_values

#     def get_config_value(self, key: str) -> str:
#         """Return config value."""
#         return self._get_config_values()[key]

#     def set_config_value(self, key: str, value: str) -> None:
#         """Set config value."""
#         self._config.set("DEFAULT", key, value)

#     def get_username(self) -> str:
#         """Return username/email."""
#         return self.get_config_value("username")

#     def set_password(self, password: str) -> None:
#         """Set the password."""
#         self.set_config_value("password", password)

#     def get_password(self) -> str:
#         """Return password."""
#         return self.get_config_value("password")

#     # def get_password(self) -> str:
#     #     """Return password."""
#     #     return self.get_config_values()["password"]
