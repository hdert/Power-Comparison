"""A graphical application to interact with your power usage statistics."""
from __future__ import annotations

import asyncio
import tkinter as tk
from tkinter import Tk, messagebox, ttk
from typing import TYPE_CHECKING

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.container import BarContainer

    from power_comparison.controller import Controller


class View:
    """A graphical application to interact with your power usage statistics."""

    _root: Tk
    _controller: Controller
    _closed: bool = False

    def __init__(self, controller: Controller) -> None:
        """Initialize the App."""
        self._controller = controller
        self._root = Tk()
        self._root.minsize(width=1280, height=720)
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        self._root.protocol("WM_DELETE_WINDOW", self.close_view)
        self.launch_login_screen()
        asyncio.get_event_loop().run_until_complete(self.exec(1 / 20))

    def close_view(self) -> None:
        """Close view."""
        self._root.destroy()
        self._closed = True

    async def exec(self, interval: float) -> None:
        """Execute view."""
        while True:
            if self._closed:
                break
            self._root.update()
            await asyncio.sleep(interval)

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

    def clear_screen(self) -> None:
        """Clear the screen."""
        for widget in self._root.winfo_children():
            widget.destroy()

    def new_frame(self) -> ttk.Frame:
        """Return a new frame."""
        self.clear_screen()
        frame = ttk.Frame(self._root)
        frame.grid(row=0, column=0, sticky="NEWS")
        self.config_grid(frame, [1], [1])
        frame.tkraise()
        return frame

    def set_padding(self, frame: ttk.Frame, padx: int, pady: int) -> None:
        """Set the padding of all children in a frame."""
        for child in frame.winfo_children():
            child.grid(padx=padx, pady=pady)

    def get_controller(self) -> Controller:
        """Return the controller."""
        return self._controller

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
    _selected_connector: ttk.Combobox
    _username: tk.StringVar
    _password: tk.StringVar

    def __init__(self, app: View) -> None:
        """Create LoginScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Login")
        window_root = self._app.new_frame()
        frame = ttk.Frame(window_root)
        frame.grid()
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
        self._next_button = ttk.Button(
            frame,
            text="Login",
            command=lambda: asyncio.create_task(self.next_clicked()),
        )
        self._next_button.grid(row=3, column=1, sticky="E")
        self._app.set_padding(frame, 5, 5)

    async def next_clicked(self) -> None:
        """Event handler for the next button being clicked."""
        self._next_button.config(state="disabled")
        result = await self._app.get_controller().try_connect(
            self._selected_connector.get(),
            self._username.get(),
            self._password.get(),
        )
        if result is not None:
            messagebox.showerror(title=result[0], message=result[1])
            self._next_button.config(state="normal")
            return
        self._app.launch_data_download()


class DataDownloadScreen:
    """Define the Data Download screen."""

    _app: View
    _message: tk.StringVar

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
        frame = ttk.Frame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1], [1])
        self._message = tk.StringVar()
        self._message.set("Downloading data")
        ttk.Label(frame, textvariable=self._message).grid(row=0, column=0)
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
        frame = ttk.Frame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1, 1], [1, 1])
        ttk.Button(
            frame,
            text="Usage Data",
            command=self._app.launch_usage_view_screen,
        ).grid(row=0, column=0)
        ttk.Button(
            frame,
            text="Plan Comparison",
            command=self._app.launch_plan_comparison_screen,
        ).grid(row=0, column=1)
        ttk.Button(frame, text="Exit", command=self._app.close_view).grid(
            row=1, column=1
        )
        ttk.Button(
            frame, text="Logout", command=self._app.launch_login_screen
        ).grid(row=1, column=0)
        self._app.set_padding(frame, 5, 5)


class UsageViewScreen:
    """Define the usage view screen."""

    _app: View
    _plot: BarContainer
    _axes: Axes
    _canvas: FigureCanvasTkAgg
    _start_date: tk.StringVar
    _end_date: tk.StringVar

    def __init__(self, app: View) -> None:
        """Create UsageViewScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Usage View")
        window_root = self._app.new_frame()
        self._app.config_grid(window_root, [1], [1, 4])
        frame = ttk.Frame(window_root)
        frame.grid(row=0, column=0)
        self._app.config_grid(frame, [1, 1, 1], [1, 1])
        self._start_date = tk.StringVar(
            value=self._app.get_controller().get_start_date().strftime("%x")
        )
        self._end_date = tk.StringVar(
            value=self._app.get_controller().get_last_date().strftime("%x")
        )
        ttk.Label(frame, text="Start date:").grid(row=0, column=0, sticky="E")
        ttk.Label(frame, text="End date:").grid(row=1, column=0, sticky="E")
        ttk.Entry(frame, textvariable=self._start_date).grid(row=0, column=1)
        ttk.Entry(frame, textvariable=self._end_date).grid(row=1, column=1)
        ttk.Button(frame, text="Plot", command=self.update_plot).grid(
            row=2, column=0, columnspan=2
        )
        self._app.set_padding(frame, 5, 5)
        # Graph
        graph_frame = ttk.Frame(window_root)
        graph_frame.grid(row=0, column=1)
        self.draw_plot(graph_frame)
        # Back Button
        back_frame = ttk.Frame(window_root)
        back_frame.grid(row=0, column=0, sticky="NW")
        ttk.Button(
            back_frame, text="Back", command=self._app.launch_main_screen
        ).grid()
        self._app.set_padding(back_frame, 5, 5)

    def update_plot(self) -> None:
        """Update usage data plot."""
        usage_data = self._app.get_controller().get_usage_data(
            self._start_date.get(), self._end_date.get()
        )
        if isinstance(usage_data, tuple):
            messagebox.showerror(*usage_data)
            return
        for count, rect in zip(usage_data, self._plot.patches):
            rect.set_height(count)
        self._axes.relim()
        self._axes.autoscale_view()
        self._canvas.draw()

    def draw_plot(self, frame: ttk.Frame) -> None:
        """Draw usage data plot."""
        # figure = Figure(figsize=(6, 4), dpi=100)
        figure = Figure(dpi=100)
        self._canvas = FigureCanvasTkAgg(figure, frame)
        self._axes = figure.add_subplot()
        x_axis = range(24)
        self._axes.set_xticks(x_axis)
        self._axes.set_title("Average Power Usage Per Hour")
        self._axes.set_xlabel("Hour of day")
        self._axes.set_ylabel("Power Usage (KWh)")
        self._axes.grid(visible=True, which="both", axis="y")
        self._plot = self._axes.bar(x_axis, 24 * [0])
        self._canvas.get_tk_widget().grid(row=0, column=0)
        self.update_plot()


class PlanComparisonScreen:
    """Define the plan comparison and profile selection screen."""

    _app: View
    _selected_plan_set: ttk.Combobox

    def __init__(self, app: View) -> None:
        """Create PlanComparisonScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Plan Comparison")
        window_root = self._app.new_frame()
        frame = ttk.Frame(window_root)
        frame.grid()
        self._app.config_grid(frame, [1], [2, 1, 3])
        self._selected_plan_set = ttk.Combobox(
            frame, values=self._app.get_controller().get_profile_set_names()
        )
        self._selected_plan_set.grid(row=0, column=0)
        ttk.Button(frame, text="Compare", command=self.compare_clicked).grid(
            row=0, column=1
        )
        back_frame = ttk.Frame(window_root)
        back_frame.grid(row=0, column=0, sticky="NW")
        ttk.Button(
            back_frame, text="Back", command=self._app.launch_main_screen
        ).grid()
        self._app.set_padding(back_frame, 5, 5)

    def compare_clicked(self) -> None:
        """Event handler for compare being clicked."""
        result = self._app.get_controller().show_comparison_data(
            self._selected_plan_set.get()
        )
        if result is not None:
            messagebox.showerror(title=result[0], message=result[1])
            return
