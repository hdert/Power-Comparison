"""Define the plan comparison screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from customtkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from power_comparison.tkinter_figure import new_figure

if TYPE_CHECKING:
    from power_comparison.view import View


class PlanComparisonScreen:
    """Define the plan comparison and profile selection screen."""

    _app: View
    _selected_plan_set: ctk.CTkOptionMenu
    _legend_frame: ctk.CTkScrollableFrame
    _figure: Figure
    _canvas: FigureCanvasTkAgg
    _start_date: StringVar
    _end_date: StringVar

    def __init__(self, app: View) -> None:
        """Create PlanComparisonScreen."""
        self._app = app
        self.tk_init()

    def tk_init(self) -> None:
        """Initialize Tkinter for this screen."""
        self._app.set_title("Power Comparison: Plan Comparison")
        window_root = self._app.new_frame()
        self._app.config_grid(window_root, [1], [1, 4])
        left_frame = ctk.CTkFrame(window_root)
        left_frame.grid(row=0, column=0, sticky="NEWS")
        self._app.config_grid(left_frame, [1, 2], [1])
        frame = ctk.CTkFrame(left_frame)
        frame.grid(row=0, column=0)
        self._app.config_grid(frame, [1, 1, 1, 1], [1, 1])
        # Plan Selection
        ctk.CTkLabel(frame, text="Select group of plans:").grid(
            row=0, column=0, sticky="E"
        )
        self._selected_plan_set = ctk.CTkOptionMenu(
            frame, values=self._app.get_controller().get_profile_set_names()
        )
        self._selected_plan_set.grid(row=0, column=1)
        # Date Selection
        self._start_date = StringVar(
            value=self._app.get_controller().get_start_date().strftime("%x")
        )
        self._end_date = StringVar(
            value=self._app.get_controller().get_last_date().strftime("%x")
        )
        ctk.CTkLabel(frame, text="Start date:").grid(
            row=1, column=0, sticky="E"
        )
        ctk.CTkLabel(frame, text="End date:").grid(row=2, column=0, sticky="E")
        ctk.CTkEntry(frame, textvariable=self._start_date).grid(
            row=1, column=1
        )
        ctk.CTkEntry(frame, textvariable=self._end_date).grid(row=2, column=1)
        ctk.CTkButton(frame, text="Compare", command=self.update_plot).grid(
            row=3, column=0, columnspan=2
        )
        self._app.set_padding(frame, 5, 5)
        # Graph
        graph_frame = ctk.CTkFrame(window_root)
        graph_frame.grid(row=0, column=1, sticky="NESW")
        self._app.config_grid(graph_frame, [1], [1])
        self.setup_plot(graph_frame)
        # Legend
        self._legend_frame = ctk.CTkScrollableFrame(left_frame)
        self._legend_frame.grid(row=1, column=0, sticky="NESW")
        self._legend_frame.bind_all(
            "<Button-4>",
            lambda _: self._legend_frame._parent_canvas.yview(
                "scroll", -1, "units"
            ),
        )
        self._legend_frame.bind_all(
            "<Button-5>",
            lambda _: self._legend_frame._parent_canvas.yview(
                "scroll", 1, "units"
            ),
        )
        # Back Button
        back_frame = ctk.CTkFrame(window_root)
        back_frame.grid(row=0, column=0, sticky="NW")
        ctk.CTkButton(
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
            CTkMessagebox(title=result[0], message=result[1], icon="cancel")
            return
        self._figure.clear()
        axes = self._figure.add_subplot()
        y_axis = [str(i) for i in range(1, len(result) + 1)]
        x_axis = [p[1] for p in result]
        axes.set_title(
            f"Comparison of power plans for {self._selected_plan_set.get()}"
        )
        minor_x_ticks = range(0, int(x_axis[-1]), 100)
        major_x_ticks = range(0, int(x_axis[-1]), 200)
        axes.set_xlabel("Estimated cost of plan in a year ($)")
        axes.set_xticks(major_x_ticks)
        axes.tick_params(axis="x", labelrotation=45)
        axes.set_xticks(minor_x_ticks, minor=True)
        axes.grid(visible=True, which="both", axis="x")
        axes.grid(which="minor", alpha=0.3)
        axes.set_ylabel("Power Plan")
        axes.yaxis.set_inverted(True)
        axes.set_yticks(range(len(y_axis)), labels=y_axis)
        axes.set_yticklabels(y_axis)
        axes.barh(y_axis, x_axis)
        self._canvas.draw()
        self.update_legend(result)

    def update_legend(self, info: list[tuple[str, float]]) -> None:
        """Update the legend with power plan information.

        Args:
            info: A list of power plan names, and estimated prices.
        """
        for widget in self._legend_frame.winfo_children():
            widget.destroy()
        for i, (name, value) in enumerate(info):
            ctk.CTkLabel(
                self._legend_frame,
                text=f"#{i + 1:<2} {name}",
            ).grid(row=i, column=0, sticky="W")
            ctk.CTkLabel(self._legend_frame, text=f"${value:.2f}").grid(
                row=i, column=1, sticky="E", padx=5
            )

    def setup_plot(self, frame: ctk.CTkFrame) -> None:
        """Setup comparison plot."""
        self._figure, self._canvas = new_figure(
            frame,
            self._app.get_background_color(),
            self._app.get_foreground_color(),
        )
        self._figure.subplots_adjust(left=0.2)
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="NESW")
