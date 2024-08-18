"""Define the plan comparison screen."""

from __future__ import annotations

import tkinter as tk
from textwrap import wrap
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from power_comparison.view import View


class PlanComparisonScreen:
    """Define the plan comparison and profile selection screen."""

    _app: View
    _selected_plan_set: ttk.Combobox
    _figure: Figure
    _canvas: FigureCanvasTkAgg
    _start_date: tk.StringVar
    _end_date: tk.StringVar

    def __init__(self, app: View) -> None:
        """Create PlanComparisonScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Plan Comparison")
        window_root = self._app.new_frame()
        self._app.config_grid(window_root, [1], [1, 4])
        frame = ttk.Frame(window_root)
        frame.grid(row=0, column=0)
        self._app.config_grid(frame, [1, 1, 1, 1], [1, 1])
        # Plan Selection
        ttk.Label(frame, text="Select group of plans:").grid(
            row=0, column=0, sticky="E"
        )
        self._selected_plan_set = ttk.Combobox(
            frame, values=self._app.get_controller().get_profile_set_names()
        )
        self._selected_plan_set.grid(row=0, column=1)
        # Date Selection
        self._start_date = tk.StringVar(
            value=self._app.get_controller().get_start_date().strftime("%x")
        )
        self._end_date = tk.StringVar(
            value=self._app.get_controller().get_last_date().strftime("%x")
        )
        ttk.Label(frame, text="Start date:").grid(row=1, column=0, sticky="E")
        ttk.Label(frame, text="End date:").grid(row=2, column=0, sticky="E")
        ttk.Entry(frame, textvariable=self._start_date).grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self._end_date).grid(row=2, column=1)
        ttk.Button(frame, text="Compare", command=self.update_plot).grid(
            row=3, column=0, columnspan=2
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
        """Event handler for compare being clicked."""
        result = self._app.get_controller().get_comparison_data(
            self._selected_plan_set.get(),
            self._start_date.get(),
            self._end_date.get(),
        )
        if isinstance(result, tuple):
            messagebox.showerror(*result)
            return
        self._figure.clear()
        axes = self._figure.add_subplot()
        y_axis = [p[0] for p in result]
        x_axis = [p[1] for p in result]
        axes.set_title(
            f"Comparison of power plans for {self._selected_plan_set.get()}"
        )
        minor_x_ticks = range(0, int(x_axis[-1]), 100)
        major_x_ticks = range(0, int(x_axis[-1]), 200)
        axes.set_xlabel("Estimated cost of plan in a year ($)")
        axes.set_xticks(major_x_ticks)
        axes.tick_params(axis="x", labelrotation=90)
        axes.set_xticks(minor_x_ticks, minor=True)
        axes.grid(visible=True, which="both", axis="x")
        axes.grid(which="minor", alpha=0.3)
        axes.set_ylabel("Power Plan")
        y_axis = ["\n".join(wrap(l, 20)) for l in y_axis]
        axes.set_yticks(range(len(y_axis)), labels=y_axis)
        axes.set_yticklabels(y_axis)
        axes.barh(y_axis, x_axis)
        self._canvas.draw()

    def draw_plot(self, frame: ttk.Frame) -> None:
        """Draw comparison plot."""
        self._figure = Figure(figsize=(8, 6), dpi=100)
        self._canvas = FigureCanvasTkAgg(self._figure, frame)
        self._figure.subplots_adjust(left=0.2)
        self._canvas.get_tk_widget().grid(row=0, column=0)
