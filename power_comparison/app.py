"""App"""

from view import View
from controller import Controller
from data import Data, Profiles


class App:
    def __init__(self) -> None:
        data = Data()
        profiles = Profiles()
        controller = Controller(data, profiles)
        View(controller)
        data.close()


if __name__ == "__main__":
    App()
