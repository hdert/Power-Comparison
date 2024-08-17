"""App."""

from power_comparison.controller import Controller
from power_comparison.data import Data, Profiles
from power_comparison.view import View


class App:
    """App."""

    def __init__(self) -> None:
        """Initialize App."""
        data = Data()
        profiles = Profiles()
        controller = Controller(data, profiles)
        View(controller)
        data.close()


def main() -> None:
    """Entry point for application."""
    App()


if __name__ == "__main__":
    main()
