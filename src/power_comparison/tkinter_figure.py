"""Shared code for Tkinter matplotlib figures."""

import customtkinter as ctk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def new_figure(
    frame: ctk.CTkFrame, bg_color: str, fg_color: str
) -> tuple[Figure, FigureCanvasTkAgg]:
    """Return a new configured figure."""
    figure = Figure()
    figure.patch.set_facecolor(bg_color)
    mpl.rcParams["axes.spines.top"] = False
    mpl.rcParams["axes.spines.bottom"] = False
    mpl.rcParams["axes.spines.left"] = False
    mpl.rcParams["axes.spines.right"] = False
    mpl.rcParams["axes.facecolor"] = bg_color
    mpl.rcParams["text.color"] = fg_color
    mpl.rcParams["axes.labelcolor"] = fg_color
    mpl.rcParams["xtick.color"] = fg_color
    mpl.rcParams["ytick.color"] = fg_color
    canvas = FigureCanvasTkAgg(figure, frame)
    return figure, canvas
