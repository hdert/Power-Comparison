"""Define the usage view screen."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from customtkinter import StringVar
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)

from power_comparison.tkinter_figure import new_figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.container import BarContainer

    from power_comparison.view import View


class UsageViewScreen:
    """Define the usage view screen."""

    _app: View
    _plot: BarContainer
    _axes: Axes
    _canvas: FigureCanvasTkAgg
    _start_date: StringVar
    _end_date: StringVar

    def __init__(self, app: View) -> None:
        """Create UsageViewScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Usage View")
        window_root = self._app.new_frame()
        self._app.config_grid(window_root, [1], [1, 4])
        frame = ctk.CTkFrame(window_root)
        frame.grid(row=0, column=0)
        self._app.config_grid(frame, [1, 1, 1], [1, 1])
        self._start_date = StringVar(
            value=self._app.get_controller().get_start_date().strftime("%x")
        )
        self._end_date = StringVar(
            value=self._app.get_controller().get_last_date().strftime("%x")
        )
        ctk.CTkLabel(frame, text="Start date:").grid(
            row=0, column=0, sticky="E"
        )
        ctk.CTkLabel(frame, text="End date:").grid(row=1, column=0, sticky="E")
        ctk.CTkEntry(frame, textvariable=self._start_date).grid(
            row=0, column=1
        )
        ctk.CTkEntry(frame, textvariable=self._end_date).grid(row=1, column=1)
        ctk.CTkButton(frame, text="Plot", command=self.update_plot).grid(
            row=2, column=0, columnspan=2
        )
        self._app.set_padding(frame, 5, 5)
        # Graph
        graph_frame = ctk.CTkFrame(window_root)
        graph_frame.grid(row=0, column=1)
        self.draw_plot(graph_frame)
        # Back Button
        back_frame = ctk.CTkFrame(window_root)
        back_frame.grid(row=0, column=0, sticky="NW")
        ctk.CTkButton(
            back_frame, text="Back", command=self._app.launch_main_screen
        ).grid()
        self._app.set_padding(back_frame, 5, 5)

    def update_plot(self) -> None:
        """Update usage data plot."""
        usage_data = self._app.get_controller().get_usage_data(
            self._start_date.get(), self._end_date.get()
        )
        if isinstance(usage_data, tuple):
            CTkMessagebox(
                title=usage_data[0], message=usage_data[1], icon="cancel"
            )
            return
        for count, rect in zip(usage_data, self._plot.patches):
            rect.set_height(count)
        self._axes.relim()
        self._axes.autoscale_view()
        self._canvas.draw()

    def draw_plot(self, frame: ctk.CTkFrame) -> None:
        """Draw usage data plot."""
        figure, self._canvas = new_figure(
            frame,
            self._app.get_background_color(),
            self._app.get_foreground_color(),
        )
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
