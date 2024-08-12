"""App"""

from .view import View
from .controller import Controller
from .data import Data


class App:
    def __init__(self) -> None:
        data = Data()
        controller = Controller(data)
        View(controller)
        data.close()
