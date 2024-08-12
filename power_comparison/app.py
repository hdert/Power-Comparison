from .view import View
from .controller import Controller


class App:
    def __init__(self) -> None:
        View(Controller())
