"""The main user-facing script to interact with the power comparison suite of tools."""

import contact_energy_downloader
import data_processor
import statistics_generator
import default_values
import asyncio
from os import path
from configparser import ConfigParser
import os
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import datetime
import csv


class App:

    config: str
    connector: contact_energy_downloader.ContactEnergyApi
    root: Tk

    def __init__(self):
        """Program entry point.

        Handles carrying out first time setup and automatic data downloading,
        Then passes control off to a menu that lets the user select what they would like to do.
        """
        self.root = Tk()
        UserNamePasswordLogin(self, self.show_usage_screen)
        self.root.mainloop()

    def get_usage(self, start: datetime.datetime | None):
        asyncio.run(
            contact_energy_downloader.get_usage(
                self.connector, default_values.usage_data_file_path, default_start=start
            )
        )

    def save_config(self):
        contact_energy_downloader.save_configuration(
            self.config, default_values.config_file_path
        )

    def show_usage_screen(self):
        """Show the usage data screen."""
        UsageData(self, self.show_main_screen)

    def show_main_screen(self):
        """Show the main application screen."""
        MainScreen(self)


class UserNamePasswordLogin:

    app: App
    next_screen: callable

    def __init__(self, app: App, next_screen):
        """Perform first time setup for the user.

        This includes creating the relevant directories and files,
        and asking the user for permission to recreate the config
        file if it already exists (it is guaranteed to be
        non-conformant if this function is called).
        """
        self.app = app
        self.next_screen = next_screen
        os.makedirs(path.dirname(default_values.config_file_path), exist_ok=True)
        os.makedirs(path.dirname(default_values.analysis_file_path), exist_ok=True)
        os.makedirs(path.dirname(default_values.usage_data_file_path), exist_ok=True)
        try:
            app.config = contact_energy_downloader.get_configuration(
                default_values.config_file_path
            )
        except (KeyError, FileNotFoundError):
            self.tk_init()
            return
        self.tk_init()
        self.authenticate(from_gui=False)

    def tk_init(self) -> None:
        self.app.root.title("Login")

        mainframe = ttk.Frame(self.app.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.app.root.columnconfigure(0, weight=1)
        self.app.root.rowconfigure(0, weight=1)

        self.username = StringVar()
        ttk.Label(mainframe, text="Email:").grid(column=0, row=0, sticky=W)
        username_entry = ttk.Entry(mainframe, width=15, textvariable=self.username)
        username_entry.grid(column=1, row=0, sticky=E)

        self.password = StringVar()
        ttk.Label(mainframe, text="Password:").grid(column=0, row=1, sticky=W)
        password_entry = ttk.Entry(
            mainframe, width=15, show="*", textvariable=self.password
        )
        password_entry.grid(column=1, row=1, sticky=E)

        ttk.Button(mainframe, text="Login", command=self.authenticate).grid(
            column=1, row=2, sticky=E
        )

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        username_entry.focus()
        self.app.root.bind("<Return>", self.authenticate)
        mainframe.tkraise()

    def authenticate(self, *args, from_gui=True) -> None:
        """Try to authenticate with the contact energy API."""
        if from_gui:
            config = ConfigParser()
            config.set("DEFAULT", "email", self.username.get())
            config.set("DEFAULT", "password", self.password.get())
            self.app.config = config
        try:
            self.app.connector = asyncio.run(
                contact_energy_downloader.authenticate(self.app.config)
            )
        except ValueError:
            messagebox.showerror(
                title="Incorrect credentials",
                message="The email or password you entered was incorrect",
            )
            return
        except asyncio.TimeoutError:
            messagebox.showerror(
                title="Timeout",
                message="Timeout trying to connect to the Contact Energy API",
            )
            raise e
        except contact_energy_downloader.AuthException:
            messagebox.showerror(
                title="Incorrect credentials",
                message="The email or password you entered was incorrect",
            )
            return
        self.app.save_config()
        self.next_screen()


class UsageData:
    app: App
    next_screen: callable

    def __init__(self, app: App, next_screen):
        """Show the usage data retrieval screen."""
        self.app = app
        self.next_screen = next_screen
        if not self.usage_data_file_start_date_exists(
            default_values.usage_data_file_path
        ):
            self.tk_init()
            return
        self.app.get_usage(start=None)
        self.next_screen()

    def usage_data_file_start_date_exists(self, usage_data_file_path: str) -> bool:
        """Returns whether a suitable starting date exists in the usage data file."""
        if not path.exists(usage_data_file_path):
            return False
        with open(usage_data_file_path, "r", newline="") as usage_file:
            reader = csv.reader(usage_file, delimiter=",")
            start = None
            for row in reader:
                if len(row) > 0:
                    start = row
            if start is None:
                return False
            try:
                datetime.datetime.strptime(
                    start[0].strip(), "%Y-%m-%d"
                ) + datetime.timedelta(days=1)
            except ValueError:
                return False
            return True

    def tk_init(self):
        self.app.root.title("Retrieve Usage Data")

        mainframe = ttk.Frame(self.app.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.app.root.columnconfigure(0, weight=1)
        self.app.root.rowconfigure(0, weight=1)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        mainframe.tkraise()


class MainScreen:
    app: App

    def __init__(self, app: App):
        """Show the main screen."""
        self.app = app
        self.tk_init()

    def tk_init(self):
        self.app.root.title("Power Comparison")

        mainframe = ttk.Frame(self.app.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.app.root.columnconfigure(0, weight=1)
        self.app.root.rowconfigure(0, weight=1)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        mainframe.tkraise()


if __name__ == "__main__":
    App()
