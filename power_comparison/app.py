from .view import View
from .controller import Controller
import asyncio


class App:
    def __init__(self) -> None:
        view = asyncio.run(View.create(Controller()))
        view.close()
