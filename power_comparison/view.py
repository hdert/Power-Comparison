"""A graphical application to interact with your power usage statistics."""

from tkinter import Tk, messagebox
from tkinter import ttk
from typing import Self
import tkinter as tk
import asyncio

from .controller import Controller


class View:
    """A graphical application to interact with your power usage statistics."""

    _root: Tk
    _controller: Controller

    @classmethod
    async def create(cls, controller: Controller) -> Self:
        """Initialize the App."""
        self = cls()
        self._controller = controller
        self._root = Tk()
        self._root.minsize(width=1280, height=720)
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        await LoginScreen.create(self)
        self._root.mainloop()
        return self

    def config_grid(
        self, frame: ttk.Frame, rows: list[int], columns: list[int]
    ) -> None:
        """Configure the amount of rows and columns on the root."""
        for i, weight in enumerate(rows):
            frame.rowconfigure(i, weight=weight)
        for i, weight in enumerate(columns):
            frame.columnconfigure(i, weight=weight)

    def set_title(self, title: str) -> None:
        """Configure the window title."""
        self._root.title(title)

    def new_frame(self) -> ttk.Frame:
        """Return a new frame."""
        frame = ttk.Frame(self._root)
        frame.grid()
        frame.tkraise()
        return frame

    def set_padding(self, frame: ttk.Frame, padx: int, pady: int) -> None:
        """Set the padding of all children in a frame."""
        for child in frame.winfo_children():
            child.grid(padx=padx, pady=pady)

    def get_controller(self) -> Controller:
        """Return the controller."""
        return self._controller

    async def launch_data_download(self) -> None:
        """Launch data download screen."""
        await DataDownloadScreen.create(self)

    def clear_screen(self) -> None:
        """Clear screen."""
        for child in self._root.winfo_children():
            child.destroy()

    def close(self) -> None:
        self._controller.close()


class LoginScreen:
    """Define the Login or Registration selection screen."""

    _app: View
    _selected_connector: ttk.Combobox
    _username: tk.StringVar
    _password: tk.StringVar

    @classmethod
    async def create(cls, app: View) -> None:
        """Create LoginScreen."""
        self = cls()
        self._app = app
        await self.tk_init()

    async def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Login")
        frame = self._app.new_frame()
        self._app.config_grid(frame, [1, 1, 1, 1], [1, 2])
        ttk.Label(frame, text="Power Company:").grid(
            row=0, column=0, sticky="E"
        )
        self._selected_connector = ttk.Combobox(
            frame,
            values=self._app.get_controller().get_connector_names(),
        )
        self._selected_connector.grid(row=0, column=1)
        ttk.Label(frame, text="Username/Email:").grid(
            row=1, column=0, sticky="E"
        )
        self._username = tk.StringVar()
        ttk.Entry(frame, textvariable=self._username).grid(row=1, column=1)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="E")
        self._password = tk.StringVar()
        ttk.Entry(frame, show="•", textvariable=self._password).grid(
            row=2, column=1
        )
        ttk.Button(
            frame,
            text="Login",
            command=lambda: asyncio.get_event_loop().create_task(
                self._next_clicked()
            ),
        ).grid(row=3, column=1, sticky="E")
        self._app.set_padding(frame, 5, 5)

    async def _next_clicked(self) -> None:
        """Event handler for the next button being clicked."""
        result = await self._app.get_controller().try_connect(
            self._selected_connector.get(),
            self._username.get(),
            self._password.get(),
        )
        if result is not None:
            messagebox.showerror(title=result[0], message=result[1])
            return
        asyncio.create_task(self._app.launch_data_download())


class DataDownloadScreen:
    """Define the Data Download screen."""

    _app: View
    _message: tk.StringVar

    @classmethod
    async def create(cls, app: View) -> None:
        """Create DataDownloadScreen."""
        self = cls()
        self._app = app
        self.tk_init()
        asyncio.create_task(
            self._app.get_controller().download_data(self.update_message)
        )

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Downloading Data")
        self._app.clear_screen()
        frame = self._app.new_frame()
        frame.grid()
        self._app.config_grid(frame, [1], [1])
        self._message = tk.StringVar()
        self._message.set("Downloading data")
        ttk.Label(frame, textvariable=self._message).grid(row=0, column=0)
        self._app.set_padding(frame, 5, 5)

    def update_message(self, message: str) -> None:
        """Update message for user feedback on download."""
        self._message.set(message)


class DataViewScreen:
    """Define the Data View screen."""

    _app: View

    def __init__(self, app: View):
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""


if __name__ == "__main__":
    View(Controller())
