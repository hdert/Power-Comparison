"""A graphical application to interact with your power usage statistics."""

from tkinter import Tk
from tkinter import ttk
import tkinter as tk

from .controller import Controller


class View:
    """A graphical application to interact with your power usage statistics."""

    _root: Tk
    _controller: Controller

    def __init__(self, controller: Controller) -> None:
        """Initialize the App."""
        self._controller = controller
        self._root = Tk()
        self._root.minsize(width=1280, height=720)
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        LoginScreen(self)
        self._root.mainloop()

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
        return ttk.Frame(self._root)

    def set_padding(self, frame: ttk.Frame, padx: int, pady: int) -> None:
        """Set the padding of all children in a frame."""
        for child in frame.winfo_children():
            child.grid(padx=padx, pady=pady)

    def get_controller(self) -> Controller:
        """Return the controller."""
        return self._controller


class LoginScreen:
    """Define the Login or Registration selection screen."""

    _app: View
    _selected_connector: tk.StringVar
    _username: tk.StringVar
    _password: tk.StringVar

    def __init__(self, app: View) -> None:
        self._app = app
        self.tk_init()
        # self._selected_connector = None
        # self._username = None
        # self._password = None

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        frame = self._app.new_frame()
        frame.grid()
        self._app.config_grid(frame, [1, 1, 1, 1], [1, 2])
        self._selected_connector = tk.StringVar()
        ttk.Label(frame, text="Power Company").grid(row=0, column=0)
        ttk.Combobox(
            frame,
            textvariable=self._selected_connector,
            values=self._app.get_controller().get_connector_names(),
        ).grid(row=0, column=1)
        ttk.Label(frame, text="Username/Email").grid(row=1, column=0)
        self._username = tk.StringVar()
        ttk.Entry(frame, textvariable=self._username).grid(row=1, column=1)
        ttk.Label(frame, text="Password").grid(row=2, column=0)
        self._password = tk.StringVar()
        ttk.Entry(frame, show="•", textvariable=self._password).grid(
            row=2, column=1
        )
        ttk.Button(frame, text="Login", command=self._next_clicked).grid(
            row=3, column=1, sticky="E"
        )
        self._app.set_padding(frame, 5, 5)

    def _next_clicked(self) -> None:
        """Event handler for the next button being clicked."""
        if self._app.get_controller().try_connect(
            self._selected_connector.get(),
            self._username.get(),
            self._password.get(),
        ):
            print("Success!")
        else:
            print("Fail!")


class DataViewScreen:
    """Define the Data View screen."""

    _app: View

    def __init__(self, app: View):
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""


if __name__ == "__main__":
    View()
