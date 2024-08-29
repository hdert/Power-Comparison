"""A graphical application to interact with your power usage statistics."""
from __future__ import annotations

import asyncio
from tkinter import PhotoImage
from typing import TYPE_CHECKING

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

from power_comparison.plan_comparison_screen import PlanComparisonScreen
from power_comparison.usage_view_screen import UsageViewScreen

if TYPE_CHECKING:
    from power_comparison.controller import Controller


class View:
    """A graphical application to interact with your power usage statistics."""

    _root: ctk.CTk
    _controller: Controller
    _close: bool = False
    _theme: str

    def __init__(self, controller: Controller) -> None:
        """Initialize the App."""
        self._controller = controller
        ctk.set_default_color_theme(controller.get_theme_path())
        self._root = ctk.CTk()
        self._root.minsize(width=1280, height=720)
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        self._root.protocol("WM_DELETE_WINDOW", self.close_view)
        self._root.iconbitmap()
        icon = PhotoImage(file=self.get_controller().get_icon_path())
        self._root.iconphoto(True, icon)
        self._theme = ctk.get_appearance_mode()
        self._theme_text = ctk.StringVar()
        self.launch_login_screen()
        asyncio.get_event_loop().run_until_complete(self.exec(1 / 20))

    def close_view(self) -> None:
        """Close view."""
        self._close = True

    async def exec(self, interval: float) -> None:
        """Execute view."""
        while True:
            if self._close:
                self._root.destroy()
                break
            self._root.update()
            await asyncio.sleep(interval)

    def config_grid(
        self, frame: ctk.CTkFrame, rows: list[int], columns: list[int]
    ) -> None:
        """Configure the amount of rows and columns on the root."""
        for i, weight in enumerate(rows):
            frame.rowconfigure(i, weight=weight)
        for i, weight in enumerate(columns):
            frame.columnconfigure(i, weight=weight)

    def set_title(self, title: str) -> None:
        """Configure the window title."""
        self._root.title(title)

    def clear_screen(self) -> None:
        """Clear the screen."""
        for widget in self._root.winfo_children():
            widget.destroy()

    def new_frame(self) -> ctk.CTkFrame:
        """Return a new frame.

        This returns a new 'root'-like frame for a new window.
        It also clears the screen, and configures this frame to have
        one row and column.
        """
        self.clear_screen()
        frame = ctk.CTkFrame(self._root)
        frame.grid(row=0, column=0, sticky="NEWS")
        self.config_grid(frame, [1], [1])
        return frame

    def set_padding(self, frame: ctk.CTkFrame, padx: int, pady: int) -> None:
        """Set the padding of all children in a frame."""
        for child in frame.winfo_children():
            child.grid(padx=padx, pady=pady)

    def get_controller(self) -> Controller:
        """Return the controller."""
        return self._controller

    def get_background_color(self) -> str:
        """Return the background color."""
        if self._theme == "Dark":
            return "#262624"
        return "#f5f5ed"

    def get_foreground_color(self) -> str:
        """Return the foreground color."""
        if self._theme == "Dark":
            return "#f5f5ed"
        return "#262624"

    def switch_theme(self) -> None:
        """Change the application theme."""
        if self._theme == "Dark":
            self._theme = "Light"
        else:
            self._theme = "Dark"
        ctk.set_appearance_mode(self._theme)

    def appearance_switch_button(self, frame: ctk.CTkFrame) -> None:
        """Add an appearance switch button to frame."""
        switch_frame = ctk.CTkFrame(frame)
        switch_frame.grid(row=0, column=0, sticky="NE")
        image = ctk.CTkImage(
            light_image=Image.open(
                self.get_controller().get_darkmode_icon_path()
            ),
            dark_image=Image.open(
                self.get_controller().get_lightmode_icon_path()
            ),
        )
        ctk.CTkButton(
            switch_frame,
            width=28,
            height=28,
            image=image,
            text="",
            command=self.switch_theme,
            fg_color=("#363634", "#262624"),
            hover_color=("#464644", "#363634"),
        )
        self.set_padding(switch_frame, 5, 5)

    def launch_login_screen(self) -> None:
        """Launch the login screen."""
        LoginScreen(self)

    def launch_data_download(self) -> None:
        """Launch data download screen."""
        DataDownloadScreen(self)

    def launch_main_screen(self) -> None:
        """Launch main screen."""
        MainScreen(self)

    def launch_usage_view_screen(self) -> None:
        """Launch usage view screen."""
        UsageViewScreen(self)

    def launch_plan_comparison_screen(self) -> None:
        """Launch plan comparison screen."""
        PlanComparisonScreen(self)


class LoginScreen:
    """Define the Login or Registration selection screen."""

    _app: View
    _selected_connector: ctk.CTkOptionMenu
    _username: ctk.StringVar
    _password: ctk.StringVar

    def __init__(self, app: View) -> None:
        """Create LoginScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Login")
        window_root = self._app.new_frame()
        frame = ctk.CTkFrame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1, 1, 1, 1], [1, 2])
        ctk.CTkLabel(frame, text="Power Company:").grid(
            row=0, column=0, sticky="E"
        )
        self._selected_connector = ctk.CTkOptionMenu(
            frame,
            values=self._app.get_controller().get_connector_names(),
        )
        self._selected_connector.grid(row=0, column=1)
        ctk.CTkLabel(frame, text="Username/Email:").grid(
            row=1, column=0, sticky="E"
        )
        self._username = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=self._username).grid(row=1, column=1)
        ctk.CTkLabel(frame, text="Password:").grid(row=2, column=0, sticky="E")
        self._password = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            frame, show="•", textvariable=self._password
        )
        password_entry.grid(row=2, column=1)
        password_entry.bind(
            "<Return>", lambda _: asyncio.create_task(self.next_clicked())
        )
        self._next_button = ctk.CTkButton(
            frame,
            text="Login",
            command=lambda: asyncio.create_task(self.next_clicked()),
        )
        self._next_button.grid(row=3, column=1, sticky="E")
        self._app.set_padding(frame, 5, 5)

        self._app.appearance_switch_button(window_root)

    async def next_clicked(self) -> None:
        """Event handler for the next button being clicked."""
        self._next_button.configure(state="disabled")
        result = await self._app.get_controller().try_connect(
            self._selected_connector.get(),
            self._username.get(),
            self._password.get(),
        )
        if result is not None:
            CTkMessagebox(title=result[0], message=result[1], icon="cancel")
            self._next_button.configure(state="normal")
            return
        self._app.launch_data_download()


class DataDownloadScreen:
    """Define the Data Download screen."""

    _app: View
    _message: ctk.StringVar

    def __init__(self, app: View) -> None:
        """Create DataDownloadScreen."""
        self._app = app
        self.tk_init()
        self._app.get_controller().download_data(
            self._app.launch_main_screen, self.update_message
        )

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Downloading Data")
        window_root = self._app.new_frame()
        frame = ctk.CTkFrame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1], [1])
        self._message = ctk.StringVar()
        self._message.set("Downloading data")
        ctk.CTkLabel(frame, textvariable=self._message).grid(row=0, column=0)
        self._app.set_padding(frame, 5, 5)

    def update_message(self, message: str) -> None:
        """Update message for user feedback on download."""
        self._message.set(message)


class MainScreen:
    """Define the main option selection/dashboard screen."""

    _app: View

    def __init__(self, app: View) -> None:
        """Create MainScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Dashboard")
        window_root = self._app.new_frame()
        frame = ctk.CTkFrame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1, 1], [1, 1])
        ctk.CTkButton(
            frame,
            text="Usage Data",
            command=self._app.launch_usage_view_screen,
        ).grid(row=0, column=0)
        ctk.CTkButton(
            frame,
            text="Plan Comparison",
            command=self._app.launch_plan_comparison_screen,
        ).grid(row=0, column=1)
        ctk.CTkButton(frame, text="Exit", command=self._app.close_view).grid(
            row=1, column=1
        )
        ctk.CTkButton(
            frame, text="Logout", command=self._app.launch_login_screen
        ).grid(row=1, column=0)
        self._app.set_padding(frame, 5, 5)

        self._app.appearance_switch_button(window_root)
